# -*- coding: utf-8 -*-
#
#  Author:  Jack Ding
#  E-Mail:  jack.w.ding@gmail.com
#  Date:    09/29/2010
#  Version: 0.2
# 
#  Note:  This is a Multi-Process programe
#

import os
import sys
import random
import time
import socket
import httplib
import traceback 
import logging

import threading
import subprocess

#import urllib2
#import webbrowser 
import win32com.client
from win32com.client import Dispatch, constants

import multiprocessing
from multiprocessing import Process, Queue, current_process, Lock

#from network import *
from config_pv import *
import util_process


logger = logging.getLogger('Module')

'''
'''
cur_dir = os.getcwd()
sys.path.append(cur_dir)

# global
g_host = "localhost"
g_port = 23456
g_mutex = threading.Lock() 
g_index = 0

# Create queues
g_task_queue = Queue()
g_done_queue = Queue()

# 
ie_process_name = 'iexplore.exe'

class AdslControl():
	def __init__(self):
		logger.debug("init")
	def control(self):
		'''
		rasdial cnc username password
		rasdial cnc /disconnect 
		'''
		
'''
'''
class VisitResult():
	def __init__(self, id=-1, hostname=None, code=0, result=None):
		self.id = id
		self.hostname = hostname
		self.code = code
		self.result = result
		self.consume_time = 0;
	def get_result(self):
		#msg = 'id:%d,result=%s' % ( self.id, self.result)
		return (self.id, self.result, self.consume_time)

'''
Error_Code:
0: SUCCESS, OK
1: Timeout
2: Other
'''		
class WebVisitor():
	def __init__(self, DestHost, WorkerId, TaskId):
		#logger.debug("#%d, new WebVisitor" % os.getpid()
		self.dest_host = DestHost
		self.worker_id = WorkerId
		self.task_id = TaskId
		self.v_result = VisitResult()
		self.timeout = 5
	def navigate(self):
		self.v_result.id = self.task_id
		try:
			logger.debug("task_id=%3d, worker=%2d, visit=%s" % (self.task_id, self.worker_id, self.dest_host))
			start = int(time.time())
			ie = Dispatch('InternetExplorer.Application')    
			ie.Visible = 0
			ie.Navigate(self.dest_host)
			state = ie.ReadyState    			
			count = 0
			while 1:
				state = ie.ReadyState    
				if state == 4:   
					self.v_result.result = 'OK'
					self.v_result.code = 0
					break
				if count > self.timeout:
					self.v_result.result = 'Timeout'
					self.v_result.code = 1
					break
				time.sleep(1)
				count = count + 1
			end = int(time.time())
			self.v_result.consume_time = end - start
			state = None
			ie.Quit()
			ie = None
			del ie
		except Exception, e:
			exstr = traceback.format_exc() 
			print exstr
			self.v_result.result = 'Exception'
			self.code = 3
		return self.v_result
	def navigate2(self):
		self.v_result.result = 'OK'
		self.code = 0
		return self.v_result
	def simu_login(self):
		ie = win32com.client.Dispatch("InternetExplorer.Application")    
		ie.Visible = 0
		#ie.Navigate(loginurl)    
		ie.Document.getElementById("tbUserName").value=username    
		ie.Document.getElementById("tbPassword").value=password    
		ie.Document.getElementById("btnLogin").click()   
		while 1:    
			state = ie.ReadyState    
			print state    
			if state ==4 and str(ie.LocationURL) == "http://home.cnblogs.com/":    
				break
			time.sleep(1)
		#print ie.Document.getElementById('lnk_current_user').title
	def test(self):
		ie = win32com.client.Dispatch("InternetExplorer.Application")    
		while ie.Busy:
			time.sleep(0.5)
		doc = ie.Document
		for i in doc.images:
			print i.src, i.width, i.height	
		doc.forms[0].submit()  
		
		
	
