# 京东电商平台数据爬取和销售数据分析

## 项目描述

本项目使用Python和Selenium对京东电商平台进行数据爬取，包括用户信息、购物记录和评价等，共计3万条数据。然后使用Python和Pandas库对销售数据进行数据清洗，包括数据缺失值处理、异常值检测，确保数据质量和准确性。接着，运用Tableau创建仪表盘，通过图表和交互式报告展示销售趋势、销售额、客户地域分布等业务指标辅助决策。最后进行销售数据的深度分析，包括趋势分析、词云统计以及市场地位的评估，为业务决策提供定量的支持和建议。

## 项目功能

- 爬取京东电商平台数据，包括用户信息、购物记录和评价等，共计3万条数据
- 使用Python和Pandas库对销售数据进行数据清洗，包括数据缺失值处理、异常值检测，确保数据质量和准确性
- 运用Tableau创建仪表盘，通过图表和交互式报告展示销售趋势、销售额、客户地域分布等业务指标辅助决策
- 进行销售数据的深度分析，包括趋势分析、词云统计以及市场地位的评估，为业务决策提供定量的支持和建议

## 项目结构

```lua
|-- data/
|   |-- 销售详情表.csv
|   |-- 评论详情表.csv
|-- analysis/
|   |-- 数据预处理.ipynb
|-- dashboard/
|   |-- 京东电商数据分析.twbx
|-- spiders/
|   |-- jd_spider.py
|-- README.md
```

- `data/`: 存储爬取的数据文件
- `analysis/`: 存储数据清洗的Jupyter Notebook
- `dashboard/`: 存储Tableau仪表盘文件
- `spiders/`: 存储数据爬取脚本
- `README.md`: 项目介绍文件

## 安装说明

- 安装Python3
- 安装必要的Python库: Selenium, Pandas
- 安装Tableau软件

## 使用说明

1. 运行`jd_spider.py`文件进行数据爬取。
2. 运行`数据预处理.ipynb`文件进行销售数据清洗。
3. 打开Tableau软件，导入`京东电商数据分析.twbx`文件，查看销售仪表盘

## 参考资料

- [Python官方网站](https://www.python.org/)
- [Selenium官方文档](https://www.selenium.dev/documentation/en/)
- [Pandas官方网站](https://pandas.pydata.org/)
- [商业智能和分析软件](https://www.tableau.com/zh-cn)

