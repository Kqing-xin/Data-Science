import random
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import re
import io


# ==================== 🛠️ 1. Fetch 区 (只负责请求和返回 DF) ====================
def get_target_dates():
    """
    日期引擎：交互式获取日期区间
    1. 不输入 -> 默认昨天
    2. 只输一个 -> 查单日
    3. 输两个 -> 查区间
    返回: ['2026-04-01', '2026-04-02'...] 格式的列表
    """
    print("\n📅 --- 日期配置 ---")
    start_input = input("请输入开始日期 (如 2026-04-01，回车查昨天): ").strip()

    # 1. 默认逻辑：查昨天
    if not start_input:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"✅ 未输入，已自动选择昨天: {yesterday}")
        return [yesterday]

    # 2. 区间或单日逻辑
    end_input = input("请输入结束日期 (单日查询请直接回车): ").strip()

    if not end_input:
        print(f"✅ 已选择单日查询: {start_input}")
        return [start_input]

    # 3. 自动生成日期序列
    try:
        start_dt = datetime.strptime(start_input, "%Y-%m-%d")
        end_dt = datetime.strptime(end_input, "%Y-%m-%d")

        if start_dt > end_dt:
            print("❌ 错误：开始日期不能晚于结束日期！")
            return []

        delta = end_dt - start_dt
        date_list = [(start_dt + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)]
        print(f"✅ 已生成区间：共 {len(date_list)} 天")
        return date_list
    except ValueError:
        print("❌ 格式错误：请输入正确的日期格式 (例如 2026-04-01)")
        return []

def check_cookie_valid(headers):
    """
    侦测函数：通过请求生意参谋首页或轻量接口，判断 Cookie 是否还有效
    """
    test_url = "https://sycm.taobao.com/cc/item/view/top.json?dateRange=2026-04-06%7C2026-04-06&dateType=day&pageSize=20&page=1&order=desc&orderBy=payAmt&device=0&compareType=cycle&keyword=&follow=false&cateId=&cateLevel=&indexCode=payAmt%2CsucRefundAmt%2CpayItmCnt%2CitemCartCnt%2CitmUv&_=1775565732061&token=f2925201c" # 一个极简的菜单接口
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        # 如果被重定向到了登录页，或者返回 code 是未登录状态
        if "login.taobao.com" in response.url:
            return False
        json_data = response.json()
        if json_data.get("code") in [0, 200]:
            return True
        else:
            return False
    except Exception:
        return False
def fetch_module_preview_3600190(headers):
    """📋26年每日核心指标"""
    url = "https://sycm.taobao.com/lyone/fetchData/preview.json?reportId=3600190"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            json_data = response.json()
            if json_data.get("code") in [0, 200]:
                data_block = json_data.get("data", {})

                # 精准提取表头和数据行
                columns = data_block.get("columns", [])
                rows = data_block.get("rows", [])

                if columns and rows:
                    # 利用 pandas 原生特性直接对齐表头和数据
                    df = pd.DataFrame(data=rows, columns=columns)
                    print(f"  ✅ 获取成功，数据结构为 {len(df)} 行 × {len(columns)} 列。")
                    return df
                else:
                    print("  ⚠️ 数据内容为空 (无 columns 或 rows)。")
                    return pd.DataFrame()
            else:
                print(f"  ⚠️ 业务异常: {json_data.get('message', '未知')}")
        else:
            print(f"  ❌ 网络异常: HTTP {response.status_code}")
    except Exception as e:
        print(f"  ❌ 抓取异常: {e}")

    return pd.DataFrame()

