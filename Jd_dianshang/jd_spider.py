# @time:2022/10/12 10:48
# @Author:玉衡Kqing
# @File:jd_spider.py
# @Software:PyCharm
import time
import requests
import retrying
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import random
from pyquery import PyQuery as pq
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine
import sqlalchemy


def get_proxies():
    """
    此函数用来获取可用的ip地址
    :return: 返回一个proxies_list列表
    """
    proxies_list = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.54"
    }
    for i in range(1,6):
        flag = 1
        response = requests.get(f"https://www.kuaidaili.com/free/inha/{i}/",headers=headers).text
        doc_obj = pq(response)
        ip = doc_obj("#list > table > tbody  tr > td:nth-child(1)").items()
        port = doc_obj("#list > table > tbody  tr > td:nth-child(2)").items()
        for j,k in zip(ip,port):
            url = "https://www.baidu.com/"
            ip, port = j.text(),k.text()
            proxy = {'http':f"{ip}:{port}"}
            print(f"第{i}页第{flag}个",proxy)
            flag = flag + 1
            try:
                res = requests.get(url, proxies=proxy, headers=headers,timeout=3)
                print(res.status_code)
                if res.status_code == 200 and f"{ip}:{port}" not in proxies_list:
                    proxies_list.append(f"{ip}:{port}")
            except:
                print(f"{proxy}响应失败")
                continue
    print(f"共获取到{len(proxies_list)}个ip")
    # print(proxies_list)
    return proxies_list   #返回了一个代理ip列表
def change_proxy(browser,proxies_list):
    """
    selenium更改代理ip
    :param browser: 实例化的Chrome浏览器对象
    :param proxies_list: [ip:port,ip:port]形式的列表
    :return: 无
    """
    from selenium.webdriver.common.proxy import Proxy, ProxyType
    ip = random.choice(proxies_list)
    print(f"使用{ip}获取当前页")
    proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': ip  # 这里放ip就好
    })
    desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy()
    proxy.add_to_capabilities(desired_capabilities)
    browser.start_session(desired_capabilities)
