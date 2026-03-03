import os
import csv
from pymatgen.core import Structure
from pymatgen.analysis.local_env import CrystalNN

# ===============================
# 可修改：常见金属理想配位数
# ===============================
IDEAL_CN = {
    "Zn": 4,
    "Cu": 6,
    "Fe": 6,
    "Co": 6,
    "Ni": 6,
    "Mg": 6,
    "Al": 6,
    "Mn": 6,
    "Cr": 6,
    "Zr": 8
}

# ===============================
# 路径设置
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "ASR")
OUTPUT_FILE = os.path.join(BASE_DIR, "oms_result.csv")


def analyze_structure(cif_path):
    """
    分析单个 CIF 文件，返回开放位候选列表
    """
    structure = Structure.from_file(cif_path)
    cnn = CrystalNN()

    open_sites = []

    for i, site in enumerate(structure):
        element = site.specie.symbol

        if element in IDEAL_CN:
            try:
                neighbors = cnn.get_nn_info(structure, i)
                cn = len(neighbors)

                if cn < IDEAL_CN[element]:
                    open_sites.append({
                        "index": i,
                        "element": element,
                        "cn": cn
                    })

            except Exception:
                continue

    return open_sites


def main():
    results = []

    cif_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".cif")]

    print(f"共发现 {len(cif_files)} 个 CIF 文件\n")

    for file in cif_files:
        cif_path = os.path.join(DATA_DIR, file)

        print(f"正在处理: {file}")

        try:
            open_sites = analyze_structure(cif_path)

            for site in open_sites:
                results.append([
                    file,
                    site["index"],
                    site["element"],
                    site["cn"]
                ])

        except Exception as e:
            print(f"处理失败: {file} | 原因: {e}")

    # 写入 CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["cif_file", "atom_index", "element", "coordination_number"])
        writer.writerows(results)

    print("\n分析完成")
    print(f"结果已保存至: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()