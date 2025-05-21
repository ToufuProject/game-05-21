# pillowが必要
# pip install Pillow

from PIL import Image
import os

IMG_NAME = "ningen2025.png"
RESIZED_IMG_NAME = "resized_"+IMG_NAME

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "imgs")
IMG_PATH = os.path.join(IMG_DIR, IMG_NAME)
RESIZED_IMG_PATH = os.path.join(IMG_DIR, RESIZED_IMG_NAME)
# 変更したいサイズ
SIZE = (32, 32)

def resize_img(img_path, resize_img_path, size):
    with Image.open(img_path) as img:
        # リサイズされた画像(がぞう)を新しい変数(へんすう)に保存(ほぞん)
        resized_img = img.resize(size)
        # リサイズされた画像を保存
        resized_img.save(resize_img_path, "PNG")
        print("リサイズ完了！")

resize_img(img_path=IMG_PATH, resize_img_path=RESIZED_IMG_PATH, size=SIZE)
