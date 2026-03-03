import itertools
import math
from collections import defaultdict

import numpy as np
from pymatgen.core import Structure
from pymatgen.core.periodic_table import Element
from pymatgen.analysis.local_env import CrystalNN


# =========================
# 0) 配置：改成你的 CIF 路径
# =========================
CIF_PATH = "../data/cif_raw/2023[Sc][nan]3[ASR]2.cif"

# 平面判据容差角（补充材料：15°）
PLANE_ANGLE_TOL_DEG = 15.0

# SOAP 参数（默认先用这套；不分型就调小 rcut / sigma）
SOAP_RCUT = 5.0
SOAP_NMAX = 8
SOAP_LMAX = 6
SOAP_SIGMA = 0.4

# 是否打印 SOAP 分簇成员（建议先 True）
SOAP_CLUSTER_DEBUG = True


# =========================
# 1) 工具函数：更稳地取占优元素（处理混占/无序）
# =========================
def dominant_element(site):
    sp = site.species
    el = max(sp.keys(), key=lambda e: sp[e])
    return el


# =========================
# 2) 取第一配位层：用 CrystalNN
# =========================
def get_first_coordination_sphere(structure, metal_index, cnn):
    nn_info = cnn.get_nn_info(structure, metal_index)
    neigh_indices = [x["site_index"] for x in nn_info]
    seen = set()
    uniq = []
    for i in neigh_indices:
        if i not in seen:
            seen.add(i)
            uniq.append(i)
    return uniq


# =========================
# 3) 几何：点到平面的投影、角度、平面判断
# =========================
def normalize(v):
    n = np.linalg.norm(v)
    if n < 1e-12:
        return v
    return v / n

def plane_from_3_points(p1, p2, p3):
    v1 = p2 - p1
    v2 = p3 - p1
    n = np.cross(v1, v2)
    if np.linalg.norm(n) < 1e-10:
        return None, None
    n = normalize(n)
    return n, p1

def signed_distance_to_plane(p, n, p0):
    return float(np.dot(p - p0, n))

def project_point_to_plane(p, n, p0):
    d = signed_distance_to_plane(p, n, p0)
    return p - d * n

def angle_deg(a, b, c):
    v1 = a - b
    v2 = c - b
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 < 1e-12 or n2 < 1e-12:
        return 0.0
    cosang = np.dot(v1, v2) / (n1 * n2)
    cosang = max(-1.0, min(1.0, float(cosang)))
    return math.degrees(math.acos(cosang))

def is_on_plane_by_angle(atom_p, plane_pts, n, p0, tol_deg=15.0):
    lp = project_point_to_plane(atom_p, n, p0)
    for li in plane_pts:
        ang = angle_deg(atom_p, li, lp)
        if ang >= tol_deg:
            return False
    return True

def side_label(p, plane_pts, n, p0, tol_deg=15.0):
    if is_on_plane_by_angle(p, plane_pts, n, p0, tol_deg):
        return 0
    d = signed_distance_to_plane(p, n, p0)
    return 1 if d > 0 else -1


# =========================
# 4) Plane-based OMS 判据（补充材料 S5-i）
# =========================
def plane_based_is_open(structure, metal_idx, neigh_idxs, tol_deg=15.0):
    n = len(neigh_idxs)
    if n <= 3:
        return True, f"CN={n} <= 3 => open (SI rule)"

    coords = np.array(structure.cart_coords)
    m_p = coords[int(metal_idx)]
    neigh_ps = {int(i): coords[int(i)] for i in neigh_idxs}
    neigh_idxs = [int(i) for i in neigh_idxs]

    for comb in itertools.combinations(neigh_idxs, 3):
        p1, p2, p3 = neigh_ps[comb[0]], neigh_ps[comb[1]], neigh_ps[comb[2]]
        nvec, p0 = plane_from_3_points(p1, p2, p3)
        if nvec is None:
            continue

        plane_pts = [p1, p2, p3]
        other_neigh = [i for i in neigh_idxs if i not in comb]
        labels_neigh = [side_label(neigh_ps[i], plane_pts, nvec, p0, tol_deg) for i in other_neigh]
        label_m = side_label(m_p, plane_pts, nvec, p0, tol_deg)

        # A：金属+其它原子全在平面
        if label_m == 0 and all(l == 0 for l in labels_neigh):
            return True, f"Plane-based STRICT(A): all on plane using {comb}"

        # B：金属在平面，其他原子全在同一侧（不允许 0）
        if label_m == 0 and len(labels_neigh) > 0:
            if (all(l == 1 for l in labels_neigh) or all(l == -1 for l in labels_neigh)):
                return True, f"Plane-based STRICT(B): metal on plane, others same side using {comb}"

        # C：金属在一侧，其他原子全在另一侧（不允许 0）
        if label_m != 0 and len(labels_neigh) > 0:
            target = -label_m
            if all(l == target for l in labels_neigh):
                return True, f"Plane-based STRICT(C): metal opposite side using {comb}"

    return False, "Plane-based STRICT: no plane combination triggered"


