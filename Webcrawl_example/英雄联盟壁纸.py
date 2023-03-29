import urllib3
from urllib3 import request
import requests
import json
import time
import os
import re
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44"}
def get_Page():
    page_urls = []
    url = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"
    res = requests.get(url,headers=header)
    res = res.content.decode("utf*8")
    find_id = re.compile(r'{"heroId":"(.*?)"')
    hero_id = re.findall(find_id,res)
    for i in hero_id:
        url = f"https://game.gtimg.cn/images/lol/act/img/js/hero/{i}.js"
        page_urls.append(url)
    return page_urls

def get_img_urls():
    results_list = []
    page_urls = get_Page()

    for page_url in page_urls:
        res = requests.get(page_url,headers=header)
        result = res.content.decode("utf-8")
        result_dict = json.loads(result)
        skins_list = result_dict["skins"]
        #print(skins_list)
        for skin in skins_list:
            hero_dict = {}
            hero_dict["name"] = skin["heroName"]
            hero_dict["skin_name"] = skin["name"]

            if skin["mainImg"] == '':
                continue
            hero_dict["imgUrl"] = skin["mainImg"]
            print(hero_dict)
            results_list.append(hero_dict)
        #time.sleep(2)
    return results_list

def save_image(index,img_url):
    path = "skin/" + img_url["name"]
    if not os.path.exists(path):
        os.makedirs(path)
    response = requests.get(img_url["imgUrl"],headers=header).content
    try:
    #print(response)
        with open("./skin/" + img_url['name'] + "/" + img_url['skin_name'] + ".jpg","wb") as f:
            f.write(response)
    except BaseException:
        mod_skin_name = str(img_url['skin_name']).replace("/"," ")
        with open("./skin/" + img_url['name'] + "/" + mod_skin_name + ".jpg","wb") as f:
            f.write(response)

def main():
    image_urls = get_img_urls()
    print(f"总共有{len(image_urls)}个网页")
    for index,img_url in enumerate(image_urls):
        print(f"目前正处于{image_urls.index(img_url)}")
        save_image(index,img_url)
    print("Done")



if __name__ == '__main__':
    main()