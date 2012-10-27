# -*- coding: utf-8 -*-
#
#  Author: Jack Ding
#  E-Mail: jack.w.ding@gmail.com
#  Date: 09/14/2010
#　Version: 0.1
#

import os
import sys
import logging
import wx
import time

from util import *
from config_pv import *
import run_pv_mp

import multiprocessing


class MainPanel(wx.Panel):
	def __init__(self, parent):
		self.logger = logging.getLogger('AppLog')
		self.config_data = PVGConfigData.getInst()
		self.config_data.print_all()
		self.target_url = {}
		self.name_list = []
		self.url_list = []
		self.target_num = 0
		self.process_num = 0
		self.adsl_name = ''
		self.adsl_user = ''
		self.adsl_password = ''
		self.per_url_num = 0
		self.use_adsl = False
		# for url list
		self.list_index = 0
		#
		self.x = 20
		#
		self.load_config()
		wx.Panel.__init__(self, parent, size=(600, 800))
		
		head_text = wx.StaticText(self, -1, "Web Flush Tools",  (250, 10), (160, -1), wx.ALIGN_CENTER)
		head_text.SetForegroundColour('blue')
		#head_text.SetBackgroundColour('black')
		font = wx.Font(18, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
		head_text.SetFont(font)
		
 		self.create_task_view()
		self.create_url_list_view()
		self.create_edit_url_view()
		self.create_adsl_info_view()
		self.create_process_view()
		self.create_cmd_view()
	def create_task_view(self):
		x_1 = self.x + 100
		y_1 = 60
        # the combobox Control: platform
		#wx.StaticText(self, label=cn_str("URL:"), pos=(20, 60))
		#self.urlText = wx.TextCtrl(self, -1, self.target_url, pos=(120, 60), size=(250, 20))
		wx.StaticText(self, label=cn_str("Number:"), pos=(self.x, y_1))
		self.numText = wx.TextCtrl(self, -1, str(self.target_num), pos=(x_1, y_1), size=(250, 20))
		self.load_from_target_url()
	def create_edit_url_view(self):
		x_1 = self.x + 100
		x_2 = 120
		y_1 = 280
		wx.StaticText(self, label=cn_str("name:"), pos=(self.x, y_1))
		self.urlNameText = wx.TextCtrl(self, -1, "", pos=(x_1, y_1), size=(380, 20))
		wx.StaticText(self, label=cn_str("url:"), pos=(self.x, y_1+20))
		self.urlUrlText = wx.TextCtrl(self, -1, "", pos=(x_1, y_1+20), size=(380, 20))
		# save and remove button
		self.saveUrlButton =wx.Button(self, label=cn_str("Save URL  "), pos=(x_2, y_1+50))
		self.Bind(wx.EVT_BUTTON, self.Event_Save_URL, self.saveUrlButton)
		self.removeUrlButton =wx.Button(self, label=cn_str("Remove URL"), pos=(x_2+120, y_1+50))
		self.Bind(wx.EVT_BUTTON, self.Event_Remove_URL, self.removeUrlButton)
	def create_url_list_view(self):
		x_1 = self.x + 100
		y_1 = 360
		#projectList = self.config_data.get_project_build_files()
		wx.StaticText(self, label=cn_str("URL:"), pos=(self.x, y_1))
		self.urlListBox = wx.ListBox(self, 11, pos=(self.x, y_1+20),  size=(480, 140), choices=self.url_list, 
				style=wx.LB_SINGLE | wx.LB_ALWAYS_SB |wx.LB_HSCROLL, validator=wx.DefaultValidator, name="listBox")
		self.Bind(wx.EVT_LISTBOX, self.Event_URL_List, self.urlListBox)
	def create_adsl_info_view(self):
		x_1 = self.x + 100
		y_1 = 100
		wx.StaticText(self, label=cn_str("ADSL Conntion:"), pos=(self.x, y_1))
		self.anameText = wx.TextCtrl(self, -1, self.adsl_name, pos=(x_1, y_1), size=(250, 20))
		wx.StaticText(self, label=cn_str("ADSL User"), pos=(self.x, y_1+20))
		self.auserText = wx.TextCtrl(self, -1, self.adsl_user, pos=(x_1, y_1+20), size=(250, 20))
		wx.StaticText(self, label=cn_str("Password"), pos=(self.x, y_1+40))
		self.apasswdText = wx.TextCtrl(self, -1, self.adsl_password, pos=(x_1,y_1+40), size=(250, 20))
	def create_process_view(self):
		x_1 = self.x + 100
		y_1 = 180
		wx.StaticText(self, label=cn_str("Process"), pos=(self.x, y_1))
		t_str = str(self.process_num)
		self.processText = wx.TextCtrl(self, -1, t_str, pos=(x_1, y_1), size=(250, 20))
		wx.StaticText(self, label=cn_str("Per URL Num"), pos=(self.x, y_1+30))
		t_str = str(self.per_url_num)
		self.perdialText = wx.TextCtrl(self, -1, t_str, pos=(x_1, y_1+30), size=(250, 20))
	def create_cmd_view(self):
        # A button
		self.startButton =wx.Button(self, label=cn_str("Start"), pos=(500, 60))
		self.Bind(wx.EVT_BUTTON, self.Event_Start_Cmd, self.startButton)
		self.stopButton =wx.Button(self, label=cn_str("Stop"), pos=(500, 90))
		self.Bind(wx.EVT_BUTTON, self.Event_Stop_Cmd, self.stopButton)
		self.saveButton =wx.Button(self, label=cn_str("Save"), pos=(500, 120))
		self.Bind(wx.EVT_BUTTON, self.Event_Save_Cmd, self.saveButton)
	def load_config(self):
		self.target_url = self.config_data.get_target_url()
		self.load_from_target_url()
		self.target_num = self.config_data.get_target_num()
		self.process_num = self.config_data.get_process_num()
		self.use_adsl = self.config_data.get_use_adsl()
		self.adsl_name = self.config_data.get_adsl_name()
		self.adsl_user = self.config_data.get_adsl_user()
		self.adsl_password = self.config_data.get_adsl_password()
		self.per_url_num = self.config_data.get_per_url_num()
	def save_config(self):
		self.update_data()
		self.config_data.set_target_url(self.target_url)
		self.config_data.set_target_num(self.target_num)
		self.config_data.set_process_num(self.process_num)
		self.config_data.set_use_adsl(self.use_adsl)
		self.config_data.set_adsl_name(self.adsl_name)
		self.config_data.set_adsl_user(self.adsl_user)
		self.config_data.set_adsl_password(self.adsl_password)
		self.config_data.set_per_url_num(self.per_url_num)
		self.config_data.save_data()
	def update_data(self):
		self.target_num = eval(self.numText.GetValue())
		self.process_num = eval(self.processText.GetValue())
		self.adsl_name = self.anameText.GetValue()
		self.adsl_user = self.auserText.GetValue()
		self.adsl_password = self.apasswdText.GetValue()
		self.per_url_num = eval(self.perdialText.GetValue())
		self.print_config()
	def update_url_list_data(self):
		self.load_from_target_url()
		print "###self.url_list=", self.url_list
		self.urlListBox.Clear()
		for x in self.url_list:
			self.urlListBox.Append(x)
		self.Refresh()
	def Event_Start_Cmd(self, event):
		print u"start"
		self.save_config()
		run_pv_mp.start()
	def Event_Stop_Cmd(self, event):
		print u"stop"
		run_pv_mp.stop()
	def Event_Save_Cmd(self, event):
		print u"save"
		self.save_config()
	def Event_URL_List(self, event):
		urlList = event.GetEventObject()
		self.list_index = urlList.GetSelection()
		sel = event.GetString()
		self.urlNameText.SetValue(self.name_list[self.list_index])
		self.urlUrlText.SetValue(sel)
		print u"URL:id=%s,name=%s, sel=%s" % (self.list_index , self.name_list[self.list_index], sel)
	def Event_Save_URL(self, event):
		name = self.urlNameText.GetValue()
		value = self.urlUrlText.GetValue()
		for k,v in self.target_url.items():
			if k == name:
				self.target_url[k] = value
				print "edit name=%s, new url=%s" % (name, value)
				break
		# not find key in dict, then add new one
		self.target_url[name] = value
		print "add new, name=%s, url=%s" % (name, value)
		self.update_url_list_data()
	def Event_Remove_URL(self, event):
		object = event.GetEventObject()
		name = self.urlNameText.GetValue()
		value = self.urlUrlText.GetValue()
		find = False
		for k in self.target_url:
			if k == name:
				find = True
				break
		if find == True:
			del(self.target_url[k])
			print "remove: name=%s, url=%s" % (name, value)
			self.urlNameText.SetValue('')
			self.urlUrlText.SetValue('')
		else:
			print "can not del this url"
		self.update_url_list_data()
	def load_from_target_url(self):
		self.name_list = []
		self.url_list = []
		for k, v in self.target_url.items():
			self.name_list.append(k)
			self.url_list.append(v)
	def Event_Select_Project(self, event):
		'''
		wildcard = "Symbian project build file (*.inf)|*.inf|" \
				"Symbian package file (*.pkg)|*.pkg|" \
				"All files (*.*)|*.*"
		dialog = wx.FileDialog(None, "Choose a file", os.getcwd(), 
				"", wildcard, wx.OPEN)
		if dialog.ShowModal() == wx.ID_OK:
			file_path = dialog.GetPath() 
			self.projectListBox.Append(file_path)
			n = self.projectListBox.GetCount()
			p_list = []
			for i in range(0, n):
				p_list.append(self.projectListBox.GetString(i))
			self.config_data.set_project_info_list(p_list)

		dialog.Destroy()
		'''
		print u""
	def check_url_list(self):
		n1 = len(self.target_url)
		n2 = len(self.url_list)
		n3 = len(self.name_list)
		print "self.target_url==%d, url_list=%d, name_list=%d" % (n1, n2, n3)
		
	def print_config(self):
		msg = "MainPanel: target_num=%d|process_num=%d|target_url=%s|use_adsl=%d|adsl_name=%s|adsl_user=%s|adsl_password=%s" % \
				(self.target_num, self.process_num, self.target_url, \
					self.use_adsl, self.adsl_name, self.adsl_user, self.adsl_password)
		print msg

		
		
class MainFrame(wx.Frame):

    def __init__(self, parent, id, title):
		print "Frame __init__"
		frame_style = wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX
		#wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MINIMIZE_BOX |wx.MAXIMIZE_BOX)
		wx.Frame.__init__(self, parent=parent, id=-1, title=cn_str("Coolham Tools"), pos=wx.DefaultPosition, 
				size=(800, 600), style=frame_style)
		 # self.frame = wx.Frame(None, id=-1, title="Startup", pos=wx.DefaultPosition,
		# size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE,
		#panel = wx.Panel(self, -1, size=(300, 100))
		pannel = MainPanel(self)
		
		# button = wx.Button(panel, -1, "Close Me", pos=(15, 15))
		# self.Bind(wx.EVT_BUTTON, self.OnCloseMe, button)
		# self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
    def OnCloseMe(self, event):
        self.Close(True)

    def OnCloseWindow(self, event):
        self.Destroy()
	
class MainApp(wx.App):

	def __init__(self, redirect=True, filename=None):
		self.logger = logging.getLogger('AppLog')
		self.logger.debug("App __init__")
		self.config_data = PVGConfigData.getInst()
		wx.App.__init__(self, redirect, filename)

	def OnInit(self):
		self.logger.debug("App OnInit")
		#print "OnInit"    #输出到stdout
		# self.frame = wx.Frame(None, id=-1, title="Startup", pos=wx.DefaultPosition,
		# size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE,
		# name="frame")
		self.frame = MainFrame(None, id=-1, title="CoolHam")
		
		self.frame.Show()
		self.SetTopWindow(self.frame)
		#print sys.stderr, "A pretend error message"    #输出到stderr
		return True

	def OnExit(self):
		print "OnExit"

def register(id):
	time.sleep(2)
	r = RegisterClient("pv_generator", version)
	r.do_regist()
	
def regist_client():
	th = threading.Thread(target=register,args=(1,) )
	th.start()
	
	
if __name__ == '__main__':
	multiprocessing.freeze_support()
	#regist_client()
	app = MainApp(redirect=False) 
	app.MainLoop()  

	
#
# if __name__ == '__main__':
	# app = wx.App(False)
	# #frame = wx.Frame(None, -1, "Client Auto Builder")   
	# frame = wx.Frame(None, id=-1, title="Client Auto Builder", pos=wx.DefaultPosition, 
					# size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, name="frame")
	# panel = MainPannel(frame)
	# #MiniFrame().Show()

	# frame.Show()
	# app.MainLoop()




