from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import requests
import os
from sqlalchemy import create_engine, Column, Integer, String, SmallInteger
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import pickle

import random
# 创建数据库模型
Base = declarative_base()


class TMImg(Base):
    __tablename__ = 'tm_img'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    url = Column(String(255))
    filename = Column(String(255))
    state = Column(SmallInteger, nullable=False,
                   default=0)  # 0=下载, 1=下载完成, 2=下载失败


# 连接数据库
engine = create_engine('mysql+pymysql://root:123456@localhost:3306/tm_db')
Session = sessionmaker(bind=engine)
session = Session()
# 保存 Cookies 到文件


def save_cookies(driver, path):
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)

# 从文件加载 Cookies


def load_cookies(driver, path):
    with open(path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)
# 检查是否已经登录


def is_logged_in(driver):
    try:
        driver.find_element(By.CLASS_NAME, "site-nav-user")
        return True
    except:
        return False


def wait_for_login(driver):
    print("请用手机扫码登录淘宝...")
    while True:
        try:
            driver.find_element(By.CLASS_NAME, "site-nav-user")
            print("登录成功!")
            break
        except:
            time.sleep(2)
            print("等待扫码登录...")


# 淘宝登录并等待用户扫码
def login_taobao(driver):
    driver.get("https://login.taobao.com/member/login.jhtml")
    time.sleep(3)

    try:
        qr_login_switch = driver.find_element(By.CLASS_NAME, "icon-qrcode")
        qr_login_switch.click()
        print("切换到二维码登录页面...")
    except Exception:
        print("二维码登录页面加载失败，可能已经在扫码页面")

    print("请用手机扫码登录淘宝...")
    while not is_logged_in(driver):
        time.sleep(2)
        print("等待扫码登录...")

    save_cookies(driver, "taobao_cookies.pkl")  # 登录后保存Cookies


def handle_slider_verification(driver):
    print("检测到滑块验证，请手动完成...")
    while True:
        try:
            # 你可以检查某个元素是否消失，例如滑块验证框
            driver.find_element(
                By.XPATH, '//div[contains(@class, "J_MIDDLEWARE_FRAME_WIDGET")]')
            time.sleep(5)
            print("等待手动完成滑块验证...")
        except:
            print("滑块验证完成，继续操作...")
            break

# 爬取淘宝评论图片


def crawl_taobao(keyword):

    # 创建 ChromeOptions 对象
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--headless")  # 如果需要无头模式
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1920x1080")  # 设置窗口大小

    # 初始化 WebDriver，使用 ChromeDriverManager
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    # # 初始化 WebDriver
    # driver = uc.Chrome(options=options)
    # 加载Cookies，尝试保持登录状态
    driver.get("https://www.taobao.com/")
    try:
        load_cookies(driver, "taobao_cookies.pkl")
        driver.refresh()
        time.sleep(3)
    except FileNotFoundError:

        login_taobao(driver)

    # 如果没有登录，执行扫码登录
    if not is_logged_in(driver):
        login_taobao(driver)

    # 登录后搜索关键字
    driver.get(f'https://s.taobao.com/search?q={keyword}')
    time.sleep(random.uniform(10, 20))

    # 循环抓取每一页
    while True:
        # 模拟下拉加载更多商品
        # scroll_and_load_more(driver)

        # 获取商品列表
        product_links = []
        products = driver.find_elements(
            By.XPATH, '//div[contains(@class, "contentInner--")]//a')

        for product in products:
            link = product.get_attribute('href')

            if link and "https://detail.tmall.com/item.htm" in link:  # 只跳转到包含 tmall 的链接
                product_links.append(link)

        # 依次进入每个商品详情页
        for link in product_links:
            driver.get(link)
            time.sleep(10)
       # 检测是否出现滑块验证
            if len(driver.find_elements(By.XPATH, '//div[contains(@class, "J_MIDDLEWARE_FRAME_WIDGET")]')) > 0:
                handle_slider_verification(driver)  # 调用处理滑块验证的函数
            # 这里判断当前商品详情页面的链接  如果是 https://chaoshi.detail.tmall.com/ 就 新写一个 scroll_to_chaoshi_reviews方法
            current_url = driver.current_url
            if "https://chaoshi.detail.tmall.com/" in current_url:
                scroll_to_chaoshi_reviews(driver)  # 调用超市商品的滚动方法
            else:

                scroll_to_reviews(driver)  # 调用普通商品的滚动方法

            # 抓取评价区域的图片
            try:
                images = driver.find_elements(
                    By.XPATH, '//div[contains(@class, "album--")]//img')
                # images = driver.find_elements(
                #     By.XPATH, '//div[contains(@class, "photo--") or contains(@class, "cover--")]//img')
                [download_image(img.get_attribute('src'), keyword)
                 for img in images]
            except Exception as e:
                print(f"抓取图片失败: {str(e)}")

        # 检查是否有下一页，如果有则点击下一页
           # 检查是否有下一页，如果有则点击下一页
        if not go_to_next_page(driver):
            break  # 如果没有下一页，结束抓取

    driver.quit()