def fetch_module_item_daily_detail(headers, fresh_url):
    """
    D商品数据每日明细
    """
    all_clean_rows = []
    current_page = 1

    while True:
        # 1. 动态生成当前页的 URL (精准替换 page=x)
        paged_url = re.sub(r'page=\d+', f'page={current_page}', fresh_url)

        try:
            response = requests.get(paged_url, headers=headers)
            if response.status_code != 200:
                print(f"  ❌ 第 {current_page} 页请求失败，状态码: {response.status_code}")
                break

            json_data = response.json()
            if json_data.get("code") not in [0, 200]:
                print(f"  ⚠️ 接口返回异常: {json_data.get('message')}")
                break

            raw_list = json_data.get("data", {}).get("data", [])

            # 如果这一页没有数据了，说明已经抓完了，跳出循环
            if not raw_list:
                # print(f" ✅ 当日数据抓取完毕，共 {current_page - 1} 页。")
                break

            # 2. 【你的原始映射逻辑开始 - 完全保留】
            now = time.localtime()
            curr_year = now.tm_year
            curr_month = now.tm_mon

            for entry in raw_list:
                item_info = entry.get("item", {})
                def v(key): # 快捷取值函数
                    return entry.get(key, {}).get("value", 0)

                row = {
                    "年份": curr_year,
                    "月份": curr_month,
                    "统计日期": time.strftime('%Y-%m-%d', time.localtime(entry.get("statDate", {}).get("value")/1000)) if entry.get("statDate") else "-",
                    "商品ID": item_info.get("itemId"),
                    "商品名称": item_info.get("title"),
                    "主商品ID": item_info.get("mainProductId"),
                    "商品类型": "主商品" if item_info.get("itemId") == item_info.get("mainProductId") else "渠道品",
                    "货号": "-",
                    "商品状态": entry.get("itemStatus", "-"),
                    "商品标签": "-",
                    "商品访客数": v("itmUv"),
                    "商品浏览量": v("itmPv"),
                    "平均停留时长": round(v("stayTimeAvg"),2),
                    "商品详情页跳出率": f"{v('itmBounceRate')*100:.2f}%" if v('itmBounceRate') else "0.00%",
                    "商品收藏人数": v("itemCltByrCnt"),
                    "商品加购件数": v("itemCartCnt"),
                    "商品加购人数": v("itemCartByrCnt"),
                    "下单买家数": v("crtByrCnt"),
                    "下单件数": v("crtItmQty"),
                    "下单金额": round(v("crtAmt"),2),
                    "下单转化率": f"{v('crtRate')*100:.2f}%" if v('crtRate') else "0.00%",
                    "支付买家数": v("payByrCnt"),
                    "支付件数": v("payItmCnt"),
                    "支付金额": round(v("payAmt"),2),
                    "商品支付转化率": f"{v('payRate')*100:.2f}%" if v('payRate') else "0.00%",
                    "支付新买家数": v("newPayByrCnt"),
                    "支付老买家数": v("payOldByrCnt"),
                    "老买家支付金额": round(v("olderPayAmt")),
                    "聚划算支付金额": v("jhsPayAmt"),
                    "访客平均价值": round(v("uvAvgValue"),2),
                    "成功退款金额": round(v("sucRefundAmt"),2),
                    "竞争力评分": "-",
                    "年累计支付金额": round(v("ytdPayAmt"),2),
                    "月累计支付金额": round(v("mtdPayAmt"),2),
                    "月累计支付件数": v("mtdPayItmCnt"),
                    "搜索引导支付转化率": f"{v('seGuidePayRate')*100:.2f}%" if v('seGuidePayRate') else "0.00%",
                    "搜索引导访客数": v("seGuideUv"),
                    "搜索引导支付买家数": v("seGuidePayByrCnt"),
                    "结构化详情引导转化率": "-",
                    "结构化详情引导成交占比": "-"
                }
                all_clean_rows.append(row)
            # 【你的原始映射逻辑结束】
            # print(f"  🟢 第 {current_page} 页解析完成，当前累计: {len(all_clean_rows)} 行")
            # 3. 准备抓取下一页
            current_page += 1
            time.sleep(0.5) # 增加小延迟防止被屏蔽
        except Exception as e:
            print(f"  ❌ 第 {current_page} 页解析异常: {e}")
            break

    # 4. 返回汇总后的数据框
    if all_clean_rows:
        df = pd.DataFrame(all_clean_rows)
        return df

    return pd.DataFrame()

