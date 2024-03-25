import ui.ui1
import ui.ui2
import ui.ui3
import ui.ui4
import ui.ui5
import ui.login_resgister
import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer, Qt, QRect,QTimer, QDateTime
from PyQt5.QtGui import QPixmap
import datetime
import os
import numpy as np
import shutil
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from Mysql_Setting import db
cur = db.cursor()
User = 'User'
Images = 'Images'
# 获取当前文件所在的目录路径
dir_path = os.path.dirname(os.path.abspath(__file__))

file_name = ['1511602118787317762', '1511602118854426626', '1511602118934118402']
dvcid_name = ['设备1', '设备2',     '设备3']
product_num = 3 #设备数

'''注册登录界面'''
class winlogin(ui.login_resgister.Ui_MainWindow, QMainWindow):
    def __init__(self):
        super(winlogin, self).__init__()
        self.setupUi(self)
        '''界面居中显示'''
        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        newLeft = (screen.width() - size.width()) / 2
        newTop = (screen.height() - size.height()) / 2
        '''将信号连接到槽'''
        self.frame_r.setVisible(0)
        self.move(int(newLeft), int(newTop))
        # 登录
        self.btn_login.clicked.connect(self.login_)
        # 注册
        try:
            self.btn_register.clicked.disconnect()  # 尝试断开之前的连接
            self.btn_ok.clicked.disconnect()  # 尝试断开之前的连接
        except TypeError:
            pass  # 如果连接不存在，就不进行断开
        # 注册
        self.btn_register.clicked.connect(self.register_)
        self.btn_ok.clicked.connect(self.register_ok)
        # 显示密码
        self.passwordshow.clicked.connect(self.passwordshow_clicked)

    # 显示密码事件
    def passwordshow_clicked(self):
        # 如果显示密码按钮被选中否则不显示密码
        if self.passwordshow.isChecked():
            self.lineEdit_password.setEchoMode(QLineEdit.Normal)
        else:
            self.lineEdit_password.setEchoMode(QLineEdit.Password)
    # 登录事件
    def login_(self):
        self.frame_r.setVisible(0)
        self.frame_login.setVisible(1)
        user_name = self.lineEdit_user.text()
        user_password = self.lineEdit_password.text()
        # 执行SQL语句，从User数据表中查询username和password字段值
        cur.execute(f"SELECT username,password FROM {User}")
        # 将数据库查询的结果保存在result中
        result = cur.fetchall()
        name_list = [it[0] for it in result]  # 从数据库查询的result中遍历查询元组中第一个元素name
        # 判断用户名或密码不能为空
        if not (user_name and user_password):
            QMessageBox.critical(self, "错误", "用户名或密码不能为空！")
            # 判断用户名和密码是否匹配
        elif user_name in name_list:
            if user_password == result[name_list.index(user_name)][1]:
                # QMessageBox.information(self, "欢迎您", "登录成功！\n在此添加新界面！")
                self.ui = winui1(username=user_name)
                self.ui.show()
                self.close()
            else:
                QMessageBox.critical(self, "错误", "密码输入错误！")
        # 账号不在数据库中，则弹出是否注册的框
        else:
            QMessageBox.critical(self, "错误", "该账号不存在，请注册！")
    # 注册事件
    def register_(self):
        self.frame_r.setVisible(1)
        self.frame_login.setVisible(0)
        self.lineEdit_r_user.clear()
        self.lineEdit_r_password.clear()
        self.lineEdit_phone.clear()
    def register_ok(self):
        name = self.lineEdit_r_user.text()
        password = self.lineEdit_r_password.text()
        phone =self.lineEdit_phone.text()
        # 向user数据表中插入语句
        insert_sql = f"INSERT INTO {User}(username,password,phone) VALUES ('%s','%s','%s')" % (name, password,phone)
        # 读取user数据表中的username和password字段值
        read_sql = f'''select * from {User} where username = "{name}"'''
        user_data = cur.execute(read_sql)
        # 判断注册账号和密码
        if user_data.real:
            QMessageBox.critical(self, "警告", "该注册账号已存在！请检查")
        else:
            cur.execute(insert_sql)
            db.commit()
            QMessageBox.information(self, "欢迎您", "注册成功！")
            self.frame_r.setVisible(0)
            self.frame_login.setVisible(1)
            self.lineEdit_r_user.clear()
            self.lineEdit_r_password.clear()
            self.lineEdit_phone.clear()
