import os
import cv2
from PIL import Image

def is_image_without_people(image_path):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    image = cv2.imread(image_path)
    
    if image is None:  # 检查图像是否读取成功
        print(f"无法读取图像: {image_path}")
        return False  # 如果无法读取，可以视为无人的图片

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    return len(faces) == 0

def process_images(input_dir, output_dir):
 
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):  # 添加 webp 支持
            image_path = os.path.join(input_dir, filename)
            if not os.path.isfile(image_path):  # 检查文件存在性
                print(f"文件不存在: {image_path}")
                continue

            if is_image_without_people(image_path):
                output_path = os.path.join(output_dir, filename)
                Image.open(image_path).save(output_path)
                print(f"保存无人的图片: {output_path}")

input_directory = "cvimg"  # 替换为你的目录路径
output_directory = "无人的图片"  # 输出目录
process_images(input_directory, output_directory)
