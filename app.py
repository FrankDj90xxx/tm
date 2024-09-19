import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QWidget
from PyQt5.QtCore import Qt
from crawlers.taobao_crawler import crawl_taobao
from crawlers.xianyu_crawler import crawl_xianyu
# 如果需要，导入小红书和百度的爬虫逻辑


class CrawlerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('评论图片爬取器')
        self.setGeometry(100, 100, 400, 200)

        # 创建主窗口的小部件
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # 创建布局
        layout = QVBoxLayout()

        # 关键字输入框
        self.keywordInput = QLineEdit(self)
        self.keywordInput.setPlaceholderText("请输入关键字")
        layout.addWidget(self.keywordInput)

        # 平台选择框
        self.platformComboBox = QComboBox(self)
        self.platformComboBox.addItems(["淘宝", "闲鱼", "小红书", "百度"])
        layout.addWidget(self.platformComboBox)

        # 搜索按钮
        self.searchButton = QPushButton("开始爬取", self)
        layout.addWidget(self.searchButton)
        self.searchButton.clicked.connect(self.start_crawling)  # 连接按钮点击事件

        # 状态标签
        self.statusLabel = QLabel("状态: 等待输入", self)
        self.statusLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.statusLabel)

        # 设置布局
        self.central_widget.setLayout(layout)

    def start_crawling(self):
        # 获取输入的关键字和选择的平台
        keyword = self.keywordInput.text()
        platform = self.platformComboBox.currentText()

        # 根据选择的平台启动相应的爬虫
        if platform == '淘宝':
            img_urls = crawl_taobao(keyword)
        elif platform == '闲鱼':
            img_urls = crawl_xianyu(keyword)
        # 在这里添加小红书和百度的爬虫
        else:
            self.statusLabel.setText(f"未支持的平台：{platform}")
            return

        # 根据爬取结果更新状态
        if img_urls:
            self.statusLabel.setText(f"成功爬取 {len(img_urls)} 张图片")
            for url in img_urls:
                self.download_and_show_image(url)
        else:
            self.statusLabel.setText("没有找到相关图片")

    def download_and_show_image(self, url):
        import requests
        from PIL import Image
        from io import BytesIO
        import matplotlib.pyplot as plt

        response = requests.get(url)
        img = Image.open(BytesIO(response.content))

        # 显示图片
        plt.imshow(img)
        plt.axis('off')
        plt.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CrawlerApp()
    window.show()
    sys.exit(app.exec_())
