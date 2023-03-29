# -*- codeing = utf-8 -*-
# @time :2021/2/5 12:29
# @Author :玉衡Kqing
# @File   ：豆瓣.py
# @Software:PyCharm



from bs4 import BeautifulSoup                    #网页解析，获取数据
import re                                        #正则表达式，进行文字匹配
import urllib.request,urllib.error               #指定url获取网页数据
import xlwt                                      #进行excel操作
import sqlite3                                   #进行SQLite数据库操作



def main():
    baseurl = "https://movie.douban.com/top250?start="
    #1.爬取网页
    datalist = getData(baseurl)
    savepath = "豆瓣电影top250.xls"              #保存路径， .是指当前文件夹，\\新建一个文件夹
    #3.保存数据
    saveData(datalist,savepath)

    #askURL("https://movie.douban.com/top250?start=")

#影片详情链接的规则
findLink = re.compile(r'<a href="(.*?)">')                                 #创建正则表达式对象，表示规则
#影片图片
findImgSrc = re.compile(r'<img .*src="(.*?)"',re.S)                        #re.S 匹配包括换行符在内的字符
#影片片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
#影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')
#影片概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
#找到影片相关内容
findBd = re.compile(r'<p class="">(.*?)</p>',re.S)

#爬取网页
def getData(baseurl):
    datalist = []
    for i in range(0,10):
        url = baseurl + str(i*25)                                             #调用获取页面信息的函数10次
        html = askURL(url)                                                    #保存获取到的网页源码
    # 2.逐一解析数据
        soup = BeautifulSoup(html,"html.parser")
        for item in soup.find_all('div',class_="item"):
            #print(item)                                                       #测试：查看电影item的全部信息
            data = []                                                         #保存一部电影的全部信息
            item = str(item)

            #获取影片详情的链接
            link = re.findall(findLink,item) [0]                                 #re库用来通过正则表达式查找指定的字符串
            data.append(link)                                                    #添加链接

            imgSrc = re.findall(findImgSrc,item)[0]
            data.append(imgSrc)                                                  #添加图片

            titles = re.findall(findTitle,item)                                   #片名可能只有中文名，没有外文
            if len(titles) == 2:
                ctitle = titles[0]                                               #ctitle表示中文名
                data.append(ctitle)                                              #添加中文名
                otitle = titles[1].replace("/","")                               #去掉无关的符号
                data.append(otitle)
            else:
                data.append(titles[0])
                data.append("  ")                                                #外国名字留空

            rating = re.findall(findRating,item)[0]
            data.append(rating)                                                  #添加评分

            judgeNum = re.findall(findJudge,item)[0]
            data.append(judgeNum)                                                #添加评价人数

            inq = re.findall(findInq,item)
            if len(inq) != 0 :
                inq = inq[0].replace("。","")                                    #去掉句号
                data.append(inq)                                                 #添加概述
            else:
                data.append("")                                                  #留空

            bd = re.findall(findBd,item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?',' ',bd)                              #去掉<br/>
            bd = re.sub('/',' ',bd)                                              #替换/
            data.append(bd.strip())                                              #去掉前后的空格

            datalist.append(data)                                               #把处理好的一部电影的信息放入datalist
    return datalist

def askURL(url):
    head = {                                                                  #模拟浏览器头部向服务器发送信息
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    }                                                                         #用户代理告诉浏览器我们是什么类型机器
    request = urllib.request.Request(url,headers= head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        print(html)
    except urllib.error.URLError as e :
        if hasattr(e,"code"):                                                 #hasattr() 函数用于判断对象是否包含对应的属性。hasattr(object, name)
            print(e.code)                                                     #获取的错误代码
        if hasattr(e,"reason"):
            print(e.reason)                                                   #获取的错误原因
    return  html
#3.保存数据
def saveData(datalist,savepath):
    print("save.....")
    book = xlwt.Workbook(encoding="utf-8",style_compression=0)           #创建workbook对象
    sheet = book.add_sheet("豆瓣电影top250",cell_overwrite_ok=True)       #创建工作表
    col = ("电影链接","图片链接","影片中文名","影片外国名","评分","评价数","概况","相关信息")
    for i in range (0,8):
        sheet.write(0,i,col[i])                     #列名
    for i in range (0,250):
        print("第%d条"%(i+1))
        data = datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j])             #数据
    book.save(savepath)                  #保存


if __name__ == "__main__":                           #当程序执行时
#调用函数
    main()
    print("爬取完毕")