



import os
import cv2
from PIL import Image
import numpy as np  # 确保导入 numpy

def convert_images_to_jpg(input_directory, output_directory):
    # 创建输出目录（如果不存在）
    os.makedirs(output_directory, exist_ok=True)

    # 获取目录下的所有文件
    for filename in os.listdir(input_directory):
        # 构建文件路径
        file_path = os.path.join(input_directory, filename)
        
        # 检查是否为文件
        if os.path.isfile(file_path):
            # 尝试读取图像
            try:
                # 使用 Pillow 打开图片
                with Image.open(file_path) as img:
                    # 将 Pillow 图像转换为 RGB
                    img = img.convert("RGB")
                    opencv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

                    # 获取文件名（不带扩展名）
                    name, _ = os.path.splitext(filename)  # 去掉扩展名
                    name = name.split(".jpg")[0]  # 去掉 .jpg 及后面的内容
                    # 新的文件路径，替换扩展名为 .jpg
                    new_file_path = os.path.join(output_directory, f"{name}.jpg")
                    # 保存为 JPG 格式
                    cv2.imwrite(new_file_path, opencv_image)
               
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
        else:
            print(f"{file_path} is not a valid file.")

# 使用示例
input_directory = r"淘宝-羽毛球拍子"  # 替换为你的源目录路径
output_directory = r"cvimg"      # 替换为你的目标目录路径
convert_images_to_jpg(input_directory, output_directory)

