import cv2
import numpy as np
import pytesseract
import os
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
from Mysql_Setting import db
cur = db.cursor()
Images = 'Images'
m = '设备1'
def show(name):
    cv2.imshow('image', name)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def extract_hot_areas(image_path, temperature_threshold):
    # 读取热红外图像
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # 对图像进行阈值处理，提取高温区域
    _, hot_areas_mask = cv2.threshold(img, temperature_threshold,255, cv2.THRESH_BINARY)

    # 按位与运算，提取高温区域
    hot_areas = cv2.bitwise_and(img, img, mask=hot_areas_mask)

    return hot_areas

def process(path,filename):
    # 读取图像
    image_path = path+filename

    hot_areas = extract_hot_areas(image_path,120)

    img = cv2.imread(image_path)
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    # show(hot_areas)
    
    # 创建一个与输入图像大小相同的空白图像
    mask = np.zeros_like(hot_areas)

# 提取圆形区域的特征信息
    # 定义圆心和半径
    center = (609, 364)  # 圆心的x和y坐标
    radius =180 # 圆的半径

    # 在mask上画一个填充的白色圆
    cv2.circle(mask, center, radius, (255), thickness=-1)

    # 将输入图像和mask进行按位与操作，提取圆形区域
    output_image = cv2.bitwise_and(hot_areas, mask)
    # 对结果图像进行阈值处理，得到二值图像
    _, hot_areas_mask = cv2.threshold(output_image, 205, 255, cv2.THRESH_BINARY)

    #确定卷积核大小3x3，对图像进行腐蚀、膨胀、边缘检测、查找轮廓操作
    kernel = np.ones((3, 3), np.uint8)
    # 减小粗细
    erosion = cv2.erode(hot_areas_mask, kernel, iterations=1)
    # 增强连通性
    sure_bg = cv2.dilate(erosion, kernel, iterations=1)
    # 边缘检测
    edges = cv2.Canny(sure_bg, 50, 150)
    # 使用findContours查找图像中的轮廓，并将轮廓保存到filtered_contours列表中
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        filtered_contours.append(contour)


#2 提取圆形外部的特征信息
    center = (655, 347)  # 圆心的x和y坐标
    radius = 265
    # 创建一个空白图像掩膜，与hot_areas的大小相同。
    mask = np.zeros_like(hot_areas)
    # 对hot_areas进行切片，得到高度和宽度
    height, width = hot_areas.shape[:2]
    # 指定起始行、起始列、结束行和结束列来定义矩形的位置和大小。
    start_row, start_col = int(height * 1/10), int(width * 1/10)
    end_row, end_col = int(height * 9/10), int(width * 9/10)

    # 在掩膜上绘制矩形
    cv2.rectangle(mask, (start_col, start_row+15), (end_col-200, end_row+100), (255), -1)
    # 使用按位与将掩膜应用于输入图像，提取矩形区域内的像素值。
    masked_gray = cv2.bitwise_and(hot_areas, mask)

    cv2.circle(mask, center, radius, (255), thickness=-1)
    # 创建一个反转的掩膜，通过对原始掩膜取反得到。
    mask_inv = cv2.bitwise_not(mask)

    # 将输入图像和反转mask进行按位与操作，恢复圆外部区域的原始像素值
    outside_circle = cv2.bitwise_and(masked_gray, mask_inv)

    # 在原始图像上画一个填充圆，将圆变成黑色
    cv2.circle(masked_gray, center, radius, (0), thickness=-1)

    # 重复上述步骤，对另一个圆形区域进行相同的操作
    center_1 = (523, 338)  # 另一个圆心的x和y坐标
    radius_1 = 185

    cv2.circle(mask, center_1, radius_1, (255), thickness=-1)
    mask_inv_1 = cv2.bitwise_not(mask)

    # 将输入图像和反转mask进行按位与操作，恢复圆外部区域的原始像素值
    outside_circle = cv2.bitwise_and(masked_gray, mask_inv_1)

    # 在原始图像上画再一个填充圆，将圆变成黑色
    cv2.circle(masked_gray, center, radius, (0), thickness=-1)
    # 将两个圆形区域之外的图像部分与处理后的圆形区域进行组合，得到最终结果
    result = cv2.add(outside_circle, masked_gray)

    # 在原始图像上画一个填充圆，将圆变成黑色
    cv2.circle(result, center, radius, (0), thickness=-1)
    cv2.circle(result, center_1, radius_1, (0), thickness=-1)

    _, hot_areas_mask = cv2.threshold(result, 200, 240, cv2.THRESH_BINARY)
    # 对图像进行腐蚀、膨胀、边缘检测、查找轮廓操作
    # 减小粗细
    erosion = cv2.erode(hot_areas_mask, kernel, iterations=2)
    # 增强连通性
    sure_bg = cv2.dilate(erosion, kernel, iterations=1)
    # 边缘检测
    edges = cv2.Canny(sure_bg, 50, 150)
    # 使用findContours查找图像中的轮廓，并将轮廓保存到filtered_contours列表中
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        filtered_contours.append(contour)

    # 绘制边界矩形
    for contour in filtered_contours:

        x, y, w, h = cv2.boundingRect(contour) #xy坐标、wh大小
        if w<6 or h<6:
            continue
        else:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), 2) #绘制黑色边界矩形

    # show(img) # 显示图像

    cv2.imwrite("./processed_images/" + filename,img)

#3 文字识别预处理
    x, y, w, h = 1000, 90, 200, 80

    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

    cropped_img = image[y:y + h, x:x + w]

    _, hot_areas_mask = cv2.threshold(cropped_img, 170, 255, cv2.THRESH_BINARY)

    gray = cv2.medianBlur(hot_areas_mask , 3)

    # thresholded_image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)[0]

    gray = cv2.medianBlur(gray , 3)




    config = '-c tessedit_char_whitelist=0123456789 --psm 6'

    # 使用Tesseract识别数字
    detected_numbers = pytesseract.image_to_string(gray, config=config)
    try:
        number = list(detected_numbers[0:3])
        a = "".join(map(str, number))
        t = int(a) / 10
        print(f"{filename}  {int(a) / 10}°")
        if t > 35:
            status = '高温警告'
        else:
            status = '正常'
        # 向images数据表中插入语句
        insert_sql = f"INSERT INTO {Images}(iname,temp,dvcid,status) VALUES ('%s','%s','%s','%s')" % (filename, t, m, status)
        cur.execute(insert_sql)
        db.commit()
        return a
    except:
        t = '识别不出'
        print(f"{filename}  识别不出")
        insert_sql = f"INSERT INTO {Images}(iname,temp,dvcid) VALUES ('%s','%s','%s')" % (filename, t, m)
        cur.execute(insert_sql)
        db.commit()
        return None


