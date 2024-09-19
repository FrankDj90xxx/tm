import os
import requests
from sqlalchemy import create_engine, Column, Integer, String, SmallInteger
from sqlalchemy.orm import sessionmaker, declarative_base


Base = declarative_base()

# 定义模型


class Img(Base):
    __tablename__ = 'tm_img'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    url = Column(String(255))
    filename = Column(String(255))
    state = Column(SmallInteger)


# 创建数据库引擎
engine = create_engine('mysql+pymysql://root:123456@localhost:3306/tm_db')
Session = sessionmaker(bind=engine)
session = Session()

# 查询所有 state 为 0 的记录
images = session.query(Img).all()

for image in images:
    name = image.name
    url = image.url

    # 创建目录
    if not os.path.exists(name):
        os.makedirs(name)

    # 下载文件
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
            'Accept': 'application/octet-stream',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果请求失败，抛出异常
        file_name = os.path.basename(url)  # 从 URL 中提取文件名
        # 保存文件到指定目录
        file_path = os.path.join(name, file_name)
        with open(file_path, 'wb') as file:
            file.write(response.content)

        # 更新 state 为 1
        image.state = 1
        image.filename = file_name
        session.commit()
        print(f"下载并保存 {file_name} 到 {name}，状态更新为 1")

    except Exception as e:
        print(f"下载 {url} 失败: {e}")

# 关闭会话
session.close()