def fetch_module_shop_flow_source_all(headers, fresh_url):
    """
    D流量来源
    """
    try:
        response = requests.get(fresh_url, headers=headers)
        if response.status_code == 200:
            json_data = response.json()
            raw_data = json_data.get("data", [])
            clean_rows = []

            # --- 💡 内部取值辅助 ---
            def v(entry, key, field="value"):
                """安全取值：支持嵌套字典取值，取不到返回 None"""
                obj = entry.get(key)
                if isinstance(obj, dict):
                    res = obj.get(field)
                    return res if res is not None else None
                return None

            def fmt_val(val, is_money=False):
                """处理数值：None 转 '-'，金额保留两位，人数转整型"""
                if val is None: return "-"
                try:
                    num = float(val)
                    return round(num, 2) if is_money else int(num)
                except: return "-"

            def fmt_pct(val):
                """处理百分比：None 转 '-'，小数转百分号"""
                if val is None or not isinstance(val, (int, float)): return "-"
                return f"{val * 100:.2f}%"

            # 💡 自动从数据或 URL 提取日期
            def extract_date_info(entry, url):
                # 优先尝试从数据节点取
                ts = v(entry, "statDate")
                if isinstance(ts, (int, float)) and ts > 1000000: # 13位毫秒
                    dt = time.localtime(ts / 1000)
                    return time.strftime('%Y-%m-%d', dt), f"{dt.tm_mon}月"
                # 兼容部分接口 statDate 直接是字符串的情况
                elif isinstance(ts, str) and "-" in ts:
                    return ts, f"{int(ts.split('-')[1])}月"
                # 备选：从 URL 匹配
                match = re.search(r'dateRange=([\d-]+)', url)
                if match:
                    d_str = match.group(1)
                    return d_str, f"{int(d_str.split('-')[1])}月"
                return "-", "-"

            def build_row(entry, l1="-", l2="-", l3="-"):
                row_date, row_month = extract_date_info(entry, fresh_url)

                # 定义内部工具
                get_v = lambda k: v(entry, k, "value")
                get_c = lambda k: v(entry, k, "cycleCrc") # 环比字段

                return {
                    "月份": row_month,
                    "日期": row_date,
                    "一级来源": l1, "二级来源": l2, "三级来源": l3,

                    # --- 1. 核心流量 & 环比 ---
                    "访客数": fmt_val(get_v("uv")),
                    "访客数环比": fmt_pct(get_c("uv")),

                    # --- 2. 下单转化 (映射 crt 字段) ---
                    "下单金额": fmt_val(get_v("crtVldAmt"), True),
                    "下单金额变化": fmt_pct(get_c("crtVldAmt")),
                    "下单买家数": fmt_val(get_v("crtByrCnt")),
                    "下单买家数变化": fmt_pct(get_c("crtByrCnt")),
                    "下单转化率": fmt_pct(get_v("crtRate")),
                    "下单转化率变化": fmt_pct(get_c("crtRate")),

                    # --- 3. 支付转化 (映射 pay 字段) ---
                    "支付金额": fmt_val(get_v("payAmt"), True),
                    "支付金额变化": fmt_pct(get_c("payAmt")),
                    "支付买家数": fmt_val(get_v("payByrCnt")),
                    "支付买家数变化": fmt_pct(get_c("payByrCnt")),
                    "支付转化率": fmt_pct(get_v("payRate")),
                    "支付转化率变化": fmt_pct(get_c("payRate")),

                    # --- 4. 效益指标 ---
                    "客单价": fmt_val(get_v("payPct"), True),
                    "客单价变化": fmt_pct(get_c("payPct")),
                    "UV价值": fmt_val(get_v("uvValue"), True),
                    "uv价值变化": fmt_pct(get_c("uvValue")),

                    # --- 5. 互动 & 留存 ---
                    "关注店铺买家数": fmt_val(get_v("shopCltByrCnt")),
                    "关注店铺买家数变化": fmt_pct(get_c("shopCltByrCnt")),
                    "收藏商品买家数": fmt_val(get_v("cltItmCnt")),
                    "收藏商品买家数变化": fmt_pct(get_c("cltItmCnt")),
                    "加购人数": fmt_val(get_v("cartByrCnt")),
                    "加购人数变化": fmt_pct(get_c("cartByrCnt")),
                    "新访客": fmt_val(get_v("newUv")),
                    "新访客变化": fmt_pct(get_c("newUv")),

                    # --- 6. 细分支付明细 ---
                    "直接支付买家数": fmt_val(get_v("directPayByrCnt")),
                    "收藏商品-支付买家数": fmt_val(get_v("cltItmPayByrCnt")),
                    "粉丝支付买家数": fmt_val(get_v("fansPayByrCnt")),
                    "加购商品-支付买家数": fmt_val(get_v("ordItmPayByrCnt")),

                    # --- 7. 引导 & 广告 ---
                    "引导店铺页访客数": fmt_val(get_v("leShopVisitUv")),
                    "引导店铺页访客数变化": fmt_pct(get_c("leShopVisitUv")),
                    "引导短视频访客数": fmt_val(get_v("guideToShortVideoUv")),
                    "引导商品访客数": fmt_val(get_v("ipvUvRelate")),
                    "种草成交人数": fmt_val(get_v("interestPayUVFlow")),
                    "种草成交金额": fmt_val(get_v("interestPayAmtFlow"), True),
                    "广告成交金额": fmt_val(get_v("adPayAmt"), True),
                    "广告成交金额变化": fmt_pct(get_c("adPayAmt")),
                    "广告点击量": fmt_val(get_v("adPv")),
                    "广告点击量变化": fmt_pct(get_c("adPv"))
                }

            # --- 💡 扁平化循环 (还原原版层级) ---
            for l1 in raw_data:
                n1 = l1.get("pageName", {}).get("value", "-")
                c1 = l1.get("children", [])
                clean_rows.append(build_row(l1, l1=n1, l2=n1 if not c1 else "汇总", l3=n1 if not c1 else "汇总"))
                for l2 in c1:
                    n2 = l2.get("pageName", {}).get("value", "-")
                    c2 = l2.get("children", [])
                    clean_rows.append(build_row(l2, l1=n1, l2=n2, l3=n2 if not c2 else "汇总"))
                    for l3 in c2:
                        n3 = l3.get("pageName", {}).get("value", "-")
                        clean_rows.append(build_row(l3, l1=n1, l2=n2, l3=n3))

            return pd.DataFrame(clean_rows)
    except Exception as e:
        print(f"  ❌ 流量明细解析异常: {e}")
    return pd.DataFrame()

