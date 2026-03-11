'''
了解正则表达式是什么 https://www.runoob.com/python/python-reg-expressions.html
所有语言的正则表达式都是相通的，会一个就是都会啦~
以后忘了，看一眼就能想起来的，宝宝是最棒的~
使用Python re模块完成哥哥给的题目
'''


# 题目1：从字符串中提取 所有数字。
# 示例：
text1 = "abc123def45gh6"
# 要求输出：
ret1 = ['123', '45', '6']
# 使用 re.findall()
# 数字正则

# 题目 2 从日志中提取 所有 IP 地址。
# 示例：
text2 = """
connect from 192.168.1.1
connect from 10.0.0.25
connect from 172.16.5.100
"""
# 要求输出：
ret2 = ['192.168.1.1', '10.0.0.25', '172.16.5.100']

import re


# 详细教程https://www.byhy.net/py/lang/extra/regex/
p1=re.compile(r'\d+')
ret1=p1.findall(text1)
print(ret1)

p2=re.compile(r'\d+\.\d+\.\d+\.\d+')
ret2=p2.findall(text2)
print(ret2)


content = '''苹果，苹果是绿色的
橙子，橙子是橙色的
香蕉，香蕉是黄色的'''

# ^ 匹配每行开头
# .* 匹配到第一个逗号之前的所有字符
# () 捕获组只返回匹配的内容
p3 = re.compile(r'^(.*)，', re.MULTILINE)
for one in  p3.findall(content):
    print(one)

content = '''张三，手机号码15945678901
李四，手机号码13945677701
王二，手机号码13845666901'''
# 先整行匹配，再分组需要的内容
p4 = re.compile(r'^(.+)，.+(\d{11})', re.MULTILINE)
for one in  p4.findall(content):
    print(one)