'''主界面'''
class winui1(ui.ui1.Ui_MainWindow, QMainWindow):
    def __init__(self,username):
        super(winui1, self).__init__()
        self.setupUi(self)
        self.username = username
        self.label_user.setText(self.username)
        '''界面居中显示'''
        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        newLeft = (screen.width() - size.width()) / 2
        newTop = (screen.height() - size.height()) / 2
        self.move(int(newLeft), int(newTop))
        self.file_index = 0
        self.file_process = file_name[self.file_index]#文件名

        self.start_time = datetime.datetime.now()

        self.images_orl = []  # 用于保存所有图片的列表
        self.images_pro = []  # 用于保存所有图片的列表
        self.imageFiles_orl = []  # 新增代码，用来保存图片文件名
        self.imageIndex_orl = 0  # 当前显示的图片的索引
        self.imageIndex_pro = 0  # 当前显示的图片的索引
        self.timer_orl = QTimer(self)
        self.timer_orl.timeout.connect(self.displayNextImage_orl)

        self.timer_pro = QTimer(self)
        self.timer_pro.timeout.connect(self.displayNextImage_pro)
        # self.loadImages_pro()  # 加载所有图片

        # 创建定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_time)
        self.timer.start(1000)
        self.run()
    def run(self):
        self.btn_start.clicked.connect(self.img_start_show)
        self.btn_stop.clicked.connect(self.img_stop_show)
        self.btn_winshow.clicked.connect(self.slot_btn_winshow)
        self.btn_select.clicked.connect(self.slot_btn_winshow)
        self.btn_last.clicked.connect(self.slot_btn_last)
        self.btn_next.clicked.connect(self.slot_btn_next)

        self.action_phone.triggered.connect(self.phone_alt)
        self.action_password.triggered.connect(self.password_alt)
        self.action_altuser.triggered.connect(self.winloginshow)
        self.action_userdel.triggered.connect(self.user_del)
        self.action_back.triggered.connect(self.winclose)

        self.btn_load_img.clicked.connect(self.open_folder_dialog)
        self.btn_save.clicked.connect(self.img_save)
        self.btn_help.clicked.connect(self.winhelp)
    #退出
    def winclose(self):
        self.close()
    # 帮助窗口显示
    def winhelp(self):
        self.helpui =winui5()
        self.helpui.show()
    #图片保存
    def img_save(self):
        try:
            file_path_name = os.path.join(dir_path, 'processed_images', self.filename)
            # 定义目标复制路径及新的文件名
            file_path, _ = QFileDialog.getSaveFileName(self, "保存图片", file_path_name,
                                                       "Images (*.png *.xpm *.jpg)")

            # 复制文件
            shutil.copy(file_path_name, file_path)
            QMessageBox.information(self, "提示", "图片保存成功！")
        except:
            QMessageBox.critical(self, "错误", "未开始检测无法保存图片！")
    #打开文件夹
    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", "/")
        if folder_path:
            folder_name = os.path.basename(folder_path)
            self.file_process = folder_name
            # print("打开的文件夹是：", folder_name)
    #用户删除
    def user_del(self):
        cur.execute(f"DELETE FROM {User} WHERE username=%s", (self.username,))
        db.commit()
        QMessageBox.information(self, "提示", "账号已注销！")
        self.ui = winlogin()
        self.ui.show()
        self.close()
    #切换用户
    def winloginshow(self):
        self.ui = winlogin()
        self.ui.show()
        self.close()
    #用户密码修改
    def password_alt(self):
        self.passwordui = winui3(username=self.username)
        self.passwordui.show()
    #用户手机修改
    def phone_alt(self):
        self.phoneui = winui4(username=self.username)
        self.phoneui.show()
    #切换上一个设备
    def slot_btn_last(self):
        self.img_stop_show()
        self.file_index -= 1
        if self.file_index < 0:
            self.file_index = len(file_name) - 1
        self.file_process = file_name[self.file_index]
        self.img_start_show()
    #切换下一个设备
    def slot_btn_next(self):
        self.img_stop_show()
        self.file_index += 1
        if self.file_index >= len(file_name):
            self.file_index = 0
        self.file_process = file_name[self.file_index]
        self.img_start_show()
    #开始检测，播放图片
    def img_start_show(self):#开始按钮
        self.start_time = datetime.datetime.now()
        self.loadImages_orl()  # 加载所有图片
        # 通过定时器，每隔两秒切换到下一张照片
        self.timer_pro.start(2000)
        self.timer_orl.start(2000)
    #温度曲线和查询界面显示
    def slot_btn_winshow(self):
        self.ui = winui2(username=self.username)
        self.ui.show()
        self.close()
    '''以下为图片循环相关函数'''
    def img_stop_show(self):
        # 停止定时器
        self.timer_pro.stop()
        self.timer_orl.stop()
        self.images_orl = []  # 用于保存所有图片的列表
        self.images_pro = []  # 用于保存所有图片的列表
        self.imageFiles_orl = []  # 新增代码，用来保存图片文件名
        self.imageIndex_orl = 0  # 当前显示的图片的索引
        self.imageIndex_pro = 0  # 当前显示的图片的索引
        # 清空标签
        self.label_pro.clear()
        self.label_orl.clear()
        self.label_pro.setText('处理后的图像')
        self.label_orl.setText('原图')
        self.label_name_pro.setText('')
        self.label_name_orl.setText('')
        self.label_temp.setText('')
        self.label_status.setText('')
        self.label_time.setText('')
    def loadImage_pro(self, path):
        # print(path)
        # 使用QPixmap实例加载单张图片
        pixmap_pro = QPixmap(path).scaled(self.label_pro.width(), self.label_pro.height())
        self.images_pro.append(pixmap_pro)

    def displayNextImage_pro(self):
        # 显示下一张图片
        self.imageIndex_pro += 1
        if self.imageIndex_pro == len(self.images_pro):
            self.imageIndex_pro = 0

        pixmap = self.images_pro[self.imageIndex_pro]
        self.label_pro.setPixmap(pixmap)

        # 重新调整标签以使其适合所显示的图片大小
        self.label_pro.setGeometry(QRect(50, 50, pixmap.width(), pixmap.height()))

        # 告诉QT重绘标签widget
        self.label_pro.update()

    def loadImage_orl(self, path):
        # 使用QPixmap实例加载单张图片
        pixmap = QPixmap(path).scaled(self.label_orl.width(), self.label_orl.height())
        self.images_orl.append(pixmap)
        self.imageFiles_orl.append(os.path.basename(path))  # 新增代码，获取文件名并保存到列表中

    def loadImages_orl(self):
        # 获取指定目录下的所有文件
        file_path_orl = os.path.join(dir_path, self.file_process)
        file_path_pro = os.path.join(dir_path, 'processed_images')
        files = os.listdir(file_path_orl)
        # files = sorted(files)
        # print(files)
        for file in files:
            # 如果素有文件不是图片，跳过
            if not file.endswith('.jpg') and not file.endswith('.png') and not file.endswith('.gif'):
                continue
            path = os.path.join(file_path_orl, file)
            # print(path)
            path_pro = os.path.join(file_path_pro, file)
            self.loadImage_orl(path)
            self.loadImage_pro(path_pro)
        # 更新显示的图像

        self.label_orl.setPixmap(QPixmap(self.images_orl[self.imageIndex_orl]))
        self.label_pro.setPixmap(QPixmap(self.images_pro[self.imageIndex_orl]))

    def displayNextImage_orl(self):
        # 显示下一张图片
        self.imageIndex_orl += 1
        if self.imageIndex_orl == len(self.images_orl):
            self.imageIndex_orl = 0
        pixmap = self.images_orl[self.imageIndex_orl]
        self.filename = self.imageFiles_orl[self.imageIndex_orl]  # 获取当前展示的图片的文件名
        print("当前识别的图片文件名为：", self.filename)
        cur.execute(f"SELECT temp,status,dvcid FROM {Images} where iname ='{self.filename}'")
        # 将数据库查询的结果保存在result中
        result = cur.fetchone()
        temp  = result[0]
        status = result[1]
        dvcid = result[2]
        self.label_temp.setText(f'{temp}°')
        self.label_name_orl.setText(f'设备号：{dvcid}')
        self.label_name_pro.setText(f'设备号：{dvcid}')
        self.label_status.setText(status)
        end_time = datetime.datetime.now()
        pro_time = end_time-self.start_time
        self.label_time.setText(str(pro_time))
        self.label_orl.setPixmap(pixmap)
        # 重新调整标签以使其适合所显示的图片大小
        self.label_orl.setGeometry(QRect(50, 50, pixmap.width(), pixmap.height()))
        # 告诉QT重绘标签widget
        self.label_orl.update()
    #系统时间显示
    def show_time(self):
        # 获取当前时间
        current_time = QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')
        # 设置标签文本
        self.label_stystem_time.setText(current_time)