'''	
# Function run by worker processes
'''
def worker(worker_id, input, output):
	msg = ">>>worker:%2d, pid=%4d" % (worker_id, os.getpid())
	logger.debug(msg)
	global g_host, g_port
	server_addr = (g_host, g_port)
	client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#
	for func in iter(input.get, 'STOP'):
		ret = request_to_controller(client, server_addr, 'GET_TASK_ID')
		if ret != "STOP":
			task_id = eval(ret)
			result = make_task_query(client, worker_id, task_id, func)
			text = 'TASK_RESULT|ID=%d|CODE=%d|MSG=%s|WORKER=%d' % (task_id, result.code, result.result, worker_id)
			request_to_controller(client, server_addr, text)
			output.put(result)
		else:
			logger.debug("worker:%2d recv STOP flag" % worker_id)
			output.put('STOP')
			break
	client.close()
	logger.debug(">>>worker:%2d finished" % (worker_id,))

def make_task_query(udp_client, worker_id, task_id, host):
	"""
	This is a bit fancy as it accepts both instances
	of SnmpSession and host/ip addresses.  This
	allows a user to customize mass queries with
	subsets of different hostnames and community strings
	"""
	if isinstance(host, WebVisitor):
		logger.debug("#############")
		return host.navigate()
	else:
		s = WebVisitor(DestHost=host, TaskId=task_id, WorkerId=worker_id)
		return s.navigate()



def notify_controller(cmd):
	global g_host, g_port
	addr = (g_host, g_port)
	client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	if(not client.sendto(cmd, addr)):
		logger.debug("client send failed")
		
	time.sleep(1)
	client.close()

def request_to_controller(udp_socket, server_addr, cmd):
	#logger.debug("request_to_controller, server=" , server_addr
	MAXLEN = 1024
	data = None
	try:
		#if len(cmd) != udp_socket.send(cmd):
		if len(cmd) != udp_socket.sendto(cmd, server_addr):
			# where to get error message "$!".
			logger.debug("cannot send to controller")
			raise SystemExit(1)
		(data, addr) = udp_socket.recvfrom(MAXLEN)
		#logger.debug("client_recv=", data)
	except socket.error, e:
		exstr = traceback.format_exc() 
		logger.debug("request_to_controller error:%s" % exstr)		
	return data
	
'''
	controller process
'''	
def controller(id):
	logger.debug(">>>controller started")
	proc_task_num = 0
	success_task_num = 0
	failed_task_num = 0
	
	# Set the socket parameters
	global g_host, g_port
	server_addr = (g_host, g_port)
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		server_socket.bind(server_addr)
	except socket.error, e:
		logger.debug("Couldn't be a udp server on port %d : %s" % (g_port, e))
		raise SystemExit
	MAXLEN = 1024
	stop_flag = False
	while True:
		data, addr = server_socket.recvfrom(MAXLEN)
		if not data:
			logger.debug("Client has exited!")
			break
		else:
			items = data.split('|')
			cmd = items[0]
			if cmd == "QUIT":
				logger.debug(">>>controller recv QUIT cmd")
				break
			elif cmd == "STOP":
				stop_flag = True
				logger.debug(">>>controller recv STOP cmd")
			elif cmd == "GET_TASK_ID":
				if(stop_flag == True):
					logger.debug(">>>controller ask work to stop")
					server_socket.sendto("STOP", addr)
				else:
					text = str(get_task_id())
					server_socket.sendto(text, addr)
			elif cmd == "TASK_RESULT":
				id = items[1]
				code = items[2]
				msg = items[3]
				proc_task_num = proc_task_num + 1
				if code == "CODE=0":
					success_task_num = success_task_num + 1
				else:
					failed_task_num = failed_task_num + 1
				server_socket.sendto("ACK", addr)
			else:
				text = "Unknown"
				server_socket.sendto(text, addr)
				logger.debug("Unknown request")
	time.sleep(1)
	server_socket.close()
	logger.debug(">>>controller exit.")
#	
def get_task_id():
	global g_mutex, g_index
	g_mutex.acquire()
	g_index = g_index + 1
	g_mutex.release()
	return g_index

def adsl_connect(adsl_name, username, password):
	cmd = 'rasdial ' + adsl_name + ' ' + username + ' ' + password
	logger.debug(">>>adsl_connect, " + cmd)
	ad = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	ad.wait()
	print ad.stdout.read()
	ret = ad.returncode 
	logger.debug("ret=" + str(ret))
	
