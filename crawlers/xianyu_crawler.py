from selenium import webdriver
from selenium.webdriver.common.by import By
import time


def crawl_xianyu(keyword):
    driver = webdriver.Chrome()
    driver.get(f'https://s.2.taobao.com/list/?q={keyword}')
    time.sleep(3)

    # 打开第一个商品详情页
    first_item = driver.find_element(By.XPATH, '//a[@class="item-pic"]')
    first_item.click()
    time.sleep(3)

    # 切换到新窗口
    driver.switch_to.window(driver.window_handles[1])

    # 抓取评论图片
    images = driver.find_elements(
        By.XPATH, '//div[@class="item-reviews"]//img')
    img_urls = [img.get_attribute('src') for img in images]

    driver.quit()
    return img_urls