'''温度曲线和查询界面'''
class winui2(ui.ui2.Ui_MainWindow, QMainWindow):
    def __init__(self,username):
        super(winui2, self).__init__()
        self.setupUi(self)
        self.username = username
        self.label_user.setText(self.username)
        '''界面居中显示'''
        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        newLeft = (screen.width() - size.width()) / 2
        newTop = (screen.height() - size.height()) / 2
        self.move(int(newLeft), int(newTop))

        self.dvcid_index = 0
        self.dvcid = dvcid_name[self.dvcid_index]

        # 创建定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_time)
        self.timer.start(1000)
        self.run()
    def run(self):
        self.btn_back.clicked.connect(self.winback)
        self.btn_select.clicked.connect(self.data_sel)
        self.btn_save.clicked.connect(self.data_save)
        self.action_phone.triggered.connect(self.phone_alt)
        self.action_password.triggered.connect(self.password_alt)
        self.action_altuser.triggered.connect(self.winloginshow)
        self.action_userdel.triggered.connect(self.user_del)
        self.btn_last.clicked.connect(self.last_dvcid)
        self.btn_next.clicked.connect(self.next_dvcid)
        self.draw_img()
    #用户删除
    def user_del(self):
        cur.execute(f"DELETE FROM {User} WHERE username=%s", (self.username,))
        db.commit()
        QMessageBox.information(self, "提示", "账号已注销！")
        self.ui = winlogin()
        self.ui.show()
        self.close()
    #切换用户
    def winloginshow(self):
        self.ui = winlogin()
        self.ui.show()
        self.close()
    #密码修改
    def password_alt(self):
        self.passwordui = winui3(username=self.username)
        self.passwordui.show()
    #手机号修改
    def phone_alt(self):
        self.phoneui = winui4(username=self.username)
        self.phoneui.show()
    #数据保存
    def data_save(self):
        dvcid = self.comboBox.currentText()
        date = self.comboBox_date.currentText()
        time = self.lineEdit_time.text()
        staus = self.comboBox_staus.currentText()
        file_name = f"{dvcid}{date}{time}{staus}.txt"
        directory = "data"  # 存储文件的目录名
        if not os.path.exists(directory):  # 如果目录不存在，则创建目录
            os.mkdir(directory)
        file_path = os.path.join(dir_path,directory, file_name)  # 获取文件的完整路径

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"设备号：{dvcid}\n日期：{date}\n时间：{time}\n状态：{staus}\n查询信息：\n")  # 应该在这一行之后加上所需文字
            for row in range(self.tableWidget.rowCount()):
                for col in range(self.tableWidget.columnCount()):
                    item = self.tableWidget.item(row, col)
                    if item is not None:
                        f.write(item.text() + "\t")
                    else:
                        f.write("\t")
                f.write("\n")
        QMessageBox.information(self, "提示", '数据保存成功！')
        print("Data saved to txt file.")
    #上一个设备
    def next_dvcid(self):
        self.label_img.clear()
        self.dvcid_index += 1
        if self.dvcid_index >= len(dvcid_name):
            self.dvcid_index = 0
        self.dvcid = dvcid_name[self.dvcid_index]
        self.draw_img()
    #下一个设备
    def last_dvcid(self):
        self.label_img.clear()
        self.dvcid_index -= 1
        if self.dvcid_index < 0:
            self.dvcid_index = len(dvcid_name) - 1
        self.dvcid = dvcid_name[self.dvcid_index]
        self.draw_img()
    #绘制图像
    def draw_img(self):
        self.label_img.setText('')
        # 指定字体
        font = FontProperties(fname='./simkai.ttf', size=14)
        temp_list = []  # 创建一个空列表来存储temp值
        date_list = []  # 创建一个空列表来存储temp值
        sql_dvcid = f"SELECT date,time,temp FROM {Images} WHERE dvcid = '{self.dvcid}'"
        cur.execute(sql_dvcid)
        row_dvcid = cur.fetchall()
        for r in row_dvcid:
            date = f"{r[0]} {r[1]}"
            temp_list.append(r[2])  # 将每个行中的temp值添加到temp_list中
            date_list.append(date)  # 将每个行中的temp值添加到temp_list中

        # 按温度从低到高排序
        temp_list = temp_list[::-1]

        save_directory = "images"  # 存储图像的目录名
        if not os.path.exists(save_directory):  # 如果目录不存在，则创建目录
            os.makedirs(save_directory)
        save_path = os.path.join(save_directory, f"{self.dvcid}.png")  # 获取文件的完整路径
        self.label_dvcid.setText(self.dvcid)

        fig = plt.figure(dpi=64,figsize=(10,6))

        plt.plot(date_list, temp_list, linewidth=2)
        #图名，x轴、y轴名称
        plt.xlabel('日期和时间', fontproperties=font)
        plt.ylabel('温度', fontproperties=font)
        plt.title(self.dvcid + '温度变化曲线', fontproperties=font)
        # 绘制折线图
        plt.yticks(range(0, len(temp_list), 2))
        plt.xticks(range(0, len(date_list), 5))
        fig.autofmt_xdate()

        # 配置图形
        plt.savefig(save_path)
        plt.close()
        save_path = save_path.replace('\\', '/')  # 将反斜杠换为正斜杠
        self.label_img.setStyleSheet(f"border-image: url({save_path})")
    #数据查询
    def data_sel(self):#数据查询
        self.label_img.setText('')
        dvcid = self.comboBox.currentText()
        date = self.comboBox_date.currentText()
        time = self.lineEdit_time.text()
        staus = self.comboBox_staus.currentText()
        # 创建一个 SQL 查询语句的基础模板
        sql = f"SELECT dvcid, date, time, temp, status FROM {Images} WHERE dvcid = '{dvcid}'"
        if staus:
            sql += f" AND status = '{staus}'"
        if date:
            sql += f" AND date = '{date}'"
        if time:
            sql += f" AND time = '{time}'"
        cur.execute(sql)
        rows = cur.fetchall()
        self.tableWidget.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)#居中对齐
                self.tableWidget.setItem(i, j, item)
    #界面返回
    def winback(self):
        self.ui = winui1(self.username)
        self.ui.show()
        self.close()
    #显示系统时间
    def show_time(self):
        # 获取当前时间
        current_time = QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')
        # 设置标签文本
        self.label_time.setText(current_time)
