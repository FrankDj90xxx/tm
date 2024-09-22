from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import requests
import os
import random
from sqlalchemy import create_engine, Column, Integer, String, SmallInteger
from sqlalchemy.orm import declarative_base, sessionmaker
from selenium.webdriver.common.keys import Keys
import pickle
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 创建数据库模型
Base = declarative_base()


class TMImg(Base):
    __tablename__ = "tm_img"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    url = Column(String(255))
    filename = Column(String(255))
    state = Column(
        SmallInteger, nullable=False, default=0
    )  # 0=下载, 1=下载完成, 2=下载失败


# 连接数据库
engine = create_engine("mysql+pymysql://root:123456@localhost:3306/tm_db")
Session = sessionmaker(bind=engine)
session = Session()


# 设置随机的 User-Agent
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
]


# 创建 ChromeOptions 对象
options = webdriver.ChromeOptions()

options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)
options.add_argument("--disable-extensions")

options.add_argument("--disable-usb")
options.add_argument("--disable-webrtc")
options.add_experimental_option(
    "excludeSwitches", ["enable-automation", "enable-logging"]
)
options.add_experimental_option("useAutomationExtension", False)

# 初始化 WebDriver，使用 ChromeDriverManager
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)


# 随机等待时间
def random_wait(min_sec=1, max_sec=5):
    time.sleep(random.uniform(min_sec, max_sec))


# 等待扫码登录
def wait_for_login():
    print("请用扫码登录...")
    while True:

        try:
            el = driver.find_element(By.XPATH, '//*[@id="ttbar-login"]/div[1]/a')
            if el:

                print("登录成功")

                break
        except:
            random_wait(2, 5)
            print("等待扫码登录...")


# 处理滑块验证
def handle_slider_verification():
    print("检测到滑块验证，请手动完成...")
    while True:
        try:
            driver.find_element(
                By.XPATH, '//div[contains(@class, "J_MIDDLEWARE_FRAME_WIDGET")]'
            )
            random_wait(5, 10)
            print("等待手动完成滑块验证...")
        except:
            print("滑块验证完成，继续操作...")
            break


# 保存 Cookies 到文件
def save_cookies(path):
    with open(path, "wb") as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)


# 从文件加载 Cookies
def load_cookies(path):
    with open(path, "rb") as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)


# 检查是否已经登录
def is_logged_in():
    try:
        driver.find_element(By.XPATH, '//*[@id="ttbar-login"]/div[1]/a')
        return True
    except:
        return False


# 淘宝登录并等待用户扫码
def login_jd():
    goTo("https://passport.jd.com/uc/login")
    wait_for_login()
    save_cookies("jd_cookies.pkl")  # 登录后保存Cookies


def goTo(url):
    driver.get(url)
    random_wait(1, 5)
    driver.execute_script(
        "Object.defineProperty(window, 'outerWidth', { get: () => window.innerWidth });"
    )
    driver.execute_script(
        "Object.defineProperty(window, 'outerHeight', { get: () => window.innerHeight });"
    )


# 下载图片并保存到指定目录
def download_image(url, keyword):

    save_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", f"京东-{keyword}"
    )
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    existing_img = session.query(TMImg).filter_by(url=url).first()
    if existing_img:

        return True
    img_record = TMImg(name=f"京东-{keyword}", url=url, state=0)  # 初始状态为下载中

    session.add(img_record)
    session.commit()
    try:
        headers = {
          
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/octet-stream",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }
        print(url)
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果请求失败，抛出异常
        img_record.filename = os.path.basename(url)
        print(os.path.basename(url))
        if response.status_code == 200:
            filename = os.path.join(save_dir, img_record.filename)
            with open(filename, "wb") as f:
                f.write(response.content)

            img_record.state = 1
        else:
            img_record.state = 2  # 设置为下载失败
    except Exception as e:
        img_record.state = 2  # 设置为下载失败
    session.commit()
    return True


def getImgs(link, keyword):

    link.click()
    random_wait(1, 3)
    # 获取当前所有窗口句柄
    all_windows = driver.window_handles

    # 获取当前窗口的句柄
    current_window = driver.current_window_handle

    # 找到新打开的窗口（假设新窗口在最后一个）
    for window in all_windows:
        if window != current_window:
            # 切换到新窗口

            driver.switch_to.window(window)

            break
        
    random_wait(10, 20)

    try:
       
        
            # //*[@id="comment-0"]/div[1]/div[2]/div[2]/a[1]/img
            # //*[@id="comment-0"]/div[8]/div[2]/div[2]/a[1]/img
            # //*[@id="comment-0"]/div[5]/div[2]/div[2]/a[1]/img
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//a[@class="J-thumb-img"]/img',
                    )
                )
            )

            imgs = driver.find_elements(
                By.XPATH,
                '//a[@class="J-thumb-img"]/img',
            )
       
            for img in imgs:
                download_image(img.get_attribute("src"), keyword)

            # while True:
            #     try:
            #         WebDriverWait(driver, random.randint(1, 10)).until(
            #             EC.presence_of_element_located(
            #                 (
            #                     By.XPATH,
            #                     '//*[contains(@id, "comment-")]/div[1]/div[2]/div[2]/a[1]/img',
            #                 )
            #             )
            #         )

            #         imgs = driver.find_elements(
            #             By.XPATH,
            #             '//*[contains(@id, "comment-")]/div[1]/div[2]/div[2]/a[1]/img',
            #         )

            #         for img in imgs:
            #             imglst.append(img.get_attribute("src"))

            #         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            #         driver.find_elements(
            #             By.XPATH,
            #             '//*[contains(@id, "comment-")]/div[12]/div/div/a[8]',
            #         ).click()
            #     except:
            #         break
    except:
        pass

    # 关闭新窗口并切回原窗口
    driver.close()  # 关闭当前新窗口
    random_wait(1, 5)
    driver.switch_to.window(current_window)  # 切换回原窗口


def scroll_to_bottom(scroll_pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # 滚动页面
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 等待页面加载
        time.sleep(scroll_pause_time)

        # 获取新的页面高度
        new_height = driver.execute_script("return document.body.scrollHeight")

        # 如果新的高度与上一次高度相同，说明已经到达页面底部，停止滚动
        if new_height == last_height:
            print("已滚动到页面底部")
            break

        # 更新最后的页面高度
        last_height = new_height


def crawl_jd(keyword):

    goTo("https://www.jd.com/")

    try:
        load_cookies("jd_cookies.pkl")
        driver.refresh()
        time.sleep(3)
    except FileNotFoundError:

        login_jd()

    if not is_logged_in():
        login_jd()

    # 等待搜索输入框和按钮加载
    driver.find_element(By.XPATH, '//*[@id="key"]').send_keys(keyword)
    random_wait(1, 2)
    driver.find_element(By.XPATH, '//*[@id="key"]').send_keys(Keys.RETURN)

    random_wait(1, 5)

    goodlst = driver.find_elements(
        By.XPATH, '//*[contains(@id, "warecard_")]/div[5]/strong'
    )
    for good in goodlst:
        try:
            getImgs(good, keyword)

        except:
            continue

    random_wait(3600, 7200)
    driver.quit()


# 主函数
if __name__ == "__main__":
    keyword = "红双喜羽毛球球拍"
    crawl_jd(keyword)
    # 使用代理列表
