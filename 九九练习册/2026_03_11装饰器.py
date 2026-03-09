'''
今天要学习装饰器啦宝宝~
这个概念在其他语言中大概是没有的，但是在python中，是一个比较常见而且很好用的方法
看看这个，可能开始有一些些难理解，但是不着急，今天没有装饰器的任务~
https://www.runoob.com/python3/python-decorators.html
'''

# 模仿文档写一段想给哥哥说的话吧~

def my_decorator(func):
    def wrapper():
        print("谈九九以前想说的")
        func()
        print("谈九九以后想说的")
    return wrapper

@my_decorator
def say_hello():
    print("想你了九九")

say_hello()