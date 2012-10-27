# -*- coding: utf-8 -*-
#
#  Author: Weijian Ding
#
#

import os
import sys
import xml.parsers.expat
import threading
import logging
import subprocess
import traceback
from xml.dom.minidom import parse, parseString, getDOMImplementation

#import xml.dom.minidom

from util import *

env_path = os.getenv('PATH')


def check_str_type(ss):
	if isinstance(ss, unicode):
		print "## unicode"
	else:
		#print "## no unicode"
		try:
			unicode(ss, "ascii")
		except UnicodeError:
			#print "## not ascii"
			try:
				unicode(ss, "utf-8")
			except UnicodeError:
				print "## not utf-8"
			else:
				print "## utf-8"
		else:
			# str was valid ASCII data
			print "## ASCII"
			#pass
			
#
#
#
class PVGConfigData(object):
	logger = logging.getLogger('Module')
	file_name = 'config.xml'
	target_url = {}
	target_num = 0
	process_num = 0
	use_adsl = False
	adsl_name = ''
	adsl_user = ''
	adsl_password = ''
	per_url_num = 0
	
	build_options = [["" for x in range(10)] for y in range(10)]
	__inst = None # make it so-called private  
	__lock = threading.Lock() # used to synchronize code  
	
	def __init__():  
		"disable the __init__ method"  
	@staticmethod  
	def getInst():  
		PVGConfigData.__lock.acquire()  
		if not PVGConfigData.__inst:  
			PVGConfigData.__inst = object.__new__(PVGConfigData)  
			object.__init__(PVGConfigData.__inst) 
			PVGConfigData.load_data()
		PVGConfigData.__lock.release()  
		return PVGConfigData.__inst  
	@staticmethod  
	def __reset_data():
		PVGConfigData.platform = ""
		PVGConfigData.sdk_path = ""
		PVGConfigData.symbian_project = []
	
	@staticmethod  
	def load_data():
		PVGConfigData.logger.debug("PVGConfigData:load_data()")
		PVGConfigData.__reset_data()
		try:
			f = open(PVGConfigData.file_name, 'r')
			str = f.read()
			PVGConfigData.__handle_input_xml(str)
			f.close()
		except Exception, e:
			exstr = traceback.format_exc() 
			print exstr
			PVGConfigData.logger.error("PVGConfigData:load_data() failed!")
			print "Can not load data:", PVGConfigData.file_name
			PVGConfigData.__reset_data()
	@staticmethod  
	def save_data():
		PVGConfigData.logger.debug("PVGConfigData:save_data()")
		str = PVGConfigData.__encode_xml_data()
		f = open(PVGConfigData.file_name, 'w')
		t = str.encode('utf=8')
		header = u'<?xml version="1.0" encoding="utf-8"?>\n'
		h = header.encode('utf=8')
		f.write(h)
		f.write(t)
		f.close()
	@staticmethod  
	def __handle_input_xml(xml_data):
		#PVGConfigData.logger.debug("PVGConfigData:handle_input_xml=%s", xml_data.decode('utf-8').encode('gb2312'))
		try:
			dom = parseString(xml_data)
			task_node = dom.getElementsByTagName('task')[0]
			PVGConfigData.__parse_task_config(task_node)
			adsl_node = dom.getElementsByTagName('adsl')[0]
			PVGConfigData.__parse_adsl_config(adsl_node)
		except:
			exstr = traceback.format_exc() 
			print exstr
	@staticmethod  
	def __parse_task_config(task_node):

		node2s = task_node.getElementsByTagName('target-url')[0]
		node2ss = node2s.getElementsByTagName('url')
		count = 0
		for node_t in node2ss:
			name = node_t.getAttribute('name')
			#print "name=%s" % name
			for node_tt in node_t.childNodes:
				if node_tt.nodeType == node_tt.TEXT_NODE:
					count = count + 1
					url = node_tt.data
					PVGConfigData.target_url[name] = url
					#print "url%d=%s" % (count, url)
		node2s = task_node.getElementsByTagName('target-num')[0]
		for node_t in node2s.childNodes:
			if node_t.nodeType == node_t.TEXT_NODE:
				num_str = node_t.data
				PVGConfigData.target_num = eval(num_str)
				#print "target_num=", PVGConfigData.target_num
		node2s = task_node.getElementsByTagName('process-num')[0]
		for node_t in node2s.childNodes:
			if node_t.nodeType == node_t.TEXT_NODE:
				num_str = node_t.data
				PVGConfigData.process_num = eval(num_str)
				#print "process_num=", PVGConfigData.process_num
		node2s = task_node.getElementsByTagName('per-dial-num')[0]
		for node_t in node2s.childNodes:
			if node_t.nodeType == node_t.TEXT_NODE:
				num_str = node_t.data
				PVGConfigData.per_url_num = eval(num_str)
				#print "per dial num=", PVGConfigData.per_url_num
		node2s = task_node.getElementsByTagName('use-adsl')[0]
		for node_t in node2s.childNodes:
			if node_t.nodeType == node_t.TEXT_NODE:
				num_str = node_t.data
				if num_str == "0":
					PVGConfigData.use_adsl = False
				else:
					PVGConfigData.use_adsl = True
				#print "user adsl=", PVGConfigData.use_adsl
	@staticmethod  
	def __parse_adsl_config(adsl_node):
		node2s = adsl_node.getElementsByTagName('name')[0]
		for node_t in node2s.childNodes:
			if node_t.nodeType == node_t.TEXT_NODE:
				PVGConfigData.adsl_name = node_t.data
				#print "adsl name=", PVGConfigData.adsl_name
		node2s = adsl_node.getElementsByTagName('user')[0]
		for node_t in node2s.childNodes:
			if node_t.nodeType == node_t.TEXT_NODE:
				PVGConfigData.adsl_user = node_t.data
				#print "adsl user=", PVGConfigData.adsl_user
		node2s = adsl_node.getElementsByTagName('password')[0]
		for node_t in node2s.childNodes:
			if node_t.nodeType == node_t.TEXT_NODE:
				PVGConfigData.adsl_password = node_t.data
				#print "adsl password=", PVGConfigData.adsl_password
	@staticmethod  
	def __encode_xml_data():
		print "encode_xml_data"
		impl = getDOMImplementation()
		newdoc = impl.createDocument(None, "coolham", None)
		top_element = newdoc.documentElement
		
		task_node = PVGConfigData.__create_task_node(newdoc)
		adsl_node = PVGConfigData.__create_adsl_node(newdoc)
		
		top_element.appendChild(task_node)
		top_element.appendChild(adsl_node)
		
		return top_element.toxml()
	@staticmethod  
	def __create_task_node(doc):
		snode = doc.createElement("task")
		
		node1 = doc.createElement("target-url")
		for k, v in PVGConfigData.target_url.items():
			node2 = doc.createElement("url")
			node2.setAttribute('name', k)
			text = doc.createTextNode(v)
			node2.appendChild(text)
			node1.appendChild(node2)
		snode.appendChild(node1)


		node1 = doc.createElement("target-num")
		ts = str(PVGConfigData.target_num)
		text = doc.createTextNode(ts)
		node1.appendChild(text)
		snode.appendChild(node1)

		node1 = doc.createElement("process-num")
		ts = str(PVGConfigData.process_num)
		text = doc.createTextNode(ts)
		node1.appendChild(text)
		snode.appendChild(node1)

		node1 = doc.createElement("per-dial-num")
		ts = str(PVGConfigData.per_url_num)
		text = doc.createTextNode(ts)
		node1.appendChild(text)
		snode.appendChild(node1)

		node1 = doc.createElement("use-adsl")
		ts = '%d' % PVGConfigData.use_adsl
		text = doc.createTextNode(ts)
		node1.appendChild(text)
		snode.appendChild(node1)
			
		return snode
	@staticmethod  
	def __create_adsl_node(doc):
		snode = doc.createElement("adsl")

		node1 = doc.createElement("name")
		text = doc.createTextNode(PVGConfigData.adsl_name)
		node1.appendChild(text)
		snode.appendChild(node1)

		node1 = doc.createElement("user")
		text = doc.createTextNode(PVGConfigData.adsl_user)
		node1.appendChild(text)
		snode.appendChild(node1)

		node1 = doc.createElement("password")
		text = doc.createTextNode(PVGConfigData.adsl_password)
		node1.appendChild(text)
		snode.appendChild(node1)

		return snode
		
	@staticmethod  
	def print_all():
		print "----- All Config Data ------"
		urls = "target_url="
		for k, v in PVGConfigData.target_url.items():
			ss = "%s," % v
			urls += ss
		msg = "PVGConfigData: target_num=%d|process_num=%d|per_dial_num=%d|target_url=%s|use_adsl=%d|adsl_name=%s|adsl_user=%s|adsl_password=%s" % \
				(PVGConfigData.target_num, PVGConfigData.process_num, PVGConfigData.per_url_num, urls, \
					PVGConfigData.use_adsl, PVGConfigData.adsl_name, PVGConfigData.adsl_user, PVGConfigData.adsl_password)
		print "" + msg
		
	@staticmethod  
	def get_target_url():
		return PVGConfigData.target_url
	@staticmethod  
	def set_target_url(url):
		PVGConfigData.target_url = url
	@staticmethod  
	def get_target_num():
		return PVGConfigData.target_num
	@staticmethod  
	def set_target_num(target_num):
		PVGConfigData.target_num = target_num
	@staticmethod  
	def get_process_num():
		return PVGConfigData.process_num
	@staticmethod  
	def set_process_num(n):
		PVGConfigData.process_num = n
	@staticmethod  
	def get_use_adsl():
		return PVGConfigData.use_adsl
	@staticmethod  
	def set_use_adsl(flag):
		PVGConfigData.use_adsl = flag
	@staticmethod  
	def get_adsl_name():
		return PVGConfigData.adsl_name
	@staticmethod  
	def set_adsl_name(name):
		PVGConfigData.adsl_name = name
	@staticmethod  
	def get_adsl_user():
		return PVGConfigData.adsl_user
	@staticmethod  
	def set_adsl_user(user):
		PVGConfigData.adsl_user = user
	@staticmethod  
	def get_adsl_password():
		return PVGConfigData.adsl_password
	@staticmethod  
	def set_adsl_password(passwd):
		PVGConfigData.adsl_password = passwd
	@staticmethod  
	def get_per_url_num():
		return PVGConfigData.per_url_num
	@staticmethod  
	def set_per_url_num(n):
		PVGConfigData.per_url_num = n
		
	# @staticmethod  
	# def print_caller_notify():
		# print "Caller Notify:"
		# for x in PVGConfigData.notify_array:
			# if x[0] <> "":
				# print x		

	# @staticmethod  
	# def print_caller_notify_to_str():
		# str = "Caller Notify Data:\n"
		# for x in PVGConfigData.notify_array:
			# if x[0] <> "":
				# str = str + x[0] + u" " + x[1] + u" " + x[2] + u" " + x[3]
		# return str
	# @staticmethod  
	# def print_voice_mail():
		# print "Voice Mail:"
		# for x in PVGConfigData.voice_mail:
			# if x[0] <> "":
				# print x		
				