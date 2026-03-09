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

