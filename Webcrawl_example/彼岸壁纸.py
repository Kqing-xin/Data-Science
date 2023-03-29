# -*- codeing = utf-8 -*-
# @time :2021/3/15 17:13
# @Author :玉衡Kqing
# @File   ：testSpider.py
# @Software:PyCharm
import re
from bs4 import BeautifulSoup
import urllib.request,urllib.error
import os
import requests
from PIL import Image

def main():
    baseurl = "https://pic.netbian.com/4kdongman/index.html"
    getData(baseurl)
    baseurl = "https://pic.netbian.com/4kdongman/index.html"
    for i in range(2, 151):
        i = str(i)
        a = "_" + i
        url = baseurl.replace("x", "x_" + i)
        getData(url)



findname = re.compile(r'<img alt="(.*?)"')
findlink = re.compile(r'src="(.*?)"/>')
def getData(baseurl):
    html = askURL(baseurl)
    bs = BeautifulSoup(html, "html.parser")
    for item in bs.select(".slist > .clearfix > li > a > img"):
        data = []
        item = str(item)
        link = "https://pic.netbian.com/"+ re.findall(findlink,item)[0]
        name = re.findall(findname,item)[0]
        data.append(link)
        data.append(name)
        #print(data)
        head = {  # 模拟浏览器头部向服务器发送信息
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
        }
        response = requests.get(link)
        a = "彼岸壁纸"
        if not os.path.exists(a):            #判断是否存在路径，不存在就新建
            os.makedirs(a)                   #新建路径
        with open(a + "/" + '{}.jpg'.format(name),"wb") as f:      #with open（）内先写路径，记得加一个“/”表示切换目录
            f.write(response.content)                   #response.content表示返回二进制形式的图片数据  .text返回字符串数据  json返回一个对象类型数据
            '''
            img = Image.open(' a + "/" + {}.jpg'.format(name))
            img = img.resize((img.size[0]*2,img.size[1]*2),Image.ANTIALIAS)
            img.save('{}.jpg'.format(name),quality=95)  
            '''
             #图像处理
    #return data


def askURL(baseurl):
    head = {                                                                  #模拟浏览器头部向服务器发送信息
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    }                                                                         #用户代理告诉浏览器我们是什么类型机器
    request = urllib.request.Request(baseurl,headers= head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("gbk")
        #print(html)
    except urllib.error.URLError as e :
        if hasattr(e,"code"):                                                 #hasattr() 函数用于判断对象是否包含对应的属性。hasattr(object, name)
            print(e.code)                                                     #获取的错误代码
        if hasattr(e,"reason"):
            print(e.reason)                                                   #获取的错误原因
    return  html



if __name__ == "__main__":
    main()
    print("爬取完毕")