# 使用 Python 3.12 的基础镜像
FROM python:3.12

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 文件到容器中
COPY requirements.txt /app/

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制当前目录内容到容器中
COPY . /app/
CMD ["/bin/bash"]