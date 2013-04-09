#!/usr/bin/env python
# -*- coding: utf-8 -*-
from  jabber import sjabber
import os
import re
import sys
from rsa_decor import Crypt

from PyQt4.QtGui import QApplication, QMainWindow
from PyQt4.QtCore import QTimer
from PyQt4.QtCore import QThread
from gui import Ui_MainWindow


class core:
    def loadConfig(self):
        import ConfigParser

        config = ConfigParser.ConfigParser()
        if os.path.exists('rsaChat.rc'):
            config.read('rsaChat.rc')
            self.xmpp_jid = config.get('Settings', 'jid')
            self.xmpp_pwd = config.get('Settings', 'passwd')
        else:
            print '''
File rsaChat.rc not found.
Example
-------------------------

[Settings]
jid = nick@server
passwd = reallyStrongPass

-------------------------
'''
            exit(0)
        '''
		#пример записи в настройки, на всякий случай
		config.add_section('Settings')
		config.set('Settings', 'jid', 'ice2heart@jabber.ru')
		config.set('Settings', 'passwd', 'e9oojqw534')
		with open('example.cfg', 'wb') as configfile:
			config.write(configfile)
		'''

    def getKey(self, to):
        mesg = "#getkey"
        self.jb.send(to, mesg)

    def messageCB(self, conn, mess):
        #Данный колбек проверяет регулярное выражение, после чего
        #Либо рабоатет с ключами, либо шифрует сообения
        if ( mess.getBody() == None ):
            return
        msg = mess.getBody()
        patern = re.compile('^#(getkey|sendkey|mesg|getlastmesg) ?(.*)')
        res = patern.search(msg)
        if res:
            #Проверка
            a = res.groups()[0]
            if a == "getkey":
                self.sendKey(mess.getFrom())
                if self.crypt.hasKey(mess.getFrom()) != False:
                    conn.send(mess.getFrom(), "#getkey")
            elif a == "sendkey":
                if res.groups()[1] != '':
                    a = self.crypt.decodeKey(res.groups()[1].decode("hex"))
                    self.crypt.saveKey(mess.getFrom().getStripped(), a)
            elif a == "mesg":
                decryptMess = self.crypt.decryptMesg(res.groups()[1])
                if decryptMess == "#errorDecrypt":
                    self.sendKey(mess.getFrom())
                    self.print_("Error decrypt sendKey")
                else:
                    self.print_(self.to + "--> " + decryptMess)
            elif a == "getlastmesg*":
                print a

    def print_(self, text):
        self.ui.textBrowser.append(text)

    def sendKey(self, to):
        #Берем публичный ключ и прегоняем его в hex и отправляем
        key = '#sendkey ' + self.crypt.pubKey.save_pkcs1(format='DER').encode('hex')
        self.jb.send(to, key)

    def sendMsg(self):
        #Ужастная функция с костылем которая прверяет наличие ключа
        #При наличии отправляет собщение иначе иницирует обмен ключами
        if self.crypt.hasKey(self.to) == False:
            self.getKey(self.to)
            return
        text = unicode(self.ui.lineEdit.text().toUtf8(), "utf-8")
        if text == "":
            return
        print text
        acam = ""
        #Проблема модуля шифрования в ограничении длины строки, поэтому костыль
        while (len(text) > 0):
            if (len(text) > 29):
                cutText = text[0:29]
                text = text[29:]
            else:
                cutText = text
                text = ""

            mes = self.crypt.cryptMesg(self.to, cutText)
            self.ui.lineEdit.clear()
            self.jb.send(self.to, "#mesg " + mes)
            acam = acam + cutText
        self.print_(self.to + "<-- " + acam)

    def setToRow(self, alpha):
        #Устанавливаем кому отправлять сообещния, в списке делаем его в фокусе
        self.to = unicode(self.ui.listWidget.item(alpha).text().toUtf8(), "utf-8")
        self.ui.lineEdit.setFocus()
        self.print_("Now mesg to " + self.to)

    def __init__(self):
        #Первым делом загрузим настройки
        self.loadConfig()
        #Создадим объект для шифорования
        self.crypt = Crypt()

        #Создадим и подключимся к жабберу
        self.jb = sjabber(self.xmpp_jid, self.xmpp_pwd)
        self.jb.connect()

        #Зададим колбек для приходящих сообщений
        self.jb.setCB(self.messageCB)

        #Создадим Qt обработчик событий для графики
        self.app = QApplication(sys.argv)

        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        #Подключим сигналы нажатия на кнопку отправить и нажатие энтер
        self.ui.pushButton.clicked.connect(self.sendMsg)
        self.ui.lineEdit.returnPressed.connect(self.sendMsg)

        self.window.show()

        #А теперь заполним юзерлист
        userList = self.jb.userList()
        for i in userList:
            self.ui.listWidget.addItem(i)
            #Меняем пользователя для отправки собщения
        self.ui.listWidget.currentRowChanged.connect(self.setToRow)
        #Выберем по умолчанию первого пользователя
        self.ui.listWidget.setCurrentRow(0)

        #Создадим рабочего который будет "дергать" обработчик жаббера
        self.workThread = WorkThread()
        self.workThread.setWorker(self.jb)
        self.workThread.start()
        #собственно запускаем обработчик сигналов и ожидаем его завершения
        sys.exit(self.app.exec_())


class WorkThread(QThread):
    def __init__(self):
        QThread.__init__(self)

    def setWorker(self, jb):
        self.jb = jb

    def run(self):
        while self.jb.StepOn(): pass


if __name__ == "__main__":
    a = core()
