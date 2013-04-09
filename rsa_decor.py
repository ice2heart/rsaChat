#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
-----------------------------------------
Декоратор для rsa
-----------------------------------------

print "key", a.save_pkcs1(format='DER').encode("hex")
^Предоставление ключа в виде хекса

'''
import rsa


class Crypt:
    def __init__(self):
        #Словарь в котором будут храниться известные нам ключи
        self.keys = dict()
        #Генерируем и сохраняем наши ключи
        (a, b) = self.genKey(1024)
        self.privateKey = b
        self.pubKey = a

    def hasKey(self, id):
        #Проверяем на наличие ключа для контакта
        if self.keys.has_key(id) == False:
            return False
        else:
            return True

    def decodeKey(self, key):
        #Создаем публичный ключи и загружаем переданый по сети вариант
        return rsa.PublicKey(1, 1).load_pkcs1(key, format='DER')

    def saveKey(self, id, key):
    #Сохраняем ключ
        self.keys[id] = key

    def genKey(self, size):
        #Обертка для рса
        return rsa.newkeys(size, poolsize=8)

    def cryptMesg(self, to, mesg):
        #Шифруем сообщение
        getHex = mesg.encode('utf-8').encode('hex')
        a = rsa.encrypt(getHex, self.keys[to])
        #print len(mesg),len(a)
        return a.encode('hex')

    def decryptMesg(self, mesg):
        #Пытаемся расшифровать сообщение, иначе выдаем ошибку
        try:
            mess = rsa.decrypt(mesg.decode("hex"), self.privateKey)
        except rsa.pkcs1.DecryptionError:
            print "cant decrypt"
            return "#errorDecrypt"
        return mess.decode('hex').decode('utf-8')