# =========================
# 5) τ 指标（补充材料 S5-ii）
# =========================
def all_LML_angles_deg(structure, metal_idx, neigh_idxs):
    coords = np.array(structure.cart_coords)
    m = coords[int(metal_idx)]
    angles = []
    for i, j in itertools.combinations([int(x) for x in neigh_idxs], 2):
        li = coords[i]
        lj = coords[j]
        angles.append(angle_deg(li, m, lj))
    angles.sort(reverse=True)
    return angles

def tau4(structure, metal_idx, neigh_idxs):
    angs = all_LML_angles_deg(structure, metal_idx, neigh_idxs)
    if len(angs) < 2:
        return None
    alpha, beta = angs[0], angs[1]
    return (360.0 - (alpha + beta)) / 141.0

def tau5(structure, metal_idx, neigh_idxs):
    angs = all_LML_angles_deg(structure, metal_idx, neigh_idxs)
    if len(angs) < 2:
        return None
    beta, alpha = angs[0], angs[1]
    return (beta - alpha) / 60.0


# =========================
# 6) Method C：SOAP 分簇（同结构内同金属分型）
# =========================
def soap_cluster_types(structure, metal_sites, metal_elems,
                       rcut=5.0, nmax=8, lmax=6, sigma=0.4,
                       debug=False):
    """
    返回：
      labels: dict[site_idx] = cluster_id (0/1)
      info:   dict[site_idx] = 解释字符串

    说明：
      - 对每种金属元素分别做聚类
      - ne>=4：强制分两簇（常见 MOF 两类位点）
      - ne==3：也分两簇，但解释要更谨慎
      - ne<=2：不聚类（全置0）
    """
    from dscribe.descriptors import SOAP
    from sklearn.cluster import AgglomerativeClustering

    ase_atoms = structure.to_ase_atoms()
    species = sorted({dominant_element(s).symbol for s in structure})

    soap = SOAP(
        species=species,
        periodic=True,
        r_cut=rcut,
        n_max=nmax,
        l_max=lmax,
        sigma=sigma,
        sparse=False
    )

    centers = [int(i) for i in metal_sites]
    X = soap.create(ase_atoms, centers=centers)  # (n_metal, dim)

    labels = {}
    info = {}

    # 按元素分组（在 X 中的位置）
    by_elem_pos = defaultdict(list)
    for p, el in enumerate(metal_elems):
        by_elem_pos[el].append(p)

    for el, pos_list in by_elem_pos.items():
        ne = len(pos_list)
        if ne <= 2:
            for p in pos_list:
                idx = centers[p]
                labels[idx] = 0
                info[idx] = f"SOAP-cluster({el}): n={ne}, no clustering"
            continue

        Xe = X[pos_list]

        # 两簇层次聚类（欧氏距离）
        model = AgglomerativeClustering(n_clusters=2, metric="euclidean", linkage="average")
        lab = model.fit_predict(Xe)

        if debug:
            members = defaultdict(list)
            for local_i, p in enumerate(pos_list):
                members[int(lab[local_i])].append(centers[p])
            print(f"[SOAP-CLUSTER] {el} groups:", dict(members))

        for local_i, p in enumerate(pos_list):
            idx = centers[p]
            labels[idx] = int(lab[local_i])
            info[idx] = f"SOAP-cluster({el}): type={int(lab[local_i])}"

    return labels, info