def get_category_list():
    """
    获取京东的分类信息
    :return: 返回类别列表
    """
    option = webdriver.ChromeOptions()  # 创建一个配置对象
    option.add_argument("--headless")  # 开启无界面模式
    browser = webdriver.Chrome(options=option)
    browser.get("https://www.jd.com/")
    category_list = []
    # for i in range(1,19):
    for i in range(5,6):
        yidong = browser.find_element(By.CSS_SELECTOR,f'#J_cate > ul > li:nth-child({i})')
        ActionChains(browser).move_to_element(yidong).perform()
        # 显式等待
        wait = WebDriverWait(browser, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#cate_item1 > div.cate_part_col1 > div.cate_detail')))
        cates = browser.find_elements(By.CSS_SELECTOR,f"#cate_item{i} > div.cate_part_col1 > div.cate_detail > dl > dt > a")
        for cate in cates:
            name = cate.text.replace("\ue601","")
            print(name)
            category_list.append(name)
        time.sleep(random.randrange(1,3))
    print(category_list)
    return category_list
    # print(f"style={element.get_attribute('style')},id={element.get_attribute('id')},class={element.get_attribute('class')}")
    # 由于京东将元素属性设置为了display:none——隐藏元素并脱离文档流，即隐藏时不占用空间。通过js注入，修改标签属性
    # js = 'document.getElementById("J_popCtn").setAttribute("style","display: block;")'
    # js = 'document.getElementById("J_popCtn").removeAttribute("style")'
    # browser.execute_script(js)
    # print(f"style={element.get_attribute('style')},id={element.get_attribute('id')},class={element.get_attribute('class')}")
def search_category(category_list,proxies_list):
    option = webdriver.ChromeOptions()  # 创建一个配置对象
    option.add_argument("--headless")  # 开启无界面模式
    sku_list = []
    simple_info = []
    for category in category_list:
        browser = webdriver.Chrome(options=option)
        browser.get("https://list.jd.com/list.html?cat=737,794,798")
        sub_sku_list = []
        time.sleep(5)
        browser.find_element(By.CSS_SELECTOR,"#key").click()
        browser.find_element(By.CSS_SELECTOR,"#key").clear()
        browser.implicitly_wait(10)
        browser.find_element(By.CSS_SELECTOR,"#key").send_keys(category)
        time.sleep(1)
        browser.find_element(By.CSS_SELECTOR,"#search-2014 > div > button").click()
        time.sleep(1)
        # 循环获取多页,一页60
        for i in range(5):
        # for i in range(10):
            browser.execute_script(f"document.documentElement.scrollTop=10000")
            browser.implicitly_wait(10)
            browser.find_element(By.CSS_SELECTOR, "#J_goodsList > ul > li:nth-child(60) > div > div.p-img > a > img")
            # 拿到第一页60条信息
            datas_sku = browser.find_elements(By.CSS_SELECTOR,"#J_goodsList > ul > li")
            for data_sku in datas_sku:
                sku = data_sku.get_attribute("data-sku")
                sub_sku_list.append(sku)
                sku_list.append(sku)
            # 下一页
            browser.find_element(By.CSS_SELECTOR, "#J_bottomPage > span.p-num > a.pn-next").click()
            time.sleep(random.randrange(1,3))
        print(f"{category}总共拿到{len(sub_sku_list)}条数据")
        change_proxy(browser=browser, proxies_list=proxies_list)
        browser.quit()
    print(f"总共拿到{len(sku_list)}条数据！")
    df = pd.DataFrame(simple_info)
    df.to_csv("基础表.csv", encoding="utf_8_sig")
    return sku_list

def get_comment(sku,browser):
    """
    获取详情页数据
    :param sku: 商品sku
    :param failed_list: 请求失败后返回的sku_list
    :return: 返回一个商品的评论list
    """
    browser.get(f"https://item.jd.com/{sku}.html")
    browser.implicitly_wait(10)
    first_category = browser.find_element(By.CSS_SELECTOR,"#crumb-wrap > div > div.crumb.fl.clearfix > div.item.first").text
    second_category = browser.find_element(By.CSS_SELECTOR,"#crumb-wrap > div > div.crumb.fl.clearfix > div:nth-child(3)").text
    third_category = browser.find_element(By.CSS_SELECTOR,"#crumb-wrap > div > div.crumb.fl.clearfix > div:nth-child(5)").text
    try:
        brand = browser.find_element(By.CSS_SELECTOR,"#crumb-wrap > div > div.crumb.fl.clearfix > div:nth-child(7) > a").text
    except Exception:
        print(f"{sku}品牌尝试重新获取")
        brand = browser.find_element(By.CSS_SELECTOR,"#crumb-wrap > div > div.crumb.fl.clearfix > div:nth-child(7) > div > div > div.head > a").text
    price = browser.find_element(By.CSS_SELECTOR,"div.summary-price.J-summary-price > div.dd > span.p-price").text
    comments_list = []
    try:
        target = browser.find_element(By.CSS_SELECTOR,"#comment > div.mt")
        browser.execute_script("arguments[0].scrollIntoView();", target)  # 拖动到可见的元素去
        haopingdu = browser.find_element(By.CSS_SELECTOR,"#comment > div.mc > div.comment-info.J-comment-info > div.comment-percent > div").text
    except Exception:
        target = browser.find_element(By.CSS_SELECTOR, "#comment > div.mt")
        browser.execute_script("arguments[0].scrollIntoView();", target)  # 拖动到可见的元素去
        wait = WebDriverWait(browser, 3)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#comment > div.mc > div.comment-info.J-comment-info > div.comment-percent > div')))
        haopingdu = browser.find_element(By.CSS_SELECTOR,
                                         "#comment > div.mc > div.comment-info.J-comment-info > div.comment-percent > div").text
    wait = WebDriverWait(browser, 3)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#comment > div.mc > div.J-comments-list.comments-list.ETab > div.tab-main.small > ul > li.comm-curr-sku')))
    browser.find_element(By.CSS_SELECTOR,"#comment > div.mc > div.J-comments-list.comments-list.ETab > div.tab-main.small > ul > li.comm-curr-sku").click()
    time.sleep(random.randrange(1,3))
    ActionChains(browser).move_to_element(browser.find_element(By.CSS_SELECTOR,"#comment > div.mc > div.J-comments-list.comments-list.ETab > div.tab-main.small > div > div > div.current")).perform()
    ActionChains(browser).move_to_element(browser.find_element(By.CSS_SELECTOR,"#comment > div.mc > div.J-comments-list.comments-list.ETab > div.tab-main.small > div > div > div.current")).perform()
    browser.find_element(By.CSS_SELECTOR,"#comment > div.mc > div.J-comments-list.comments-list.ETab > div.tab-main.small > div > div > div.others > ul > li:nth-child(2)").click()
    time.sleep(1)
    for i in range(5):
        try:
            for i in range(1,11):
                comment_dict = {}
                comment_dict["first_category"] = first_category
                comment_dict["second_category"] = second_category
                comment_dict["third_category"] = third_category
                comment_dict["brand"] = brand
                comment_dict["price"] = price
                comment_dict["good_percent"] = haopingdu
                user_name = browser.find_element(By.CSS_SELECTOR,f"#comment-0 > div:nth-child({i}) > div.user-column > div.user-info").text
                plus = False
                plus_text = browser.find_element(By.CSS_SELECTOR,f"#comment-0 > div:nth-child({i}) > div.user-column > div.user-level").text
                if plus_text == "PLUS会员":
                    plus = True
                star = browser.find_element(By.CSS_SELECTOR,
                                            f"#comment-0 > div:nth-child({i}) > div.comment-column.J-comment-column > div:nth-child(1)").get_attribute(
                    "class")
                content = browser.find_element(By.CSS_SELECTOR,
                                               f"#comment-0 > div:nth-child({i}) > div.comment-column.J-comment-column > p").text.replace(
                    "\n", "")
                style = browser.find_element(By.CSS_SELECTOR,
                                             f"#comment-0 > div:nth-child({i}) > div.comment-column.J-comment-column > div.comment-message > div.order-info > span:nth-child(1)").text
                try:
                    size = browser.find_element(By.CSS_SELECTOR,
                                                f"#comment-0 > div:nth-child({i}) > div.comment-column.J-comment-column > div.comment-message > div.order-info > span:nth-child(2)").text
                except Exception:
                    size = ""
                try:
                    comment_time = browser.find_element(By.CSS_SELECTOR,
                                                        f"#comment-0 > div:nth-child({i}) > div.comment-column.J-comment-column > div.comment-message > div.order-info > span:nth-child(4)").text
                    if comment_time == "":
                        comment_time = browser.find_element(By.CSS_SELECTOR,
                                                        f"#comment-0 > div:nth-child({i}) > div.comment-column.J-comment-column > div.comment-message > div.order-info > span:nth-child(5)").text
                except Exception:
                    print("评论时间获取失败")
                    comment_time = browser.find_element(By.CSS_SELECTOR,
                                                        f"#comment-0 > div:nth-child({i}) > div.comment-column.J-comment-column > div.comment-message > div.order-info > span:nth-child(5)").text
                comment_dict["user_name"] = user_name
                comment_dict["plus"] = plus
                comment_dict["star"] = star
                comment_dict["content"] = content
                comment_dict["style"] = style
                comment_dict["size"] = size
                comment_dict["comment_time"] = comment_time
                print(comment_dict)
                comments_list.append(comment_dict)
            a = browser.find_element(By.CSS_SELECTOR, '#comment-0 > div.com-table-footer > div > div > a.ui-pager-next')
            browser.execute_script("arguments[0].click();", a)
            time.sleep(1)
        except Exception as e:
            print("爬取到最大数量，已跳转到下一个")
            break
    return comments_list
def split_list_n_list(origin_list, n):
    """
    分割列表
    :param origin_list:原始列表
    :param n:要分成几份
    :return:拆分后的列表
    """
    if len(origin_list) % n == 0:
        cnt = len(origin_list) // n
    else:
        cnt = len(origin_list) // n + 1

    for i in range(0, n):
        yield origin_list[i * cnt:(i + 1) * cnt]


# 这是主程序！！！

if __name__ == '__main__':
    proxies_list_origin = get_proxies()
    split_proxies_list = split_list_n_list(proxies_list_origin,9)
    proxies_list = []
    for proxy_list in split_proxies_list:
        print(proxy_list)
        proxies_list.append(proxy_list)

    # category_list = get_category_list()
    category_list = ['女装', '男装']
    sku_list = search_category(category_list,proxies_list=random.choice(proxies_list))
    # print(sku_list)

    # 拆分列表
    sku_list_split = []
    print(len(sku_list))
    sku_list = split_list_n_list(sku_list,5)
    for sku in sku_list:
        sku_list_split.append(sku)
    print(len(sku_list_split))

    option = webdriver.ChromeOptions()  # 创建一个配置对象
    option.add_argument("--headless")  # 开启无界面模式
    flag = 0
    failed_list = []
    for sku_list in sku_list_split:
        comment_list = []
        failed_list = []
        failed_ip_list = []
        group = 1
        browser = webdriver.Chrome()
        for sku in sku_list:
            data = []
            print(f"正在爬取{sku}的信息")
            try:
                lst = get_comment(sku, browser=browser)
                data.extend(lst)
                flag = flag + 1
                time.sleep(random.randrange(1, 3))
                # print(data)
                df = pd.DataFrame(data)
                df.to_csv("详情表.csv",mode="a",index=False,header=False,encoding="utf_8_sig")
            except Exception as e:
                print(e)
                failed_list.append(sku)
                print("出错了，自动进行下一个")
                continue
            if flag % 10 == 0:
                change_proxy(browser, proxies_list=proxies_list[0])
                browser.quit()
                browser = webdriver.Chrome(options=option)
                time.sleep(random.randint(3, 5))
        print(f"第{group}组爬取完成")

    print(failed_list)
    print(f"爬取完成，失败共计{failed_list}条")
        # conn = create_engine('mysql+pymysql://root:xin010727@localhost:3306/jd_database')  # pymysql链接数据库
        # try:
        #     df = pd.DataFrame(comment_list)
        #     df.to_sql('jd_data', conn, if_exists='append', index=False)
        # except:
        #     print('error')


