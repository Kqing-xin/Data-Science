# 股票量化交易系统

这是一个基于 Python 和 Jupyter Notebook 的股票量化交易系统，用于帮助股票交易者分析和决策。

## 功能

该系统支持以下功能：

- 股票数据获取：可以从公开数据源获取股票数据，包括股票价格、交易量、技术指标等。
- 股票选择：使用RPS指标进行优质股票的选择。
- 策略分析：支持多种常见的量化交易策略分析，例如er值、双均线、N日突破等。
- 交易决策：基于策略分析的结果，支持对股票进行交易决策，包括买入、卖出和持有等。
- 数据可视化：支持对股票数据和交易决策进行可视化展示，以便更好地理解和分析。

## 安装

### 1. 下载项目

你可以通过在命令行中运行以下命令来下载该项目：

```
git clone https://github.com/your_username/stock-trading-system.git
```

### 2. 安装依赖

在项目根目录下，运行以下命令安装依赖：

```
pip install -r requirements.txt
```

### 3.配置

在 **GetStockDataApi** 函数里配置 **token** 信息即可。

## 使用

你可以通过运行 Jupyter Notebook 文件来开始使用股票量化交易系统。其中包括了一些预设的策略和工具函数，例如指标选股、突破策略和数据可视化分析等内容。

### 数据获取

该系统支持从公开数据源tushare获取股票数据，只需注册一个账号即可。例如：

```
# 从 Tushare 获取 三六零 股票数据
import tushare as ts
token = ""      # your token
pro = ts.pro_api(token)  #初始化pro接口
stockdata = pro.daily(ts_code='601360.SH',start_date='20200101',end_date='20220101')
```



### 指标选股

本项目使用了 RPS（Relative Performance System）指标，这是一种用于选股和监测市场走势的技术分析工具。相比于传统的股票分析方法，RPS 指标能够更准确地评估股票表现，并找出市场中领头羊和落后者，为投资者提供更准确的股票选择和风险管理工具。

项目 RPS 指标选择的时间窗口和分组方法经过了精细的调整和优化，以确保其在实践中的有效性。项目使用 RPS 指标来筛选潜在的优质股票，并利用这些选股结果进行进一步的分析和交易决策。

```python
for index,row in stock_codes.iterrows():
    code = index
    name = row.证券简称
    df_stockload = stock_N_pct_change(stockCode=code,stockTimeS=yes_time,stockTimeE=now_time,N=N)
    N_pct_change = df_stockload[f"{N}day_pct_change"].rename(name)
    all_stock_N_pct_change = pd.concat([all_stock_N_pct_change,N_pct_change],join='outer',axis=1)
    
for column in df.columns:    # 添加RPS指标
    rps = (1-int(column)/4424)*100
    rps = round(rps,2)
    df[column] = df[column]+ "|" + str(rps)
```



### 策略分析

该系统支持多种常见的量化交易策略分析，例如：

```python
# N日突破
df = GetStockDataApi(stock_code,start_time,end_time)
df = NdaysSignal(df) 
strategy_name = "N日突破"
# 风险管理
df = NdaysStopSignal(df)
strategy_name = "带有风险管控的N日突破"
# 双均线
df = DoubleAverageSignal(df)
strategy_name = "双均线"
# 市场有效性比率
df = GetStockDataApi('600096.SH','20230101','20230314')
er = GetER(stockdata=df,N=15)
```



### 交易决策

该系统支持基于策略分析的交易决策，例如：

```python
# 基于 双均线 策略的交易决策
df = DoubleAverageSignal(df)
strategy_name = "双均线"
SimpleBackTest(df,strategy_name=strategy_name,stock_name=stock_name,cash_hold=cash_hold)
# 基于 N日突破 策略的交易决策
df = NdaysSignal(df) 
strategy_name = 'N日突破'
SimpleBackTest(df,strategy_name=strategy_name,stock_name=stock_name,cash_hold=cash_hold)
```



### 市场有效性比率

比率越高，市场走势清晰，用越短期限的均线MA5,MA15；反之，用长期限的均线,MA15,MA30。

```python
def GetER(stockdata,N=15):
    df = stockdata
    df = df.iloc[-N-1:-1,:]
    today = df.iloc[-1].close
    ago = df.iloc[0].close
    total_change = sum(abs(df.change))
    er = (today - ago)/total_change
    return er
```



### 股票诊股

独创的简易判断股票性质的方式：

```python
if profit_rate > 0.15 and win_rate >= 0.5:
    comment = "好"
else:
    comment = "一般"
good_counts = good_counts.count("好")
if good_counts > 1 :
    print(f"{stock_name}是一支好股票")
    
good_dict = {}                    #存储好股票
for key,value in need_code_dict.items():
    s = summery(value,key,'20230101',now,3000)  
    print('\n')
    if s == "Yes":  # 好股票
        good_dict[key] = value
```



### 股票总结

定义一个懒人必备的summery函数，总结股票的各项信息。

```python
in: summery('601360.SH','三六零','20230101',now,3000)

out:
    601360.SH 三六零 各策略回测结果(3000元基础)
    er值为:0.5216989843028623
    N日突破: 最终资金: 7964  策略胜率: 1.0  收益率: 1.65  评价: 好
    风险N日: 最终资金: 4983  策略胜率: 0.8  收益率: 0.66  评价: 好
    N双均线: 最终资金: 8100  策略胜率: 1.0  收益率: 1.7  评价: 好
    三六零是一支好股票
```



### 数据可视化 

该系统支持对股票数据和交易决策进行可视化展示，例如：

```python
# 通过上述调用不同的决策，将返回结果调用SimpleBackTest_info函数可输出回测结果并绘图
df1 = GetStockDataApi(stock_code,start_time,end_time)
df1_Nday = NdaysSignal(df1)
SimpleBackTest_info(df1_Nday,
                    strategy_name="N日突破",stock_name=stock_name,cash_hold=cash_hold)
```

```markdown
在 2023-01-03 以 11.57 价格--买入大华股份 200股
剩余资金:686
在 2023-02-20 以 13.82 价格--卖出大华股份 200股
剩余资金:3450
在 2023-03-01 以 15.87 价格--买入大华股份 200股
剩余资金:276
在 2023-03-08 以 15.43 价格--卖出大华股份 200股
剩余资金:3362
在 2023-03-14 以 17.7 价格--买入大华股份 100股
剩余资金:1592
在 2023-03-29 以 21.36 价格--卖出大华股份 100股
剩余资金:3728
大华股份 风险N日回测结果
风险N日: 最终资金: 3728 策略胜率0.67，收益率:0.24
```

![image-20230412154202566](C:\Users\13169\AppData\Roaming\Typora\typora-user-images\image-20230412154202566.png)

## 贡献

欢迎任何形式的贡献，包括提出问题、提出功能建议和提交代码等。如果你发现了任何问题或者有任何建议，请在 GitHub 上提出 Issue 或者发送 Pull Request。

## 授权

该项目使用 MIT 授权许可证，详情请参阅 LICENSE 文件。