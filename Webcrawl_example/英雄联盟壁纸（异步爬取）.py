# -*- codeing = utf-8 -*-
# @time :2021/3/24 19:29
# @Author :玉衡Kqing
# @File   ：英雄联盟壁纸.py
# @Software:PyCharm

from bs4 import BeautifulSoup                    #网页解析，获取数据
import re                                        #正则表达式，进行文字匹配
import urllib.request,urllib.error               #指定url获取网页数据
import sqlite3                                   #进行SQLite数据库操作
import requests
import os
import json
import jsonpath                                  #用于筛选json数据
url = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js?v=40"
response = requests.get(url).json()
hero_ids = jsonpath.jsonpath(response,'$..heroId')
for hero_id in hero_ids:
    hero_info_url = "https://game.gtimg.cn/images/lol/act/img/js/hero/{}.js".format(hero_id)
    hero_info = requests.get(hero_info_url).json()         #请求每个英雄的详细信息
    skin_info_list = hero_info['skins']                   #皮肤信息列表
    skin_id_list = jsonpath.jsonpath(skin_info_list,'$..skinId')   #保存单个英雄的所有皮肤ID
    skin_name_list = jsonpath.jsonpath(skin_info_list, '$..name')

    for skin_id,skin_name in zip(skin_id_list,skin_name_list):
        img_url = "https://game.gtimg.cn/images/lol/act/img/skin/big" + str(skin_id) + '.jpg'
        image = requests.get(img_url)     #请求皮肤图片数据

        with open('./英雄联盟壁纸/%s.jpg'%skin_name,"wb") as f:
            f.write(image.content)
        print('《%s》下载成功'%skin_name)






