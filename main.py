import sys
sys.path.append(r"D:\Document\Desktop\IDTMS")

from image_processing import process
import os

if __name__ == '__main__':
    path=r'D:\Document\Desktop\IDTMS\1511602118787317762\\'
    # picture_filename='1663603666880.jpg'
    i=0
    for filename in os.listdir(path):
            # image_path=path+picture_filename
            tempreture = process(path,filename,i)
            if tempreture!=None:
                # TODO 存入数据库
                pass
            else:
                # TODO 读取数据库的数据
                pass
            i+=1