'''密码修改界面'''
class winui3(ui.ui3.Ui_MainWindow, QMainWindow):
    def __init__(self,username):
        super(winui3, self).__init__()
        self.setupUi(self)
        self.username = username
        '''界面居中显示'''
        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        newLeft = (screen.width() - size.width()) / 2
        newTop = (screen.height() - size.height()) / 2
        self.move(int(newLeft), int(newTop))
        self.btn_ok.clicked.connect(self.password_alt)
    def password_alt(self):
        old_password = self.lineEdit_password_old.text()
        new_password = self.lineEdit_password_new.text()
        new_password_confirm = self.lineEdit_password_newconfirm.text()
        cur.execute(f"SELECT password FROM {User} where username = '{self.username}'")
        # 将数据库查询的结果保存在result中
        password_user = cur.fetchone()
        if old_password ==password_user[0]:
            if new_password == new_password_confirm:
                update_sql = f"update {User} set  password = '{new_password}' where username = '{self.username} '"
                cur.execute(update_sql)
                db.commit()
                self.lineEdit_password_old.clear()
                self.lineEdit_password_new.clear()
                self.lineEdit_password_newconfirm.clear()
                QMessageBox.information(self, "提示", "密码修改成功")
                self.close()

            else:
                QMessageBox.critical(self,"错误","两次输入密码不相同")
        else:
            QMessageBox.critical(self, "错误", "输入的原密码不正确")
