'''
今日任务：
学习 Python __name__，了解原理，https://www.runoob.com/python3/python3-name-main.html
标准库是python自带的库，三方库不是python自带的，需要通过pip install安装
学习 Python time标准库，://www.runoob.com/python3/python3-date-time.html
学习 Python datetime标准库，https://www.runoob.com/python3/python-datetime.html
学习 Python os标准库，https://www.runoob.com/python3/python3-os-file-methods.html
* 可选，学习用ssh登录远程服务器 不知道你的实力，以后学习都会在远程进行

学习完以后，九九做一道小练习吧！
如果不会远程的话，先在本地进行吧~
1.在桌面创建一个名称为"Learing"的文件夹，
2.在文件夹中生成001.txt到099.txt一共99个txt文件
3.以每0.2s的间隔，往生成的文件中写入"我要好好吃饭，分-秒"
'''
import csv
import time
from datetime import datetime, timedelta, date
import os
from pathlib import Path
from time import sleep


def main():
    # #time库
    # #获取当前时间
    # t=time.time()
    # print(t)
    # localtime=time.localtime(t)
    # print(localtime)
    # #获取格式化的时间
    # localtime2=time.asctime(localtime)
    # print(localtime2)
    # # 格式化成Sat Mar 28 22:24:24 2016形式
    # # %a本地简化星期名称
    # # %A 本地完整星期名称
    # # %b本地简化的月份名称
    # # %B本地完整的月份名称
    # # %c本地相应的日期表示和时间表示
    # print(time.strftime("%a %b %d %H:%M:%S %Y", localtime))
    # # 格式化成2016-03-20 11:45:39形式
    # print (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


    # # #datetime库
    # # 获取当前日期和时间
    # now=datetime.now()
    # print(now)
    # #格式化日期和时间
    # formatted_time=now.strftime("%Y-%m-%d %H:%M:%S")
    # print(formatted_time)
    # # 计算 10 天后的时间
    # future_time = now + timedelta(days=10)
    # print("10 天后的时间:", future_time)
    # #计算两个日期之间的天数
    # date1=date(2018,3,22)
    # date2=date(2018,3,2)
    # delte=date1-date2
    # print("两个日期之间的天数差:",delte.days)

    #os
    # 获取当前工作目录
    current_directory = os.getcwd()
    print("当前工作目录:", current_directory)
    # 列出目录内容
    files_and_dirs = os.listdir()
    print("目录内容:", files_and_dirs)
    #创建目录os.mkdir(path)
    #删除目录os.rmdir(path)     删除文件os.remove(path)

    # 获取桌面路径推荐使用pathlib
    # os.mkdir('../../../Users/TanJiayi/Desktop/Learning')
    path=Path.home()
    print(path)
    desktop_path = path / "Desktop"
    print(desktop_path)

    #在桌面创建一个名称为"Learning"的文件夹
    learning_path = desktop_path / "Learning"
    if learning_path.is_dir():
        print(f"删除: {learning_path}")
        os.rmdir(learning_path)
    os.mkdir(str(learning_path))

    #在文件夹中生成001.txt到099.txt一共99个txt文件
    for file in range(1,100):
        file_path = learning_path / f'{file:03d}.txt'
        now=datetime.now()
        content=f"我要好好吃饭,{now}"
        with open(str(file_path), 'w',encoding='utf-8') as f:
            f.write(content)
            sleep(0.2)
if __name__ == "__main__":
    main()
