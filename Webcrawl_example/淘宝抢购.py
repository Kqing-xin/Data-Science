# -*- codeing = utf-8 -*-
# @time :2021/4/22 16:41
# @Author :玉衡Kqing
# @File   ：淘宝.py
# @Software:PyCharm

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 2018/09/05
# 淘宝秒杀脚本，扫码登录版
from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime
import time
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
browser = webdriver.Edge()
print(now)
def login():
    # 打开淘宝首页，通过扫码登录
    browser.get("https://www.taobao.com/")
    if browser.find_element(By.LINK_TEXT,"亲，请登录"):
        browser.find_element(By.LINK_TEXT,"亲，请登录").click()
        print(f"请尽快扫码登录")
    time.sleep(10)

def picking():
    # 打开购物车列表页面
    browser.find_element(By.XPATH,'//*[@id="J_MiniCart"]/div[1]/a').click()
    time.sleep(3)
    # method = 0全选购物车
    method = 0
    if method == 0:
        while True:
            try:
                if browser.find_element(By.XPATH,'//*[@id="J_SelectAll1"]/div/label'):
                    browser.find_element(By.XPATH,'//*[@id="J_SelectAll1"]/div/label').click()
                    break
            except:
                print(f"找不到购买按钮")
    #method = 1 手动勾选
    else:
        print(f"请手动勾选需要购买的商品")
        time.sleep(5)

#等待抢购时间，定时秒杀，这里我们定义一个buy函数
def buy(times):
    print(times)
    while True:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        # 对比时间，时间到的话就点击结算
        if now > times:
            # 点击结算按钮
            while True:
                try:
                    if browser.find_element(By.XPATH,'//*[@id="J_Go"]'):
                        browser.find_element(By.XPATH,'//*[@id="J_Go"]').click()
                        print(f"结算成功，准备提交订单")
                        break
                except:
                    pass
            # 点击提交订单按钮
            while True:
                try:
                    if browser.find_element(By.XPATH,'//*[@id="submitOrderPC_1"]/div/a[2]'):
                        browser.find_element(By.XPATH,'//*[@id="submitOrderPC_1"]/div/a[2]').click()
                        print(f"抢购成功，请尽快付款")
                        break
                except:
                    print(f"再次尝试提交订单")
            time.sleep(0.01)
def main():
    login()
    picking()
    times = input("请输入抢购时间，格式如(2018-09-06 11:20:00.000000):")
    buy(times)

if __name__ == '__main__':
    main()