def fetch_module_item_flow_excel(headers, item_id, date_str):
    """
    需求 4: 商品流量来源
    """
    # 1. 构造 Excel 导出链接 (path 必须完全对齐你抓到的那个)
    excel_url = f"https://sycm.taobao.com/flow/excel.do?_path_=v6/excel/item/crowdtype/source/v3&belong=all&dateType=day&dateRange={date_str}%7C{date_str}&crowdType=all&device=2&itemId={item_id}&order=desc&orderBy=uv&token=9420e2bc1"

    try:
        response = requests.get(excel_url, headers=headers)
        if response.status_code == 200:
            # 💡 既然报错里出现了 Java Excel API，说明它是真正的二进制 .xls
            # 我们直接用 io.BytesIO 配合 read_excel，并指定引擎为 xlrd
            excel_data = io.BytesIO(response.content)
            # 使用 xlrd 引擎读取
            df = pd.read_excel(excel_data, engine='xlrd')
            if df.empty: return pd.DataFrame()
            # --- 💡 关键清洗：寻找真实表头 ---
            # 生意参谋导出的 Excel 前几行经常是描述文字
            header_row = 0
            for i in range(len(df)):
                # 检查这一行是否包含我们需要的关键指标，比如“访客数”
                row_values = [str(x) for x in df.iloc[i].values]
                if any("访客数" in v for v in row_values):
                    header_row = i
                    break
            # 重新设定表头并剔除上方说明行
            df.columns = df.iloc[header_row]
            df = df.iloc[header_row + 1:].reset_index(drop=True)

            # 去掉末尾的说明文字行
            # 逻辑：第一列（流量来源）不能为空
            df = df[df.iloc[:, 0].notna()].copy()

            # 插入维度列（年份、月份、日期、ID等）
            df.insert(0, "ID", item_id)
            df.insert(0, "日期", date_str)
            # ... 剩下的清洗逻辑和之前一样 ...
            return df
    except Exception as e:
        print(f"  ❌ Excel 解析失败: {e}")
    return pd.DataFrame()

def fetch_module_flow_source_detail(headers, fresh_url, date_str):
    """
    D手搜关键词数据源
    """
    all_clean_rows = []
    current_page = 1

    # 1. 自动识别初始 URL 里的 pageSize，如果没有则默认为 10
    page_size_match = re.search(r'pageSize=(\d+)', fresh_url)
    page_size = int(page_size_match.group(1)) if page_size_match else 10

    while True:
        # 🎯 核心逻辑：精准替换 URL 里的 page=x 为当前页码
        paged_url = re.sub(r'page=\d+', f'page={current_page}', fresh_url)

        try:
            response = requests.get(paged_url, headers=headers)
            if response.status_code != 200:
                print(f"  ❌ 第 {current_page} 页请求失败，状态码: {response.status_code}")
                break

            json_data = response.json()
            # 兼容生意参谋的 code 0 或 200
            if json_data.get("code") not in [0, 200]:
                print(f"  ⚠️ 接口返回异常: {json_data.get('message')}")
                break

            # 对应你提供的 JSON 层级：data 节点下的 data 列表
            data_node = json_data.get("data", {})
            raw_list = data_node.get("data", [])
            record_count = data_node.get("recordCount", 0)

            # 如果这一页没有数据了，跳出循环
            if not raw_list:
                break

            # --- 取值工具：穿透 {'value': x} 且兼容字符串 ---
            def v(entry, key):
                target = entry.get(key)
                if isinstance(target, dict) and 'value' in target:
                    return target.get('value')
                return target

            # --- 数据清洗 ---
            for entry in raw_list:
                ts = v(entry, "statDate")
                dt = datetime.fromtimestamp(int(ts)/1000) if ts else None

                row = {
                    "月份": f"{dt.month}月" if dt else "-",
                    "日期": date_str,
                    "来源名称": v(entry, "pageName"),
                    "访客数": v(entry, "uv"),
                    "支付转化率": f"{(float(v(entry, 'payRate') or 0))*100:.2f}%",
                    "支付金额": round(float(v(entry, "payAmt") or 0), 2),
                    "客单价": round(float(v(entry, "payPct") or 0), 2),
                    "下单金额": round(float(v(entry, "crtVldAmt") or 0), 2),
                    "下单买家数": v(entry, "crtByrCnt"),
                    "下单转化率": f"{(float(v(entry, 'crtRate') or 0))*100:.2f}%",
                    "支付买家数": v(entry, "payByrCnt"),
                    "UV价值": round(float(v(entry, "uvValue") or 0), 2),
                    "关注店铺人数": v(entry, "shopCltByrCnt"),
                    "收藏商品买家数": v(entry, "cltItmCnt"),
                    "加购人数": v(entry, "cartByrCnt"),
                    "新访客": v(entry, "newUv"),
                    "直接支付买家数": v(entry, "directPayByrCnt"),
                    "收藏商品-支付买家数": v(entry, "cltItmPayByrCnt"),
                    "粉丝支付买家数": v(entry, "fansPayByrCnt"),
                    "加购商品-支付买家数": v(entry, "ordItmPayByrCnt")
                }
                all_clean_rows.append(row)

            # --- 判定是否需要翻页 ---
            # 如果当前抓取的总行数已经达到或超过接口返回的 recordCount，则停止
            if len(all_clean_rows) >= record_count:
                break

            current_page += 1
            time.sleep(random.uniform(0.5, 1.2)) # 礼貌等待

        except Exception as e:
            print(f"❌ 解析异常: {e}")
            break

    return pd.DataFrame(all_clean_rows)