def adsl_disconnect(adsl_name):
	cmd = 'rasdial ' + adsl_name + ' /disconnect '
	logger.debug(">>>adsl_disconnect, " + cmd)
	ad = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	ad.wait()
	print ad.stdout.read()
	ret = ad.returncode 
	logger.debug("ret=" + str(ret))


	
def start_controller():
	# control process
	control =Process(target=controller, args=(1, ))
	control.start()
	# wait for controller start
	time.sleep(1)

def start_scheduler():
	# control process
	s =Process(target=scheduler, args=(1,))
	s.start()
	# wait for controller start
	time.sleep(1)
	
'''
	controller process
'''	
def scheduler(id):
	config_data = PVGConfigData.getInst()
	config_data.print_all()
	target_url = config_data.get_target_url()
	target_num = config_data.get_target_num()
	per_url_num = config_data.get_per_url_num()
	process_num = config_data.get_process_num()
	use_adsl = config_data.get_use_adsl()
	adsl_name = config_data.get_adsl_name()
	adsl_user = config_data.get_adsl_user()
	adsl_password = config_data.get_adsl_password()
	
	#
	url_num = len(target_url)
	per_dial_num = per_url_num * url_num
	logger.debug(">>>scheduler started")
	start = int(time.time())

	logger.debug("use_adsl=%d" % use_adsl)
	if use_adsl == True:
		dial_times = (target_num / per_dial_num) + 1
		logger.debug(">>>dial times=" + str(dial_times))
		remain_task = target_num

		for i in range(dial_times):
			# 
			logger.debug("###schedule times="  + str(i+1))
			ret = adsl_connect(adsl_name, adsl_user, adsl_password)
			time.sleep(1)
			#
			if remain_task > per_dial_num:
				bulk_task_num = per_dial_num
			else:
				bulk_task_num = remain_task
			remain_task = remain_task - per_dial_num
			
			state = perform_one_bulk(config_data, bulk_task_num)
			
			adsl_disconnect(adsl_name)

			# kill ie process
			util_process.killProcess(ie_process_name)
			
			time.sleep(1)
			
			if state != 0:
				break
	else:
		perform_one_bulk(config_data, target_num)
		
	# kill ie process
	util_process.killProcess(ie_process_name)

	notify_controller('QUIT')
	end = int(time.time())
	logger.debug(">>>Total run time=%.4d" % (end - start))

g_url_index = 0
def get_server_url(config):
	global g_url_index
	url_dict = config.get_target_url()
	url_keys =url_dict.keys()
	total = len(url_keys)
	key = url_keys[g_url_index]
	url = url_dict[key]
	g_url_index = g_url_index + 1
	if g_url_index >= total:
		g_url_index = 0
	return url
	
def perform_one_bulk(config, task_num):
	process_num = config.get_process_num()
	
	global g_task_queue, g_done_queue
	for i in range(task_num):
		server_url = get_server_url(config)
		g_task_queue.put(server_url)
	# Tell child processes to stop
	for i in range(process_num):
		g_task_queue.put('STOP')

	#
	#Start worker processes
	for i in range(process_num):
		p =Process(target=worker, args=(i, g_task_queue, g_done_queue))
		p.start()

	finished_task = 0
	failed_task = 0
	
	stop_count = 0
	for i in range(task_num):
		item = g_done_queue.get()
		if item == "STOP":
			logger.debug(">>>monitor recv STOP")
			stop_count = stop_count + 1
		else:
			(id, ret, sec) = item.get_result()
			if ret == 'OK':
				finished_task = finished_task + 1
			else:
				failed_task = failed_task + 1
			logger.debug("task:%d complete, sec=%d, result=%s" % (id, sec, ret))
		
		if stop_count >= process_num:
			logger.debug(">>>perform_one_bulk recv all worker stop msg")
			return -1

	logger.debug("finished_task=%d, failed_task=%d" % (finished_task, failed_task))
	return 0
	
def start():
	logger.info("run_pv_mp start...")
	start_controller()
	start_scheduler()
	
def stop():
	logger.info("run_pv_mp stop...")
	notify_controller('STOP')
	
#-----------------------------------------------------------------------
def main():
	'''
		Run from here.
	'''
	start()


if __name__ == '__main__':
	multiprocessing.freeze_support()
	main()
