import cv2
import numpy as np
import pytesseract
import os
os.environ['TESSDATA_PREFIX'] = r'D:\Program Files\Tesseract-OCR\tessdata'


def show(name):
    cv2.imshow('image', name)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def extract_hot_areas(image_path, temperature_threshold):
    # 读取热红外图像
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # 对图像进行阈值处理，提取高温区域
    _, hot_areas_mask = cv2.threshold(img, temperature_threshold,255, cv2.THRESH_BINARY)

    # 提取高温区域
    hot_areas = cv2.bitwise_and(img, img, mask=hot_areas_mask)

    return hot_areas

def process(path,filename,sn):
    # 读取图像
    image_path = path+filename

    hot_areas = extract_hot_areas(image_path,120)

    img = cv2.imread(image_path)
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    # show(hot_areas)
    
    # 创建一个与输入图像大小相同的空白图像
    mask = np.zeros_like(hot_areas)

    # 定义圆心和半径
    center = (609, 364)  # 圆心的x和y坐标
    radius =180 # 圆的半径

    # 在mask上画一个填充的白色圆
    cv2.circle(mask, center, radius, (255), thickness=-1)

    # 将输入图像和mask进行按位与操作，提取圆形区域
    output_image = cv2.bitwise_and(hot_areas, mask)
    _, hot_areas_mask = cv2.threshold(output_image, 205, 255, cv2.THRESH_BINARY)

    kernel = np.ones((3, 3), np.uint8)
    erosion = cv2.erode(hot_areas_mask, kernel, iterations=1)

    sure_bg = cv2.dilate(erosion, kernel, iterations=1)

    edges = cv2.Canny(sure_bg, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        filtered_contours.append(contour)

        #
    #2
    center = (655, 347)  # 圆心的x和y坐标
    radius = 265
    mask = np.zeros_like(hot_areas)

    height, width = hot_areas.shape[:2]
    start_row, start_col = int(height * 1/10), int(width * 1/10)
    end_row, end_col = int(height * 9/10), int(width * 9/10)

    # 在掩膜上绘制矩形
    cv2.rectangle(mask, (start_col, start_row+15), (end_col-200, end_row+100), (255), -1)


    masked_gray = cv2.bitwise_and(hot_areas, mask)

    cv2.circle(mask, center, radius, (255), thickness=-1)
    mask_inv = cv2.bitwise_not(mask)

    # 将输入图像和反转mask进行按位与操作，恢复圆外部区域的原始像素值
    outside_circle = cv2.bitwise_and(masked_gray, mask_inv)

    # 在原始图像上画一个填充的黑色圆，将圆圈变成黑色
    cv2.circle(masked_gray, center, radius, (0), thickness=-1)


    center_1 = (523, 338)  # 圆心的x和y坐标
    radius_1 = 185

    cv2.circle(mask, center_1, radius_1, (255), thickness=-1)
    mask_inv_1 = cv2.bitwise_not(mask)

    # 将输入图像和反转mask进行按位与操作，恢复圆外部区域的原始像素值
    outside_circle = cv2.bitwise_and(masked_gray, mask_inv_1)

    # 在原始图像上画一个填充的黑色圆，将圆圈变成黑色
    cv2.circle(masked_gray, center, radius, (0), thickness=-1)
    result = cv2.add(outside_circle, masked_gray)

    # 在原始图像上画一个填充的黑色圆，将圆圈变成黑色
    cv2.circle(result, center, radius, (0), thickness=-1)
    cv2.circle(result, center_1, radius_1, (0), thickness=-1)

    _, hot_areas_mask = cv2.threshold(result, 200, 240, cv2.THRESH_BINARY)

    erosion = cv2.erode(hot_areas_mask, kernel, iterations=2)

    sure_bg = cv2.dilate(erosion, kernel, iterations=1)

    edges = cv2.Canny(sure_bg, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        filtered_contours.append(contour)

        # 绘制边界矩形

    for contour in filtered_contours:

        x, y, w, h = cv2.boundingRect(contour)
        if w<6 or h<6:
            continue
        else:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)

    # show(img)

    cv2.imwrite("./processed_images/" + str(sn)+'.jpg',img)
    #3
    x, y, w, h = 1000, 90, 200, 80



        # 在图像上绘制矩形
    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

    cropped_img = image[y:y + h, x:x + w]

    _, hot_areas_mask = cv2.threshold(cropped_img, 170, 255, cv2.THRESH_BINARY)



    gray = cv2.medianBlur(hot_areas_mask , 3)

    thresholded_image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)[0]

    gray = cv2.medianBlur(gray , 3)



        # 显示图像

    config = '-c tessedit_char_whitelist=0123456789 --psm 6'

    # 使用Tesseract识别数字
    detected_numbers = pytesseract.image_to_string(gray, config=config)
    try:
        number = list(detected_numbers[0:3])
        a = "".join(map(str, number))
        print(f"{filename}  {int(a) / 10}°")
        return a
    except:
        print(f"{filename}  识别不出")
        return None


