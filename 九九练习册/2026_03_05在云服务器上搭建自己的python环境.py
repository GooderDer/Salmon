'''
登录云服务器哦~
公网IP地址：124.220.133.5 账户tjy 密码1
复习 cd mkdir touch vi cp top ps chmod sudo等基本命令（只需要基础，不要深入，深入1天搞不定的）
在你自己的家目录下，创建code文件夹，将这个代码仓库git clone进去（中间会遇到一些小问题，看看宝宝解决问题的能力啦）
今天的作业除了这个文件，还有其他地方哦~通过github寻找代码修改的地方
'''



# 一、目录操作
# 查看当前目录
# pwd

# 查看目录内容
# ls
# ls -l
# ls -a

# 进入目录
# cd 目录名
# 例：
# cd /home
# cd ..    返回上一级
# cd ~     回到家目录
# cd -    返回上一次目录

# 创建目录
# mkdir 目录名
# mkdir -p a/b/c 创建多级目录

# 删除目录
# rm -r 目录名




# 二、文件操作
# 创建文件
# touch 文件名
# 例：
# touch test.txt

# 复制文件
# cp 文件1 文件2

# 复制目录
# cp -r 目录1 目录2

# 移动文件 / 重命名
# mv 原文件 新文件
# 例：
# mv a.txt b.txt
# mv file.txt /home/tjy/

# 删除文件
# rm 文件名

# 强制删除
# rm -rf 文件名


# 三、文件查看
# 查看文件内容
# cat 文件名

# 分页查看
# less 文件名

# 查看文件前10行
# head 文件名

# 查看文件后10行
# tail 文件名
#
# 实时查看日志
# tail -f 文件名




# 四、文件编辑
# 打开文件
# vi 文件名
# 常用操作：
# 进入编辑模式i
# 退出编辑模式Esc
# 保存退出:wq
#不保存退出:q!



# 五、权限管理
# 修改权限
# chmod 权限 文件名
# 例：
# chmod 777 test.sh
# chmod 755 script.sh
# 权限说明：
# r = 4  读
# w = 2  写
# x = 1  执行
# 例：
# 777 = rwx rwx rwx
# 755 = rwx r-x r-x
# 644 = rw- r-- r--




# 六、进程管理
# 查看进程
# ps
# ps -ef
# ps aux

# 查找进程
# ps -ef | grep 名字

# 查看系统资源
# top
# 退出：q

# 结束进程
# kill 进程ID

# 强制结束
# kill -9 进程ID




# 七、系统管理
# 管理员权限执行
# sudo 命令
# 例：
# sudo apt update
# sudo apt install git




# 八、网络命令
# 查看IP
# ip addr

# 测试网络
# ping www.baidu.com




# 九、Git常用命令
# 克隆仓库
# git clone 仓库地址

# 查看状态
# git status

# 拉取更新
# git pull

# 提交代码
# git add .
# git commit -m "message"
# git push
