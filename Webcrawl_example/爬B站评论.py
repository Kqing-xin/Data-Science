# -*- codeing = utf-8 -*-
# @time :2021/11/10 10:36
# @Author :玉衡Kqing
# @File   ：爬B站评论.py
# @Software:PyCharm
import requests
from urllib import error,request
import urllib
import json

def askURL(url):
    head = {                                                                  #模拟浏览器头部向服务器发送信息
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    }                                                                         #用户代理告诉浏览器我们是什么类型机器
    request = urllib.request.Request(url,headers= head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        #print(html)
    except urllib.error.URLError as e :
        if hasattr(e,"code"):                                                 #hasattr() 函数用于判断对象是否包含对应的属性。hasattr(object, name)
            print(e.code)                                                     #获取的错误代码
        if hasattr(e,"reason"):
            print(e.reason)                                                   #获取的错误原因
    return  html

def main():
    comments = []
    n = 0
    while n<10:
        print(n)
        url = "https://api.bilibili.com/x/v2/reply/main?&jsonp=jsonp&next=" + str(n) + "&type=1&oid=891511588&mode=3&plat=1"
        # next表示页数，oid代表视频编号
        # mode控制排序顺序：2按时间排序，3按热度排序
        # 1635330608437格式的数字是请求时间的毫秒数
        res = askURL(url)
        with open("json.txt","w",encoding='utf-8') as f:
            f.write(res)
        jsonFile = open("json.txt","r",encoding="utf-8")
        data = json.load(jsonFile)
        #print(data)
        #reply = []        #存放每条评论的回复
        if data['data']['replies'] != "null":
            for i in data['data']['replies']:
                comments.append(i['content']['message'])
            n = n+1
                # for j in range(len(i['replies'])):
                #     reply.append(i['replies'][j]['content']['message'])     #爬每条评论的回复
        else:
            print(len(comments),comments)
            break
    return comments
if __name__ == '__main__':
    res = main()
    print(res)
