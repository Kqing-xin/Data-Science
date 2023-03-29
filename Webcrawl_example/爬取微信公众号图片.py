# @time:2022/9/7 15:27
# @Author:玉衡Kqing
# @File:微信.py
# @Software:PyCharm
import random
import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from pyquery import PyQuery as pq
from selenium.webdriver.support import expected_conditions as EC


def get_proxies():
    """
    此函数用来获取可用的ip地址
    :return: 返回一个proxies_list列表
    """
    proxies_list = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.54"
    }
    response = requests.get("https://www.beesproxy.com/free",headers=headers).text
    doc_obj = pq(response)
    ip = doc_obj("#article-copyright > figure > table > tbody > tr >td:nth-child(1)").items()
    port = doc_obj("#article-copyright > figure > table > tbody > tr >td:nth-child(2)").items()
    for j,k in zip(ip,port):
        url = "http://www.baidu.com"
        ip, port = j.text(),k.text()
        proxy = {'http':f"{ip}:{port}"}
        # print(proxy)
        try:
            res = requests.get(url, proxies=proxy, headers=headers,timeout=2)
            print(res.status_code)
            if res.status_code == 200:
                proxies_list.append(proxy)
        except:
            print(f"{proxy}响应失败")
        continue
    # print(proxies_list)
    return proxies_list   #返回了一个代理ip列表
proxies = get_proxies()
browser = webdriver.Chrome()                #实例化1个谷歌浏览器对象
browser.get("https://mp.weixin.qq.com/s/BZUddNANyZp99OLGPWsBEQ")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.54"
}


#等待页面加载
from selenium.webdriver.support.ui import WebDriverWait
wait = WebDriverWait(browser,10)
button = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="content_bottom_area"]')))
path = "新生爆照/"
if not os.path.exists(path):
    os.makedirs(path)
for i in range(66):
    imgs_dict = {}
    for i in range(1,20):
        try:
            img = browser.find_element(By.XPATH,
                                       f'//*[@id="js_content"]/section[2]/section[{i}]/section/section/section/section/section[1]/img').get_attribute('src')
            info = browser.find_element(By.XPATH,
                                        f'//*[@id="js_content"]/section[2]/section[{i}]/section/section/section/section/section[2]/p[2]').text.replace('  ','')
            number = browser.find_element(By.XPATH,
                                          f'//*[@id="js_content"]/section[2]/section[{i}]/section/section/section/section/section[2]/p[3]/strong[2]/span').text
            text = number + "信息:" + info
            imgs_dict[text] = img
        except:
            print("出错了，已自动跳过")
            continue
    # print(imgs_dict)
    for name,url in imgs_dict.items():
        print(name,url)
        response = requests.get(url,headers=headers,proxies=random.choice(proxies)).content
        with open("./微信图片/" + name[0:8] + ".png", 'wb') as f:
            print(f"正在保存{name}")
            f.write(response)

    try:
        button = browser.find_element(By.XPATH,'//*[@id="content_bottom_area"]/div[1]/div[2]/span[1]')
        button.click()
        time.sleep(5)
    except:
        print("页面加载错误，自动进行下一个")
        continue

# //*[@id="js_content"]/section[2]/section/section/section[1]/section/section/section/section/section[1]/img

# //*[@id="js_content"]/section[2]/section[1]/section/section/section/section/section[1]/img
# //*[@id="js_content"]/section[2]/section[1]/section/section/section/section/section[1]/img
# //*[@id="js_content"]/section[2]/section[3]/section/section/section/section/section[1]/img
# //*[@id="js_content"]/section[2]/section[5]/section/section/section/section/section[1]/img
# //*[@id="js_content"]/section[2]/section[7]/section/section/section/section/section[1]/img
# //*[@id="js_content"]/section[2]/section[8]/section/section/section/section/section[1]/img
# //*[@id="js_content"]/section[2]/section[10]/section/section/section/section/section[1]/img
# //*[@id="js_content"]/section[2]/section[14]/section/section/section/section/section[1]/img
# //*[@id="js_content"]/section[2]/section[16]/section/section/section/section/section[1]/img
# //*[@id="js_content"]/section[2]/section[18]/section/section/section/section/section[1]/img

