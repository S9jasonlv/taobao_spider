# config:
 1. MONGO_URL = 文件中存储mongodb的url
 2. MONGO_DB = mongodb的库名
 3. MONGO_TABLE = MongoDB的表名
 4. SERVICE_ARGS = phantomJS所需配置
     ### --load-images=false 配置phantomJS不加载页面图片
     ### --disk-cache=true 开启本地硬盘缓存

# spider逻辑:
## def search()
    1、请求淘宝首页 ，并定位到input标签和搜索按钮；
    2、在input框中输入欲查找的关键字；
    3、触发click事件，模拟点击页面的“搜索”按钮；
    4、调用分析item标签属性的函数
    5、定位到商品列表页面下发的总页数并返回；

## def next_page()
    1、定位页码输入框；
    2、定位页码旁的确定按钮；
    3、清空页面输入框的内容，并输入新的页码；
    4、触发click时间，模拟点击页码旁的确定按钮；
    5、判断页码active标签的text值是否与page_number一致；
    6、调用分析item标签属性的函数


## def get_products()
    1、定位item标签，并校验item标签是否加载成功；
    2、pyquery语法查找到所有item标签；
    3、循环取出所有item标签下的商品名称、价格、商店名、所属地、图片链接；

## def save_to_mongo()
    1、判断插入mongodb是否成功
    2、打印调试信息

## def main()
    1、调用search()方法
    2、取出total总页码数
    3、循环页码数，将页码传递给next_page()方法


```python
hello python!
```
