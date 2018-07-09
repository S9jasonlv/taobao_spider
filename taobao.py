from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
from pyquery import PyQuery as pq

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)
KEYWORD = '小米8'
MAX_PAGE = 100

def get_products():
    '''
    抓取商品详细
    :return:
    '''
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
        print(product)


def index_page(page):
    '''
    抓取索引页
    :param page: 页码
    :return:
    '''
    print('正在爬取第', page, '页')
    try:
        url = 'https://s.taobao.com/search?q=' + quote(KEYWORD)
        print(url)
        browser.get(url)
        if page > 1:
            input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager div.form > input'))
            )
            submit = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager div.form > span.J_Submit'))
            )
            input.clear()
            input.send_keys(page)
            submit.click()

        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager li.item.active > span'), str(page))
        )
        wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.m-itemlist .items .item'))
        )
        get_products()
    except TimeoutException:
        print('TIMEOUT')
        index_page(page)


def main():
    for page in range(1, MAX_PAGE + 1):
        index_page(page)

if __name__ == '__main__':
    main()