'''手机号修改界面'''
class winui4(ui.ui4.Ui_MainWindow, QMainWindow):
    def __init__(self,username):
        super(winui4, self).__init__()
        self.setupUi(self)
        self.username = username
        '''界面居中显示'''
        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        newLeft = (screen.width() - size.width()) / 2
        newTop = (screen.height() - size.height()) / 2
        self.move(int(newLeft), int(newTop))
        self.btn_ok.clicked.connect(self.phone_alt)

    def phone_alt(self):
        old_phone = self.lineEdit_phone_old.text()
        new_phone = self.lineEdit_phone_new.text()
        cur.execute(f"SELECT phone FROM {User} where username = '{self.username}'")
        # 将数据库查询的结果保存在result中
        phone_user = cur.fetchone()
        if old_phone == phone_user[0]:
            update_sql = f"update {User} set  phone = {new_phone} where username = '{self.username} '"
            cur.execute(update_sql)
            db.commit()
            self.lineEdit_phone_old.clear()
            self.lineEdit_phone_new.clear()
            QMessageBox.information(self, "提示", "手机修改成功")
            self.close()
        else:
            QMessageBox.critical(self, "错误", "输入的原手机不正确")
'''帮助窗口界面'''
class winui5(ui.ui5.Ui_MainWindow, QMainWindow):
    def __init__(self):
        super(winui5, self).__init__()
        self.setupUi(self)
        '''界面居中显示'''
        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        newLeft = (screen.width() - size.width()) / 2
        newTop = (screen.height() - size.height()) / 2
        self.move(int(newLeft), int(newTop))
        img_path  = os.path.join(dir_path, 'images','工业设备温度监测系统.png')#图片路径
        img_path = img_path.replace('\\', '/')  # 将反斜杠换为正斜杠
        self.frame.setStyleSheet(f"border-image: url({img_path})")
def main():
    '''防止界面变形'''
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    Ui = winlogin()
    Ui.show()  # 将第一和窗口换个名字显示出
    sys.exit(app.exec_())  # app.exet_()是指程序一直循环运行直到主窗口被关闭终止进程


if __name__ == '__main__':
    main()





# import sys
# sys.path.append(r"D:\PythonProj\IDTMS")
#
# from image_processing import process
# import os
#
# if __name__ == '__main__':
#     path=r'D:\PythonProj\IDTMS\1511602118787317762\\'
#     # picture_filename='1663603666880.jpg'
#
#     for filename in os.listdir(path):
#             # image_path=path+picture_filename
#             tempreture = process(path,filename)
#             if tempreture!=None:
#                 # TODO 存入数据库
#                 pass
#             else:
#                 # TODO 读取数据库的数据
#                 pass

