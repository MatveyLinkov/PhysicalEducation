import sys
import os
import csv
import sqlite3
from random import sample

from PyQt5 import QtMultimedia
from PyQt5.QtCore import Qt, QRect, QUrl
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QColorDialog, QTextBrowser
from PyQt5.QtWidgets import QButtonGroup
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QGridLayout


class Menu(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(872, 611)
        self.setWindowTitle('Pixel Art: Physical education')
        self.setWindowIcon(QIcon('icon.ico'))
        self.library = QWidget(self)                                # Создание виджета библиотеки
        self.load_mp3('sounds/click.mp3')                           # Загрузка звука для кнопок
        self.pixmap_menu = QPixmap('images/menu.png')               # Присваивание изображений
        self.pixmap_library = QPixmap('images/menu_library_on.png')                 # для меню
        self.pixmap_my_works = QPixmap('images/menu_my_works_on.png')
        self.pixmap_new_work = QPixmap('images/menu_new_work_on.png')
        self.pixmap_logo = QPixmap('images/head.png')
        self.pixmap_trashbox = QPixmap('images/trashbox.png')

        con = sqlite3.connect('arts.sqlite')                        # Подключение библиотеки Arts
        self.cur = con.cursor()

        self.pixelArtsWidget = QWidget(self.library)                # Создание pixelArtsLayout для
        self.pixelArtsWidget.setGeometry(4, 85, 865, 440)           # размещения изображений
        self.pixelArtsLayout = QGridLayout(self.pixelArtsWidget)
        self.index = 0
        for i in range(2):                                          # Добавление изобрежений
            for j in range(4):                                      # в Layout
                icon = self.cur.execute(
                    f'SELECT icon_library '
                    f'FROM Arts WHERE id = {self.index}').fetchall()[0][0]
                pixel_art = QLabel(self.pixelArtsWidget)
                pixmap_art = QPixmap(icon)
                pixel_art.setPixmap(pixmap_art)
                self.pixelArtsLayout.addWidget(pixel_art, i, j, 1, 1)
                self.index += 1

        self.myWorks = QWidget(self)                    # Создание виджета мои работы
        self.data = open('id.dat').readline()                # Открытие файла, содержащего
        self.data = self.data.split(' ')                          # айди выполненных работ
        if self.data != ['']:
            self.data = self.data[1:]
        self.length_works = len(self.data)
        if len(self.data) > 4:
            self.length_works = 4
        self.width_works = (len(self.data) - 1) // 4 + 1
        size_x, size_y = 216, 220                       # Определение размеров будущего worksLayout
        if self.length_works == 1:
            size_x = 226
        if self.width_works == 1:
            size_y = 230
        # Создание worksLayout, содержащего миниатюры выполненных работ
        self.worksWidget = QWidget(self.myWorks)
        self.worksWidget.setGeometry(4, 85,
                                     size_x * self.length_works + 1, size_y * self.width_works)
        self.worksLayout = QGridLayout(self.worksWidget)
        index = 0
        if self.data != ['']:
            for i in range(self.width_works):           # Добавление изображений в Layout
                for j in range(self.length_works):
                    icon = self.cur.execute(
                        f'SELECT icon_works '
                        f'FROM Arts WHERE id = {int(self.data[index])}').fetchall()[0][0]
                    pixel_art = QLabel(self.worksWidget)
                    pixmap_art = QPixmap(icon)
                    pixel_art.setPixmap(pixmap_art)
                    self.worksLayout.addWidget(pixel_art, i, j, 1, 1)
                    index += 1
                    if index >= len(self.data):
                        break
        self.myWorks.hide()

        self.newWork = QWidget(self)                    # Создание виджета новая работа
        self.soon = QLabel('Comming soon!', self.newWork)
        self.soon.setGeometry(300, 260, 271, 41)
        font = QFont()
        font.setFamily("Yu Gothic Light")
        font.setPointSize(28)
        self.soon.setFont(font)

        self.newWork.hide()
        self.newWork.setDisabled(True)

        self.logotype = QLabel(self)                        # Создание шапки меню
        self.logotype.setGeometry(0, -1, 872, 59)
        self.logotype.setPixmap(self.pixmap_logo)

        self.nameWindow = QLabel('Library', self)           # Наименование вкладки в меню
        self.nameWindow.setGeometry(QRect(0, 3, 872, 55))
        self.nameWindow.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setFamily("Yu Gothic Light")
        font.setPointSize(28)
        self.nameWindow.setFont(font)

        self.menu = QLabel(self)                            # Создание нижних меток/кнопок
        self.menu.resize(872, 71)
        self.menu.move(0, 549)
        self.menu.setPixmap(self.pixmap_menu)
        self.mouse_move = False

        font.setPointSize(24)
        self.delete_button = QPushButton('🗑', self)
        self.delete_button.setGeometry(820, 10, 40, 40)
        self.delete_button.setFont(font)
        self.delete_button.clicked.connect(self.delete_message)

    def delete_message(self):
        delete = QMessageBox()
        delete.setIcon(QMessageBox.Warning)
        delete.setWindowTitle('Удаление')
        delete.setText('Вы действительно хотите удалить все сохранения?')
        delete.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
        delete.buttonClicked.connect(self.delete_saves)
        delete.exec()

    def delete_saves(self, btn):
        os.chdir('saves')
        if btn.text() == 'OK':
            for filename in os.listdir():
                os.remove(filename)
        os.chdir('../')
        if btn.text() == 'OK':
            with open('id.dat', 'w') as identifier:
                identifier.close()
            self.worksWidget.hide()

    def mousePressEvent(self, event):
        self.first_click = (event.x(), event.y())       # Получение изначальных координат курсора
        self.first_position = event.y()
        self.arts_y = self.pixelArtsWidget.y()          # Получение изначальных координат виджетов
        self.works_y = self.worksWidget.y()
        if event.button() == Qt.LeftButton:             # Определение нажатия левой кнопки мыши
            self.leftClick = True
            if 57 <= event.y() <= 555:                  # Определение курсора в рабочей области
                self.mouse_move = True
            else:
                self.mouse_move = False
        else:
            self.leftClick = False
        if event.y() >= 556:    # Условие для изменения стиля нижних кнопок
            if event.x() <= 436:
                self.menu.setPixmap(self.pixmap_library)
            elif 436 < event.x():
                self.menu.setPixmap(self.pixmap_my_works)
        else:
            self.menu.setPixmap(self.pixmap_menu)

    def mouseMoveEvent(self, event):
        if event.y() >= 556:    # Условие для изменения стиля нижних кнопок
            if self.first_click[0] <= 436 and event.x() <= 436:
                self.menu.setPixmap(self.pixmap_library)
            elif 436 < self.first_click[0] and 436 < event.x():
                self.menu.setPixmap(self.pixmap_my_works)
            else:
                self.menu.setPixmap(self.pixmap_menu)
        else:
            self.menu.setPixmap(self.pixmap_menu)

    def mouseReleaseEvent(self, event):
        if self.leftClick:
            # Присваивание конечных координат курсора
            mouse_x, mouse_y = event.x() - 6, event.y() - self.pixelArtsWidget.y()
            for i in range(self.index):     # Открытие определенного пиксель арта
                fl = False
                art = self.pixelArtsLayout.itemAt(i).widget()
                if self.worksLayout.itemAt(i) != None:
                    work_art = self.worksLayout.itemAt(i).widget()
                    fl = True
                if self.pixelArtsWidget.isVisible() and \
                        art.x() - 3 <= mouse_x <= art.x() + 202 and \
                        art.y() - 3 <= mouse_y <= art.y() + 202 and 60 <= event.y() <= 554 and \
                        event.y() == self.first_click[1]:
                    if i < 24:
                        filename = self.cur.execute(
                            f'SELECT pattern FROM Arts WHERE id = {i}').fetchall()[0][0]
                    else:
                        filename = '\\'.join(QFileDialog.getOpenFileName(
                            self, 'Выбрать пиксель арт', '', 'Пиксель арт (*.csv)')[0].split('/'))
                    try:
                        self.game = Game(i, filename)   # Открытие нового окна
                        self.game.show()
                        self.hide()
                        self.player.play()
                    except Exception:
                        print('ok')
                    #    pass
                if self.worksWidget.isVisible() and fl and\
                        work_art.x() - 3 <= mouse_x <= work_art.x() + 202 and \
                        work_art.y() - 3 <= mouse_y <= art.y() + 202 and 60 <= event.y() <= 554 and\
                        event.y() == self.first_click[1]:
                    self.player.play()
                    self.info = Info(self.data[i])
                    self.info.show()
            # Условие для активации нижних кнопок
            if self.first_click[1] >= 556 and event.y() >= 556 and \
                    (self.first_click[0] <= 436 and event.x() <= 436 or
                     436 < self.first_click[0] and 436 < event.x()):
                self.library.hide()
                self.library.setDisabled(True)
                self.myWorks.hide()
                self.myWorks.setDisabled(True)
                self.player.play()
                # Открытие определенных виджетов и изменение названия в шапке
                if self.first_click[0] <= 436 and event.x() <= 436:
                    self.library.show()
                    self.library.setEnabled(True)
                    self.nameWindow.setText('Library')
                else:
                    self.myWorks.show()
                    self.myWorks.setEnabled(True)
                    self.nameWindow.setText('My Works')
            self.menu.setPixmap(self.pixmap_menu)   # Присваивание изначального стиля кнопок

    def load(self):     # Загрузка холста по указанным значениям
        # Ограничение для указания размеров холста
        if self.lenBox.value() / 2 <= self.widBox.value():
            self.colors = [''] * self.colorBox.value()
            for pixel in self.pixels.buttons():
                if int(pixel.objectName().split()[0]) >= self.widBox.value() or \
                        int(pixel.objectName().split()[1]) >= self.lenBox.value():
                    pixel.setDisabled(True)                 # Сборос стиля пикселей
                    pixel.setStyleSheet(
                        "background-color: {}".format(''))
                    pixel.setText('0')
                else:
                    pixel.setDisabled(False)    # Активация пикселей для получения цвета и номера
                pixel.setText('0')
            for color_btn in self.color_buttons.buttons():
                if int(color_btn.objectName().split()[1]) > self.colorBox.value():
                    color_btn.setDisabled(True)
                else:
                    # Активация кнопок для определения цвета и номера
                    if color_btn.objectName().split()[0] != '0' or \
                            color_btn.objectName().split()[1] != '0':
                        color_btn.setDisabled(False)
            self.status.setText('')
        else:
            self.status.setText('Невозможно задать параметры')

    def clear(self):    # Очищение парамметров
        self.lenBox.setValue(0)
        self.widBox.setValue(0)
        self.colorBox.setValue(0)
        for pixel in self.pixels.buttons():
            pixel.setDisabled(True)
            pixel.setText('0')
            pixel.setStyleSheet(
                "background-color: {}".format(''))
        for color_btn in self.color_buttons.buttons():
            color_btn.setDisabled(True)
            if color_btn.objectName().split()[0] == '0':
                color_btn.setStyleSheet(
                    "background-color: {}".format(''))

    def save(self):     # Сохранение холста в csv файл
        # Определение имени файла
        file_name = QFileDialog.getSaveFileName(self.newWork, "Save File", '/', '.csv')
        short_name = (file_name[0] + file_name[1]).split('/')[-1]
        names = open('names.dat').readline()
        names = names.split()
        if file_name != ('', '') and short_name not in names:
            with open(file_name[0] + file_name[1], 'w', encoding='utf-8', newline='') as pattern:
                writer = csv.writer(
                    pattern, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                # Запись размеров и количества цветов
                writer.writerow([self.lenBox.value(), self.widBox.value(), self.colorBox.value()])
                for i in range(self.widBox.value()):
                    # Запись положения пикселей и их номера
                    writer.writerow([f'{pixel.objectName()} {pixel.text()}'
                                     for pixel in self.pixels.buttons() if pixel.isEnabled() and
                                     int(pixel.objectName().split()[0]) == i])
                writer.writerow(f'{color_btn.objectName().split()[1]}'
                                f' {color_btn.styleSheet().split()[1]}'
                                for color_btn in self.color_buttons.buttons() if
                                0 < int(color_btn.objectName().split()[1]) <= self.colorBox.value()
                                and color_btn.objectName().split()[0] == '0')   # Запись цветов
                names.append(short_name)
                # Добавление имени файлаа к списку имен
                with open('names.dat', 'w', encoding='utf=8') as record_names:
                    record_names.write(' '.join(names))
            self.status.setText('')
        else:
            self.status.setText('Файл не сохранен, т.к. имя уже занято')

    def change_value(self):     # Изменение номера и цвета пикселя
        color_num = ''.join([btn.text() for btn in self.color_buttons.buttons() if btn.isChecked()])
        if color_num != '':
            self.sender().setStyleSheet(
                "background-color: {}".format(self.colors[int(color_num) - 1]))
        else:
            self.sender().setStyleSheet(
               "background-color: {}".format(''))
            color_num = '0'
        self.sender().setText(color_num)

    def change_color(self):     # Назначение цвета для определенного номера
        color = QColorDialog.getColor()
        if color.isValid():
            self.sender().setStyleSheet(
                "background-color: {}".format(color.name()))
        self.colors[int(self.sender().objectName().split()[1]) - 1] = color.name()

    def load_mp3(self, filename):   # Загрузка звука
        media = QUrl.fromLocalFile(filename)
        content = QtMultimedia.QMediaContent(media)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setMedia(content)


class Game(QWidget):
    def __init__(self, index, filename):
        super().__init__()
        self.initUI(index, filename)

    def initUI(self, index, filename):
        self.setObjectName("Pixel Art")
        self.setWindowTitle('Pixel Art: Physical education')        # Определение загаловка окна
        self.setWindowIcon(QIcon('icon.ico'))
        self.setFixedSize(872, 611)             # и его размеров
        self.load_mp3('sounds/click.mp3')       # Загрузка звука для кнопок
        self.id, self.filename = str(index), filename                    # Присваивание айди
        self.color_pixel = 0, ''                # Присваивание цвета

        self.save_name = 'saves/save_' + filename.split('\\')[-1]   # Определение имени сохранения
        with open(filename, 'r', encoding='utf-8') as pattern:      # Открытие паттерна пиксель арта
            pattern = list(csv.reader(pattern, delimiter=';', quotechar='"'))
            self.settings = [int(elem) for elem in pattern[0]]      # Присваивание парамметров
            self.art = pattern[1:self.settings[1] + 1]
            self.colors = [color.split() for color in pattern[-1]]
            try:                        # Проверка на нахождение сохранения в директории
                with open(self.save_name, 'r'):
                    pass
            except FileNotFoundError:   # Сохдание сохранения при его отсутствии
                with open(self.save_name, 'w', newline='') as save:
                    writer = csv.writer(
                        save, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    for i in range(self.settings[1]):
                        writer.writerow(
                            [f'discolored {self.discolor(self.colors[int(px.split()[-1]) - 1][-1])}'
                             if px.split()[-1] != '0' else 'clear #f0f0f0' for px in self.art[i]])
            with open(self.save_name, 'r', encoding='utf-8') as save:   # Открытие сохранения
                self.save = list(csv.reader(save, delimiter=';', quotechar='"'))
                x = int(485 * (self.settings[0] / self.settings[1]))
                geometry = QRect(872 // 2 - x // 2, 65,             # Присваивание геометрии холста
                                 int(485 * (self.settings[0] / self.settings[1])), 485)
                self.pixelArtWidget = QWidget(self)                     # Создание пронумерованного
                self.pixelArtWidget.setGeometry(geometry)               # и принимающего цвет
                self.pixelArtLayout = QGridLayout(self.pixelArtWidget)  # Layout's
                self.pixelArtLayout.setHorizontalSpacing(0)
                self.pixelArtLayout.setVerticalSpacing(0)

                self.coloredArtWidget = QWidget(self)
                self.coloredArtWidget.setGeometry(geometry)
                self.coloredArtLayout = QGridLayout(self.coloredArtWidget)
                self.coloredArtLayout.setHorizontalSpacing(0)
                self.coloredArtLayout.setVerticalSpacing(0)
                # Вывод пронумерованного и имеющего цвет поверх него артов
                for i in range(self.settings[1]):
                    for j in range(self.settings[0]):
                        pixel = QLabel(self.art[i][j].split()[-1], self)
                        pixel.setAlignment(Qt.AlignCenter)
                        font = QFont()
                        font.setPointSize(int(485 / max(self.settings[0:2]) / 2.5))
                        pixel.setFont(font)
                        colored_pixel = QLabel(self)
                        colored_pixel.setObjectName(self.save[i][j].split()[0])
                        colored_pixel.setStyleSheet(
                            'background-color: {}'.format(self.save[i][j].split()[-1]))
                        if colored_pixel.objectName() == 'discolored':
                            pixel.setText(self.art[i][j].split()[-1])
                        elif colored_pixel.objectName() == 'colored':
                            pixel.setText('')
                        pixel.setStyleSheet("background-color: #FFFFFF; border: 1px solid #DFDFDF")
                        if pixel.text() == '0':
                            pixel.setText('')
                            pixel.setStyleSheet("background-color: #F0F0F0")
                            colored_pixel.setStyleSheet('background-color: #F0F0F0')
                        self.pixelArtLayout.addWidget(pixel, i, j, 1, 1)
                        self.coloredArtLayout.addWidget(colored_pixel, i, j, 1, 1)

        self.up = QLabel(self)                              # Создание верхнего прямоугольника
        self.up.setGeometry(0, 0, 872, 55)
        self.up.setStyleSheet('background-color: #E7EAFD')

        self.down = QLabel(self)                            # Создание нижнего прямоугольника
        self.down.setGeometry(0, 556, 872, 55)
        self.down.setStyleSheet('background-color: #E7EAFD')

        self.congratulations = QLabel(self)     # Создания текста с поздравлением при прохождении
        self.congratulations.resize(872, 55)
        self.congratulations.setAlignment(Qt.AlignCenter)
        self.font = QFont()
        self.font.setPointSize(24)
        # Присваивание списков шрифтов
        self.fonts_list = ['Yu Gothic UI Semibold', 'Sitka Banner', 'MV Boli', 'Comic Sans MS',
                           'Microsoft YaHei UI Light', 'Segoe Script']
        # и надписей поздравления
        self.congratulations_list = ['Поздравляем!', 'Так держать!', 'Продолжай в том же духе',
                                     'Отличная работа!', 'Круто!', 'Высший пилотаж']

        self.back_button = QPushButton('◀', self)   # Создание кнопки для возвращения в меню
        font = QFont()
        font.setPointSize(20)
        self.back_button.setFont(font)
        self.back_button.setStyleSheet('color: #ffffff; background-color: #007AD9')
        self.back_button.move(15, 15)
        self.back_button.resize(25, 25)
        self.back_button.clicked.connect(self.back)
        self.back_button.clicked.connect(self.player.play)

        self.mouse_move = False

        self.color_buttons = QButtonGroup(self)
        x = 0
        # Вывод кнопок для получения цвета по номеру
        for color in self.colors:
            color_btn = QPushButton(color[0], self)
            color_btn.setGeometry(x, 556, 56, 56)
            font = QFont()
            font.setPointSize(18)
            color_btn.setFont(font)
            if len([el for el in self.hex_to_rgb(color[1]) if el < 128]) == 3:
                color_btn.setStyleSheet("color: #ffffff; background-color: {}".format(color[1]))
            else:
                color_btn.setStyleSheet("color: #000000; background-color: {}".format(color[1]))
            color_btn.clicked.connect(self.color)
            color_btn.clicked.connect(self.player.play)
            self.color_buttons.addButton(color_btn)
            x += 55
        self.info_button = QPushButton('Посмотреть информацию', self)
        self.info_button.setGeometry(365, 15, 141, 24)
        self.info_button.hide()
        self.info_button.clicked.connect(self.show_info)
        self.info_button.clicked.connect(self.player.play)
        # Изменение текста кнопок при последующем открытии холста
        for color_btn in self.color_buttons.buttons():
            if len([i for i in range(self.settings[0] * self.settings[1]) if
                    self.pixelArtLayout.itemAt(i).widget().text() == color_btn.text()]) == 0:
                color_btn.setText('✔')
                color_btn.setDisabled(True)
        # Изменение надписи и шрифта поздравления при последующем открытии
        if len([btn for btn in self.color_buttons.buttons()
                if btn.text() == '✔']) == self.settings[2]:
                    self.info_button.show()

    def back(self):     # метод для открытия меню и изменения сохранений
        self.close_window()

    def close_window(self):
        self.menu = Menu()  # открытие меню
        self.menu.show()
        self.hide()
        with open(self.save_name, 'w', newline='') as save:
            writer = csv.writer(
                save, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for i in range(int(self.settings[1])):  # изменение значений в сохранении
                for j in range(int(self.settings[0])):
                    pixel = self.coloredArtLayout.itemAt(j + i * int(self.settings[0])).widget()
                    if pixel.objectName() == 'colored':
                        self.save[i][j] = f'{pixel.objectName()} {pixel.styleSheet().split()[-1]}'
            writer.writerows(self.save)  # запись сохранения

    def color(self):    # метод для определеня цвета по номеру
        for i in range(self.settings[0] * self.settings[1]):    # Скрытие обесцвеченных пикселей
            colored_pixel = self.coloredArtLayout.itemAt(i).widget()
            if len(colored_pixel.styleSheet()) == 25 and colored_pixel.objectName() != 'colored':
                colored_pixel.setStyleSheet('')
        # Присваивание цвета по номеру
        self.color_pixel = self.sender().text(), self.sender().styleSheet().split()[-1]
        for i in range(self.settings[0] * self.settings[1]):    # Выделение пикслей взависимости
            pixel = self.pixelArtLayout.itemAt(i).widget()      # от номера
            if pixel.text() == self.sender().text():
                pixel.setStyleSheet("background-color: #BDBDBD; border: 1px solid #DFDFDF")
            elif pixel.text() != '' and pixel.styleSheet().split()[1] != '#F0F0F0':
                pixel.setStyleSheet("background-color: #FFFFFF; border: 1px solid #DFDFDF")
            else:
                pixel.setStyleSheet("background-color: #F0F0F0")

        for color_btn in self.color_buttons.buttons():  # Выделение выбранного цвета
            if color_btn == self.sender():
                color_btn.setStyleSheet(
                    f'color: {self.sender().styleSheet().split()[1]} '
                    f'border: 6px solid {self.sender().styleSheet().split()[1]} '
                    f'background-color: {self.color_pixel[-1]}')
            else:   # Смена текста при отсутстивии пикселей своего номера
                if color_btn.text() != '✔':
                    color_btn.setStyleSheet(
                        f'color: {color_btn.styleSheet().split()[1]} '
                        f'background-color: {color_btn.styleSheet().split()[-1]}')

    def mousePressEvent(self, event):           # методы для мыши
        if event.button() == Qt.LeftButton:     # Определение нажатия левой кнопки мыши
            self.mouse_move = True
            self.mouse_click(event)

    def mouseMoveEvent(self, event):
        if self.mouse_move:
            self.mouse_click(event)

    def mouseReleaseEvent(self, event):
        self.mouse_move = False

    def mouse_click(self, event):
        # Присваивание изначальных координат курсора
        mouse_x, mouse_y = event.x() - self.pixelArtWidget.x(), event.y() - self.pixelArtWidget.y()
        pixel_len = int(485 / self.settings[1])     # Определение длины пикселя
        for i in range(self.settings[0] * self.settings[1]):
            pixel = self.pixelArtLayout.itemAt(i).widget()
            colored_pixel = self.coloredArtLayout.itemAt(i).widget()
            color = self.color_pixel[1]     # Присваивание цвета
            if colored_pixel.x() < mouse_x < colored_pixel.x() + pixel_len and \
                    colored_pixel.y() < mouse_y < colored_pixel.y() + pixel_len:
                # Полное изменение цвета при совпадении номера
                if pixel.text() == self.color_pixel[0]:
                    pixel.setText('')
                    colored_pixel.setStyleSheet("background-color: {}".format(self.color_pixel[1]))
                    colored_pixel.setObjectName('colored')
                # Измение цвета на полупрозрачных при отсутствии совпадения номеров
                elif pixel.text() != self.color_pixel[0] and pixel.text() != '' and \
                        colored_pixel.objectName() == 'discolored' and \
                        self.color_pixel[0] in [btn.text() for btn in self.color_buttons.buttons()]:
                    colored_pixel.setStyleSheet(
                        "background-color: {}".format(color[0] + '80' + color[1:]))
        # Деактивация и смена текста кнопки выбора цвета при отсутствии совподающих номеров
        if len([i for i in range(self.settings[0] * self.settings[1])
                if self.pixelArtLayout.itemAt(i).widget().text() == self.color_pixel[0]]) == 0:
            for color_btn in self.color_buttons.buttons():
                if color_btn.text() == self.color_pixel[0]:
                    color_btn.setStyleSheet(
                        f'color: {color_btn.styleSheet().split()[1]}'
                        f'background-color: {color_btn.styleSheet().split()[-1]}')
                    color_btn.setText('✔')
                    color_btn.setDisabled(True)
        # Сохранение айди изображения при полном раскрашивании
        if len([btn for btn in self.color_buttons.buttons()
                if btn.text() == '✔']) == self.settings[2] and self.congratulations.text() == '':
            self.font.setFamily(''.join(sample(self.fonts_list, 1)))
            self.info_button.show()
            data = open('id.dat').readline()
            data = data.split(' ')
            if self.id not in data:
                data.append(self.id)
            with open('id.dat', 'w') as identifier:
                identifier.write(' '.join(data))

    def show_info(self):
        self.info = Info(self.id)  # Открытие нового окна
        self.info.show()

    def load_mp3(self, filename):   # Загрузка звука
        media = QUrl.fromLocalFile(filename)
        content = QtMultimedia.QMediaContent(media)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setMedia(content)

    def hex_to_rgb(self, value):    # Функции для преобразования цветов
        value = value.lstrip('#')
        return tuple(int(value[i:i + len(value) // 3], 16)
                     for i in range(0, len(value), len(value) // 3))

    def rgb_to_hex(self, red, green, blue):
        return '#%02x%02x%02x' % (red, green, blue)

    def discolor(self, value):      # Обесцвечивание цветов
        r, g, b = self.hex_to_rgb(value)
        color = round((0.58 * r) + (0.17 * g) + (0.8 * b))
        if color < 70:
            color = 70
        elif color > 255:
            color = (r + g + b) // 3
        return self.rgb_to_hex(color, color, color)


class Info(QWidget):
    def __init__(self, id):
        super().__init__()
        self.setWindowTitle('Информация')
        self.setFixedSize(802, 531)
        text = open(f'info/{id}.txt', 'r', encoding='utf-8')
        self.pixmap = QPixmap(f'images/{id}.png')
        self.image = QLabel(self)
        self.image.setGeometry(0, 0, 401, 531)
        self.image.setPixmap(self.pixmap)
        self.textBrowser = QTextBrowser(self)
        font = QFont()
        font.setFamily('Arial')
        font.setPointSize(12)
        self.textBrowser.setFont(font)
        self.textBrowser.setText(text.read())
        self.textBrowser.setGeometry(401, 0, 401, 531)
        self.textBrowser.setReadOnly(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Menu()
    ex.show()
    sys.exit(app.exec())