def fetch_module_cate_macro_excel(headers, date_str):
    """
    D类目每日明细
    """
    # 构造 URL
    url = f"https://sycm.taobao.com/cc/cockpit/marcro/excel/cate.json?dateRange={date_str}%7C{date_str}&dateType=day&pageSize=10&page=1&order=desc&orderBy=payAmt&dtUpdateTime=false&follow=false&cateType=std&indexCode=payAmt%2CpayAmtRatio%2CsucRefundAmt%2CpayRate%2CitmUv&token=9420e2bc1"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # 💡 注意：这类 .json 结尾的导出接口，有时返回的是带下载链接的 JSON
            # 如果它返回的是二进制流，则用下面的 io.BytesIO 逻辑
            # 如果报错，请截图告诉我返回的内容
            excel_data = io.BytesIO(response.content)
            df = pd.read_excel(excel_data, engine='xlrd')

            if df.empty: return pd.DataFrame()

            # 寻找表头清洗逻辑 (同你之前的逻辑)
            header_row = 0
            for i in range(min(10, len(df))):
                row_vals = [str(x) for x in df.iloc[i].values]
                if any("支付金额" in v or "类目" in v for v in row_vals):
                    header_row = i
                    break

            df.columns = df.iloc[header_row]
            df = df.iloc[header_row + 1:].reset_index(drop=True)
            df = df[df.iloc[:, 0].notna()].copy()

            df.insert(0, "日期", date_str)
            return df
    except Exception as e:
        print(f"  ❌ 类目大盘解析失败: {e}")
    return pd.DataFrame()

def fetch_module_shop_summary_excel(headers, date_str):
    """
    D新版流量来源
    """
    url = f"https://sycm.taobao.com/flow/gray/excel.do?_path_=v4/excel/shop/source/platform/summay/v4&dateType=day&dateRange={date_str}%7C{date_str}&crowdType=all&needCate=true"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            excel_data = io.BytesIO(response.content)
            # 💡 sheet_name=None 读取所有 Sheet，返回字典 {Sheet名: DataFrame}
            all_sheets_dict = pd.read_excel(excel_data, engine='xlrd', sheet_name=None)

            processed_daily_dict = {}

            for sheet_name, df in all_sheets_dict.items():
                if df.empty: continue

                # --- 你的核心清洗逻辑：寻找真实表头 ---
                header_row = 0
                found_header = False
                # 扫描前 15 行寻找表头
                for i in range(min(15, len(df))):
                    row_vals = [str(x) for x in df.iloc[i].values]
                    if any("访客数" in v or "流量来源" in v or "终端" in v for v in row_vals):
                        header_row = i
                        found_header = True
                        break

                if not found_header:
                    continue # 没找到表头的 Sheet (如说明页) 直接跳过

                # 重新设定表头并切片
                df.columns = df.iloc[header_row]
                df = df.iloc[header_row + 1:].reset_index(drop=True)

                # 剔除第一列为空的行
                df = df[df.iloc[:, 0].notna()].copy()

                # 插入日期维度（方便合并后区分）
                df.insert(0, "日期", date_str)

                processed_daily_dict[sheet_name] = df

            return processed_daily_dict # 返回这一天洗好的所有表

    except Exception as e:
        print(f"  ❌ {date_str} 报表解析失败: {e}")
    return {}
def fetch_module_item_source_excel(headers, date_str, item_id):
    """
    D新版单品流量来源
    """
    url = f"https://sycm.taobao.com/flow/gray/excel.do?_path_=excel/item/source/platform&dateRange={date_str}%7C{date_str}&dateType=day&itemId={item_id}&order=desc&orderBy=uv&flowBizType=classic&crowdType=all"
    try:
        # 解析日期字符串
        dt_obj = datetime.strptime(date_str, "%Y-%m-%d")
        year_val = dt_obj.year        # 2026
        month_val = f"{dt_obj.month}月" # 3月

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            excel_data = io.BytesIO(response.content)
            # 默认读取第一张 Sheet (所有终端)
            df = pd.read_excel(excel_data, engine='xlrd')

            if df.empty: return pd.DataFrame()

            # --- 清洗：寻找表头 ---
            header_row = 0
            for i in range(min(15, len(df))):
                row_vals = [str(x) for x in df.iloc[i].values]
                if any("流量来源" in v or "访客数" in v for v in row_vals):
                    header_row = i
                    break

            df.columns = df.iloc[header_row]
            df = df.iloc[header_row + 1:].reset_index(drop=True)
            df = df[df.iloc[:, 0].notna()].copy()

            # --- 💡 关键步骤：按顺序插入要求的维度列 ---
            # 插入顺序：年份 -> 月份 -> 日期 -> ID
            df.insert(0, "ID", item_id)
            df.insert(0, "日期", date_str)
            df.insert(0, "月份", month_val)
            df.insert(0, "年份", year_val)

            return df
    except Exception as e:
        print(f"  ❌ 商品 {item_id} 解析失败: {e}")
    return pd.DataFrame()