# 点击下一页按钮


def go_to_next_page(driver):
    try:
        # 查找“下一页”按钮
        next_page_button = driver.find_element(
            By.XPATH, '//button[contains(@class, "next-btn") and contains(@aria-label, "下一页")]')
        next_page_button.click()  # 点击“下一页”按钮
        print("已找到下一页按钮，点击继续抓取...")
        time.sleep(3)  # 等待页面加载
        return True  # 成功翻页
    except Exception as e:
        print("没有找到下一页按钮，结束抓取。")
        return False  # 没有下一页


# 模拟下拉直到找到“用户评价”

def scroll_to_chaoshi_reviews(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        try:
            # 查找并点击“宝贝评价”标签
            review_tab = driver.find_element(
                By.XPATH, '//div[contains(@class, "Tabs--title--") and contains(., "宝贝评价")]')
            review_tab.click()
            time.sleep(3)
            break
        except Exception as e:
            # 获取当前页面高度
            current_height = driver.execute_script(
                "return document.body.scrollHeight")

            # 判断是否到底部
            if current_height == last_height:
                print("已滑动到底部，未找到宝贝评价标签，返回商品列表...")
                break  # 如果到达页面底部，跳出循环

            # 否则继续滚动
            driver.execute_script("window.scrollBy(0, 500);")
            last_height = current_height
            time.sleep(2)
            print("继续滚动，寻找宝贝评价标签...")


def scroll_to_reviews(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        try:
            # 尝试找到“用户评价”按钮
            review_button = driver.find_element(
                By.XPATH, '//div[contains(@class, "tabTitleItem--") and contains(.,"用户评价")]//span')
            review_button.click()
            time.sleep(3)  # 等待页面滚动到评价区域
            break  # 找到并点击后退出循环
        except Exception as e:
            # 获取当前页面高度
            current_height = driver.execute_script(
                "return document.body.scrollHeight")

            # 判断是否到底部
            if current_height == last_height:
                print("已滑动到底部，未找到用户评价按钮，返回商品列表...")
                break  # 如果到达页面底部，跳出循环

            # 否则继续滚动
            driver.execute_script("window.scrollBy(0, 500);")
            last_height = current_height
            time.sleep(2)
            print("继续滚动，寻找用户评价按钮...")


# 模拟下拉加载更多商品
def scroll_and_load_more(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 等待页面加载
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # 页面已经到底，停止滚动
        last_height = new_height


# 下载图片并保存到指定目录
def download_image(url, keyword):

    if "2-tps-2-2" in url:
        return True
    if "2-tps-145-145.png" in url:
        return True
    if "alicdn" in url:

        save_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), '..', '淘宝图片')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        if url.startswith('//'):
            url = 'https:' + url
        existing_img = session.query(TMImg).filter_by(url=url).first()
        if existing_img:

            return True
        img_record = TMImg(name=f'淘宝-{keyword}', url=url, state=0)  # 初始状态为下载中

        session.add(img_record)
        session.commit()
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
                'Accept': 'application/octet-stream',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()  # 如果请求失败，抛出异常
            img_record.filename = os.path.basename(url)
            if response.status_code == 200:
                filename = os.path.join(save_dir, url.split("/")[-1])
                with open(filename, 'wb') as f:
                    f.write(response.content)

                img_record.state = 1
            else:
                img_record.state = 2  # 设置为下载失败
        except Exception as e:
            img_record.state = 2  # 设置为下载失败
        session.commit()
        return True


# 主函数，执行爬取操作
if __name__ == "__main__":
    keyword = "羽毛球球袋"

    crawl_taobao(keyword)
