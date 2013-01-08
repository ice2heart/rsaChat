#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xmpp,sys

#Данный фаил сожердит обертку для xmpp 
class sjabber:
	def __init__(self,xmpp_jid,xmpp_pwd):
		self.xmpp_jid = xmpp_jid
		self.xmpp_pwd = xmpp_pwd
		self.jid = xmpp.protocol.JID(xmpp_jid)
		self.client = xmpp.Client(self.jid.getDomain(),debug=[])
	def connect(self):
		con=self.client.connect()
		if not con:
			print 'could not connect!'
			sys.exit()
		print 'connected with',con
		auth = self.client.auth(self.jid.getNode(),str(self.xmpp_pwd),resource='xmpppy')
		if not auth:
			print 'could not authenticate!'
			sys.exit()
		print 'authenticated using',auth
		#Говорим серверу что мы онлайн! 
		self.client.sendInitPresence(1)
	def Process(self):
		a = self.client.Process(1)
	def send(self,to,mess):
		id = self.client.send(xmpp.protocol.Message(to,mess))
		print 'sent message with id',id
	def disconnect(self):
		self.client.sendInitPresence(1)
		self.client.disconnect()
	
	def userList(self):
		return self.client.getRoster().keys()

	def StepOn(self):
		try:
			self.Process()
		except:
			return 0
		return 1
	def setCB(self, CB):
		self.CB = CB
		self.client.RegisterHandler('message',self.messageCB)
	def messageCB(self,conn,mess):
		if ( mess.getBody() == None ):
			return
		self.CB(self,mess)