# ==================== 🧠 2. 导出区 (导出文件) ====================
def export_to_excel(dfs_dict, file_prefix="生意参谋汇总"):
    """接收 {Sheet名: DataFrame} 字典，统一导出"""
    if not dfs_dict:
        print("⚠️ [Export] 没有收集到任何有效数据，取消导出。")
        return

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"{file_prefix}_{timestamp}.xlsx"
    print(f"\n💾 [Export] 开始打包写入 {len(dfs_dict)} 个数据表...")

    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for sheet_name, df in dfs_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"  -> 成功写入 Sheet: [{sheet_name}] ({len(df)} 行)")
        print(f"🎉 [Export] 任务圆满完成！文件已生成: {output_file}\n")
    except Exception as e:
        print(f"❌ [Export] 写入文件时发生错误: {e}")

# ==================== 🧠 3. Main 区 (装配粮草，统筹执行) ====================

if __name__ == "__main__":
    print("🚀 启动数据抓取流水线...\n" + "-" * 50)
    # 1. 读取本地 Cookie
    try:
        with open("cookie.txt", "r", encoding="utf-8") as f:
            MY_COOKIE = f.read().strip()
    except FileNotFoundError:
        MY_COOKIE = ""

    global_headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "Referer": "https://sycm.taobao.com/",
        "Cookie": MY_COOKIE
    }

    # 2. 核心校验：判断内容是否为空或已过期
    print("🔍 正在验证权限状态...")
    if not MY_COOKIE or not check_cookie_valid(global_headers):
        print("\n" + "!"*60)
        print("❌ 【权限失效报警】")
        print("原因:Cookie已经过期了。")
        print("\n操作指引：")
        print("1. 请打开浏览器，重新登录生意参谋官网。")
        print("2. 按 F12 -> 进入 Network -> 刷新页面 -> 找到任意一个接口。")
        print("3. 复制最新的 Cookie 字符串，覆盖粘贴到 cookie.txt 文件并保存。")
        print("4. 重新双击运行本程序。")
        print("!"*60)
        input("\n按回车键退出程序...")
        exit()

    print("✅ 权限验证通过，开始同步数据...")
    # --------------------------------
    # 1. 配置全局 Headers (手动填入你的 Cookie)
    # MY_COOKIE = "t=840dc8cfa036c7263cbe52582afecbc0; wk_cookie2=1cd10d6b8788d39ed7f7252c519c1d3f; wk_unb=UUphyu%2BFsPw8EGXhcQ%3D%3D; xlly_s=1; mtop_partitioned_detect=1; _m_h5_tk=646a7ccc59128ec45e8b38a369fb4ba5_1775566136639; _m_h5_tk_enc=c0355694ff6f8f98dcb6ecddb7c6b320; cookie2=13dc3282447d343ca337d25fef9a45c9; _tb_token_=7081e7b8be3ee; _samesite_flag_=true; 3PcFlag=1775560655477; sgcookie=E100znLs1Qd%2BuAzWcoiThf1vZBxhtvTodz4dMLMlVO0cUAqbHo%2BSG%2FHpEKlShmw21gcQZuaKqBynF2bvxLCMeSGd35BvMiuC58RLFfpfOcVdClyP88owbZ4awbRdn2CNf70o; unb=2221493682405; sn=correctors%E7%A7%91%E7%91%9E%E8%82%A4%E6%97%97%E8%88%B0%E5%BA%97%3A%E6%A9%99%E5%AD%90; uc1=cookie21=VFC%2FuZ9aj3yE&cookie14=UoYZbx52painfw%3D%3D; csg=d5e7a66d; _cc_=VFC%2FuZ9ajQ%3D%3D; cancelledSubSites=empty; skt=4b737caa02650106; _euacm_ac_l_uid_=2221493682405; 2221493682405_euacm_ac_c_uid_=2210606851499; 2221493682405_euacm_ac_rs_uid_=2210606851499; _euacm_ac_rs_sid_=null; _portal_version_=new; cc_gray=1; XSRF-TOKEN=b1521d71-967d-447d-8114-49fc51742848; x_one_bi_sr=one-bi-sr-552c1f04c926458681b6365bee49bf5c-2210606851499-2221493682405; x_one_bi_token=one-bi-9384a0e01db44f5da4b2f60958a018c8-2210606851499-2221493682405; JSESSIONID=CF2F6F3438B9E26DDAACAB7004566D79; tfstk=gD9soEYOzP46H8otkPoUAdlWcfXXlDkrHosvqneaDOBOkxLvRseqsO5fheQeQN-NBmMvJeRNWfjNDEOplsoMu57xhnQH3cbqsSwXqEYVWsoMDEtX2VYZjnrMtU-8QdlG3-6Gnt3rzYkrjhXcHhHNzREGpiS8Bx5AkvBG0pEaJPMyjhqLfrny9Ykf4PXCkZLA66FdbweYWEeYpDsA0PFYBEKKAwj46GCT6yBd2ieAHtLvvDscJGBA6EKKAibdkbRYdih12hixr9_Il46HXwwYHdHc1aMFSMjpdG11y6QQHMJCf1_JXLdQ55spLp1PToudp3AeWM6SL5BJAILWwEcztOtv6EfBS2VC8BpMDZC_D8-BRnBpBQZYHH61S6pOTPgCydxpE9CEe0tpKF-MdnrxHM8PJhvOhYnlCOQOdMvq-RQX9IpNst4tz1xvOes1egP8Ua6x2SZCZ-ICzDiQiSjmkt0eb8NvR1Ihf4oIAPVc6MjCzDiQiSfOxGtrADagi"
    global_headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "Referer": "https://sycm.taobao.com/",
        "Cookie": MY_COOKIE
    }

    target_dates = get_target_dates()
    print(target_dates)
    if not target_dates:
        print("🛑 日期获取失败，程序退出。")
    else:
        # 2. 收集战利品的“篮子”
        all_results = {}

        # --- 开始依次执行 Fetch 任务 ---
        # [📋26年每日核心指标] --start
        print("\n📦 正在抓取模块 1: 26年每日核心指标")
        df1 = fetch_module_preview_3600190(global_headers)
        if not df1.empty:
            all_results["26年每日核心指标"] = df1
        # [📋26年每日核心指标] --end


        # [D商品数据每日明细]  --start
        print(f"\n📦 正在抓取模块 2: D商品数据每日明细 (共 {len(target_dates)} 天)...")
        FRESH_URL_2 = "https://sycm.taobao.com/cc/item/view/top.json?dateRange=2026-04-06%7C2026-04-06&dateType=day&pageSize=20&page=1&order=desc&orderBy=payAmt&device=0&compareType=cycle&keyword=&follow=false&cateId=&cateLevel=&indexCode=payAmt%2CsucRefundAmt%2CpayItmCnt%2CitemCartCnt%2CitmUv&_=1775565732061&token=f2925201c"
        combined_item_list = []  # 用于临时存放每天抓到的 DataFrame
        for date_str in target_dates:
            current_date_url = re.sub(r'dateRange=[\d-]+%7C[\d-]+', f'dateRange={date_str}%7C{date_str}', FRESH_URL_2)
            df_daily = fetch_module_item_daily_detail(global_headers, current_date_url)
            if not df_daily.empty:
                combined_item_list.append(df_daily)
                print(f"  ✅ {date_str} 获取成功,共 {len(df_daily)} 条记录。")
        if combined_item_list:
            df2_combined = pd.concat(combined_item_list, ignore_index=True)
            all_results["D商品数据每日明细"] = df2_combined
        # [D商品数据每日明细]  --end


        # [D流量来源] --start
        print(f"\n📦 正在抓取模块 3: D流量来源 (共 {len(target_dates)} 天)...")
        # 💡 粘贴你刚才抓到的那个 tree/v3.json 链接 (确保包含 indexCode 和 dateType=day)
        FRESH_URL_3_DAY = "https://sycm.taobao.com/flow/v5/shop/source/tree/v3.json?dateRange=2026-04-01%7C2026-04-01&dateType=day&pageSize=10&page=1&order=desc&orderBy=uv&device=2&belong=all&indexCode=uv%2CnewUv%2CcartByrCnt%2CpayByrCnt&token=9420e2bc1"
        combined_flow_list = []  # 用于临时存放每天抓到的 DataFrame
        for date_str in target_dates:
            # 💡 极简日期替换：只替换单日期格式 (YYYY-MM-DD%7CYYYY-MM-DD)
            current_date_url = re.sub(r'dateRange=[\d-]+%7C[\d-]+', f'dateRange={date_str}%7C{date_str}', FRESH_URL_3_DAY)
            # 抓取数据
            df_daily = fetch_module_shop_flow_source_all(global_headers, current_date_url)
            if not df_daily.empty:
                combined_flow_list.append(df_daily)
                print(f"  ✅ {date_str} 获取成功,共 {len(df_daily)} 条记录")
        # 合并所有日期的数据并存入结果集
        if combined_flow_list:
            all_results["D流量来源"] = pd.concat(combined_flow_list, ignore_index=True)
        # [D流量来源] --end


        # [D单品流量数据源] --start
        target_item_ids = ["657207835145", "666211498090", "871500035978"] # 👈 在这里填入你需要的所有商品 ID
        print(f"\n📦 正在抓取模块 4: 商品流量来源 (共 {len(target_dates)} 天 * {len(target_item_ids)} 个商品)...")
        # 你的商品明细 URL 模板
        FRESH_URL_4 = "https://sycm.taobao.com/flow/v6/item/crowdtype/source/v3.json?belong=all&dateRange=2026-04-01%7C2026-04-01&dateType=day&pageSize=10&page=1&order=desc&orderBy=uv&itemId=657207835145&device=2&indexCode=uv%2CcartByrCnt%2CpayByrCnt&_=1775642473912&token=9420e2bc1"
        combined_item_flow = []
        for date_str in target_dates:
            for item_id in target_item_ids:
                df_item = fetch_module_item_flow_excel(global_headers, item_id, date_str)
                if not df_item.empty:
                    combined_item_flow.append(df_item)
                    print(f"✅ {date_str} {item_id} 获取成功,共 {len(df_item)} 条记录 ")
        if combined_item_flow:
            all_results["D单品流量数据源"] = pd.concat(combined_item_flow, ignore_index=True)
        # [D单品流量数据源] --end


        # [D手搜关键词数据源] --start
        print(f"\n📦 正在抓取模块 5:D手搜关键词数据源  (共 {len(target_dates)} 天)...")
        FRESH_URL_4 = "https://sycm.taobao.com/flow/v3/shop/source/detail/v3.json?dateRange=2026-04-07%7C2026-04-07&dateType=day&pageSize=100&page=1&order=desc&orderBy=uv&device=2&belong=all&pageId=23.s1150&pPageId=30&childPageType=se_keyword&indexCode=uv%2CcrtByrCnt%2CcrtRate&_=1775647072085&token=9420e2bc1"
        combined_flow_list = []
        for date_str in target_dates:
            current_date_url = re.sub(r'dateRange=[\d-]+%7C[\d-]+', f'dateRange={date_str}%7C{date_str}', FRESH_URL_4)
            df_daily = fetch_module_flow_source_detail(global_headers, current_date_url, date_str)
            if not df_daily.empty:
                combined_flow_list.append(df_daily)
                print(f"  ✅ {date_str} 获取成功,共 {len(df_daily)} 条记录")
            time.sleep(random.uniform(1, 2))
        if combined_flow_list:
            # 合并、去重、存入结果字典
            df4_combined = pd.concat(combined_flow_list, ignore_index=True)
            all_results["D手搜关键词数据源"] = df4_combined
        # [D手搜关键词数据源] --end



        # [D类目每日明细] --strat
        print(f"\n📦 正在抓取模块 6:D类目每日明细 (共 {len(target_dates)} 天)... ")
        combined_cate_results = []
        for date_str in target_dates:
            df_daily = fetch_module_cate_macro_excel(global_headers, date_str)
            if not df_daily.empty:
                combined_cate_results.append(df_daily)
                print(f"  ✅ {date_str} 获取成功,共 {len(df_daily)} 条记录")
            # time.sleep(random.uniform(2.5, 4.0))
        if combined_cate_results:
            # 放入你要求的标题名称
            all_results["D类目每日明细"] = pd.concat(combined_cate_results, ignore_index=True)
        # [D类目每日明细] --end


        # [D新版流量来源]  --start
        print(f"\n📦 正在抓取模块 7: D新版流量来源 (共 {len(target_dates)} 天)...  ")
        # 建立一个总容器，用来存放所有日期的数据
        # 结构：{ 'Sheet名': [df_1号, df_2号, ...] }
        collector_map = {}
        for date_str in target_dates:
            # 1. 获取这一天洗好的多张表
            daily_data_dict = fetch_module_shop_summary_excel(global_headers, date_str)
            # 2. 将这一天的每张表投递到对应的“分类框”里
            for s_name, s_df in daily_data_dict.items():
                if s_name not in collector_map:
                    collector_map[s_name] = []
                collector_map[s_name].append(s_df)
        # 4. 最后一步：将每个“分类框”里的 DataFrame 合并，并存入 all_results
        # 只要 collector_map 里的 Key 不同，export_to_excel 就会生成独立的 Sheet
        for s_name, df_list in collector_map.items():
            if df_list:
                # 这里的 Key (如 "汇总_所有终端") 将直接成为 Excel 里的 Sheet 名字
                sheet_title = f"{s_name}"
                all_results[sheet_title] = pd.concat(df_list, ignore_index=True)
                print(f"  ✅ Sheet [{sheet_title}] 获取成功，共 {len(all_results[sheet_title])} 行。")
        # [D新版流量来源]  --end


        # [D新版单品流量来源]  --strat
        target_item_ids = ["657207835145", "666211498090", "871500035978"]
        print(f"\n📦 正在抓取模块 8: D新版单品流量来源 (共 {len(target_dates)} 天 * {len(target_item_ids)} 个商品)...")
        all_item_dfs = []
        for date_str in target_dates:
            for item_id in target_item_ids:
                df_item_daily = fetch_module_item_source_excel(global_headers, date_str, item_id)
                if not df_item_daily.empty:
                    all_item_dfs.append(df_item_daily)
                    print(f"  ✅ {date_str} {item_id} 获取成功,共 {len(df_item_daily)} 条记录")
                # 间隔，避免被风控
                time.sleep(random.uniform(0.5, 1))
        if all_item_dfs:
            # 最终合并成一个 Sheet
            all_results["D新版单品流量来源"] = pd.concat(all_item_dfs, ignore_index=True)
        # [D新版单品流量来源]  --end

        # print(all_results)
        # 3. 将装满战利品的篮子交给 Export 模块
        export_to_excel(all_results, file_prefix="生意参谋_多模块自动获取")

