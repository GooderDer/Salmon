'''
要求

请你写一个函数：analyze_log~~~
1. 统计每个用户的总消费（只统计 action=pay）
输出格式：
{
    "Tom": 500,
    "Lucy": 120,
    "Jack": 150
}
2. 找出 ERROR 次数最多的用户
输出格式：
("Tom", 1)
3. 输出消费排名前 2 的用户
输出格式：
[("Tom", 500), ("Jack", 150)]

哥哥的要求：必须使用 lambda，代码尽量结构清晰
'''


log_data = """
2026-03-01 10:00:01|INFO|user=Tom|action=login|cost=0
2026-03-01 10:01:10|ERROR|user=Lucy|action=pay|cost=120
2026-03-01 10:02:05|INFO|user=Tom|action=pay|cost=200
2026-03-01 10:03:44|WARNING|user=Jack|action=login|cost=0
2026-03-01 10:05:00|ERROR|user=Tom|action=pay|cost=300
2026-03-01 10:06:12|INFO|user=Lucy|action=logout|cost=0
2026-03-01 10:07:33|ERROR|user=Jack|action=pay|cost=150
"""

dict_log = {}
def analyze_log(log_data):
    logs=log_data.split("\n")
    for data in logs:
        if not data:
            continue
        log=data.split("|")
        state=log[1]
        user=log[2].split("=")[1]
        action=log[3].split("=")[1]
        cost=log[4].split("=")[1]
        if user not in dict_log:
            dict_log[user]=int(cost)
        else:
            dict_log[user]+=int(cost)
    print(dict_log)

print(analyze_log(log_data))























"""
后续~ 做完题目预习一下python的with用法，log_data我放在当前目录的数据下啦~宝贝看看能不能读取到操控它！
"""