# =========================
# 7) 主流程：Part A + Part B + Part C(分簇) + Part D(融合)
# =========================
def main():
    structure = Structure.from_file(CIF_PATH)

    print("\nPart A: 基于CrystalNN的粗筛")
    print("原子数:", len(structure))
    print("元素种类:", structure.symbol_set)
    print("是否有序:", structure.is_ordered)

    cnn = CrystalNN()

    # 找金属位点
    metal_sites = []
    metal_elems = []
    for i, site in enumerate(structure):
        el = dominant_element(site)
        if Element(el.symbol).is_metal:
            metal_sites.append(i)
            metal_elems.append(el.symbol)

    print(f"金属位点总数: {len(metal_sites)}")

    # 粗筛：CN
    cn_list = []
    neigh_map = {}
    for idx, m in zip(metal_sites, metal_elems):
        try:
            neigh_idxs = get_first_coordination_sphere(structure, idx, cnn)
            cn = len(neigh_idxs)
            neigh_map[idx] = neigh_idxs
        except Exception:
            cn = None
            neigh_map[idx] = []
        cn_list.append(cn)
        print(f"Site {idx:4d} | {m:>2s} | CN = {cn}")

    print("\n可能的 OMS （同元素 CN 偏低）：")
    by_elem = defaultdict(list)
    for idx, m, cn in zip(metal_sites, metal_elems, cn_list):
        if cn is not None:
            by_elem[m].append((idx, cn))

    for m, arr in by_elem.items():
        cns = sorted([cn for _, cn in arr])
        if len(cns) < 3:
            continue
        median = cns[len(cns) // 2]
        thresh = median - 1
        candidates = [(idx, cn) for idx, cn in arr if cn <= thresh]
        if candidates:
            print(f"{m}: median CN={median}, candidates={candidates}")

    # Part B：SI 判据
    print("\nPart B: 基于SI(S5) Plane-based 和 τ 指标的严格筛选")
    si_open = {}
    for idx, m in zip(metal_sites, metal_elems):
        neigh_idxs = neigh_map.get(idx, [])
        cn = len(neigh_idxs)

        is_open, reason = plane_based_is_open(structure, idx, neigh_idxs, PLANE_ANGLE_TOL_DEG)
        si_open[idx] = is_open

        t4 = tau4(structure, idx, neigh_idxs) if cn == 4 else None
        t5 = tau5(structure, idx, neigh_idxs) if cn == 5 else None

        extra = []
        if t4 is not None:
            extra.append(f"tau4={t4:.3f}")
        if t5 is not None:
            extra.append(f"tau5={t5:.3f}")
        extra_str = (" | " + ", ".join(extra)) if extra else ""

        print(f"[SI] Site {idx:4d} | {m:>2s} | CN={cn:2d} | OPEN={is_open} | {reason}{extra_str}")

    # Part C：SOAP 分簇
    print("\nPart C: SOAP 分簇（第三种方法：同金属位点分型）")
    soap_type, soap_type_info = soap_cluster_types(
        structure,
        metal_sites=metal_sites,
        metal_elems=metal_elems,
        rcut=SOAP_RCUT,
        nmax=SOAP_NMAX,
        lmax=SOAP_LMAX,
        sigma=SOAP_SIGMA,
        debug=SOAP_CLUSTER_DEBUG
    )

    for idx, m in zip(metal_sites, metal_elems):
        print(f"[SOAP-TYPE] Site {idx:4d} | {m:>2s} | TYPE={soap_type.get(idx)} | {soap_type_info.get(idx, '')}")

    # Part D：融合（给论文用的最终结论格式）
    print("\nPart D: 融合结论（SI OPEN + SOAP TYPE）")
    # 这里不强行判 OMS，而是输出“OPEN 与 TYPE 的对应关系”
    type_to_sites = defaultdict(list)
    for idx in metal_sites:
        type_to_sites[int(soap_type.get(idx, 0))].append(idx)

    print("[SUMMARY] SOAP types:", dict(type_to_sites))

    for idx, m in zip(metal_sites, metal_elems):
        open_si = bool(si_open.get(idx, False))
        t = soap_type.get(idx, 0)
        conf = "OPEN" if open_si else "CLOSED"
        print(f"[FINAL] Site {idx:4d} | {m:>2s} | SI={conf:6s} | SOAP_TYPE={t}")

    print("\nOK")


if __name__ == "__main__":
    main()