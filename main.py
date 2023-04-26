import sys
sys.path.append(r"D:\PythonProj\IDTMS")

from image_processing import process
import os

if __name__ == '__main__':
    path=r'D:\PythonProj\IDTMS\1511602118787317762\\'
    # picture_filename='1663603666880.jpg'

    for filename in os.listdir(path):
            # image_path=path+picture_filename
            tempreture = process(path,filename)
            if tempreture!=None:
                # TODO 存入数据库
                pass
            else:
                # TODO 读取数据库的数据
                pass

