# str_first = "tan jiu jiu"
# a = str_first.split(" ")
# for x in a:
#     print(x)

# t = "谈"
# jj = "99"
# tjj = t+jj
# print(tjj)

# 运算符 + * / - **

# 例题1：将test_str去掉所有数字，然后分行打印
# test_str = "你1是1我1的1小1宝1贝，如2果2不2是2的2话，请3你3变3成3我3的3小3宝3贝"

# a=test_str.split("，")
# for i in a:
#     print(i[0::2])

# new_str = test_str.replace("1","").replace("2","").replace("3","")
# print(new_str)

# def sum(a,b):
#     return a+b
#
# print(sum(1,2))
# if "d" in "abc":
#     print("yes")
# else:
#     print("no")

# 变量塞给字符串
# mv = "t99"
# tjj = f"fsadf{mv}"
# print(tjj)

# 例题2：写一个函数，输入为任意长度的字符串，输出 {'字母‘:x，'数字':x,'空格':x,'其他':x}
# a=b=c=d=0
# def count_str(input_str):
#     a=b=c=d=0
#     for x in input_str:
#         if (x >= "a" and x <= "z") or (x >= "A" and x <= "Z"):
#             a=a+1
#         elif x>="0" and x<="9":
#             b=b+1
#         elif x==" ":
#             c=c+1
#         else:
#             d=d+1
#     ret = f"'字母':{a},'数字':{b},'空格':{c},'其他':{d}"
#     return ret
#
# print(count_str("afah fdssdfhsai23532ofewr1324,/234rew."))
#
# for _ in range(10):
#     pass

# # 列表 append
# list=[]
# list.append(1)
# list.append(2)
# list.append(3)
# print(list)
# print(list.count(1))
# list.pop()
# print(list)
# print(list.index(2))
# list.remove(1)
# print(list)

list_word=[]
list_count=[]
def search_text(text):
    text1=text.split(" ")
    for i in text1:
        if list_word.count(i) == 0:
            list_word.append(i)
            list_count.append(1)
        else:
            a=list_word.index(i)
            list_count[a]+=1
    list_sort=[]
    for j in range(len(list_word)):
        list_sort.append(list_count[j])
        lista=[list_word[j],list_count[j]]
        list_sort.append(lista)
    return list_sort
print(search_text("hello world"))