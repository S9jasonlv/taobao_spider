import time
import re
import pymongo
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
from pyquery import PyQuery as pq
from config import *

# 谷歌无界面模式，不再打开浏览器
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')

browser = webdriver.PhantomJS(service_args = SERVICE_ARGS)
wait = WebDriverWait(browser, 10)   # 显示等待，验证元素是否加载成功，已加载向下执行，未加载等待10秒，超过10秒抛出超时异常
browser.set_window_size(1400, 900)

KEYWORD = '上衣'  # 搜索关键字
MAX_PAGE = 100

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
print(db)

def search():
    '''
    登录首页，并根据KEYWORD跳转搜索结果页面
    :return: 返回搜索结果总页数
    '''
    try:
        print('正在搜索')
        browser.get('https://www.taobao.com')
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#q'))
        )   # 以显式方式等待，验证元素加载是否通过；参数用于定位到搜索框（#q）的位置
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button'))
        )   # 以显式方式等待，验证元素加载是否通过；参数用于定位到搜索按钮的位置
        input.send_keys(KEYWORD)
        submit.click()
        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total'))
        )   # 定位到第一页下面的总页数标签
        get_products()
        return total.text
    except TimeoutException:
        print('timeout')
        return search()

def next_page(page_number):
    print('正在翻页', page_number)
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input'))
        )   # 定位到页码输入input框
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit'))
        )   # 定位页码旁的确认按钮
        input.clear()   # 清空页码输入框的内容
        input.send_keys(page_number)    # 输入页码
        submit.click()  # 模拟点击按钮
        wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number))
        )   # 判断页码active标签的text值是否与page_number一致
        get_products()  # 调用分析item标签的函数

    except TimeoutException:
        print('next page timeout')
        next_page(page_number)

def get_products():
    '''
    抓取商品详细
    :return:
    '''
    wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.m-itemlist .items .item'))
    )   # 定位item标签，并校验item标签是否加载成功
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'img_url': item.find('.pic-box .pic .img').attr('data-src'),
            'price': item.find('.price').text().replace('\n',''),
            'deal': item.find('.deal-cnt').text(),
            'title': item.find('.title').text().replace('\n',''),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        if product['title']:
            save_to_mongo(product)  # 调用保存到mongodb数据的函数

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储到MongoDB成功：', result)
    except Exception as e:
        print('存储到MongoDB失败：', result)
        print(e)

def main():
    try:
        total = search()
        total = int(re.compile('(\d+)').search(total).group(1))
        for i in range(2, total + 1):
            next_page(i)
    except Exception as e:
        print(e)
    finally:
        browser.close()
if __name__ == '__main__':
    main()