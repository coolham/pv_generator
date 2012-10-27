# -*- coding: utf-8 -*-
#
#  Author: Jack Ding
#  E-Mail: jack.w.ding@gmail.com
#  Date: 09/14/2010
#  Version: 0.1
#

import os
import sys
import logging
import random
import time
import socket
import httplib
import traceback 

import urllib2
import webbrowser 
import win32com.client
from win32com.client import Dispatch, constants

from network import *
from thread_pool import *
from config import *

cur_dir = os.getcwd()
sys.path.append(cur_dir)

LOG_FILENAME = 'logging.txt'
FORMAT = "%(asctime)-15s %(name)-10s %(levelname)-8s %(message)s"

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

if len(sys.argv) > 1:
    level_name = sys.argv[1]
    level = LEVELS.get(level_name, logging.NOTSET)
    logging.basicConfig(format=FORMAT, filename=LOG_FILENAME, level=level)
else:
	logging.basicConfig(level=logging.DEBUG, format=FORMAT, filename=LOG_FILENAME, )
	#logging.basicConfig(level=logging.INFO, format=FORMAT, filename=LOG_FILENAME, )

# Set up a specific logger with our desired output level
logger = logging.getLogger('PVLog')

# # create console handler and set level to debug
ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter("%(asctime)-15s - %(name)-10s - %(levelname)-8s - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)


'''
.encode(sys.getfilesystemencoding())
'''

DEFAULT_ENCODE = sys.getfilesystemencoding()


blog_addr = 'blog.sina.com.cn'
blog_path = '/zgrwzj'

fname = 'log'
f = file(fname, 'w')

class WebVisitor():
	logger = logging.getLogger('PVLog')
	server_url = blog_addr
	proxy_url = ''
	request_url = blog_path
	result = ''
	def __init(self):
		logger.debug("WebVisitor")

	def proc(self):
		content = urllib2.urlopen('http://blog.sina.com.cn/zgrwzj').read()
		return True

class BokerVisitor():
	logger = logging.getLogger('PVLog')
	proxy_url = ''
	result = ''
	def __init(self):
		logger.debug("BokerVisitor")
	
	def proc_http_requests(self, n, requests):
		index = 1
		while(index <= n):
			key1 = 'host_%d' % index
			host = requests[key1]
			key2 = 'uri_%d' % index
			uri = requests[key2]
			key3 = 'referer_%d' % index
			referer = requests[key3]
			self.http_request(host, uri, referer)
			index = index + 1
		return True
	def http_request(self, host, uri, referer):
		request_server = host
		request_uri = uri
		
		mnet = MNetwork(request_server)
		
		req_headers = {}
		req_headers['Accept-Language'] = 'zh-cn'
		req_headers['User-Angent'] = 'Mozilla/4.0'
		req_headers['Host'] = host
		req_headers['Connection'] = 'Keep-Alive'
		

		if len(referer) > 0:
			req_headers['referer'] = referer

		r, msg = mnet.post_http_request(request_uri, req_headers)
		if r == True:
			t = self.http_response(msg)
		else:
			t = 0

		mnet.close()
		
		return t
	def http_response(self, res):
		self.http_status = res.status
		self.http_reason = res.reason
		#print self.title, u" Status=", http_status, u" ", http_reason
		self.logger.info("proc_http_response: Status=%d Reason=%s", self.http_status, self.http_reason)
		
		return self.http_status
		
		if self.http_status == 200:
			#self.result = res.getheader("Result")
			#print self.title, u" Session-ID=", self.session
			#print u"Content-Length=", content_length
			msg =  res.read()
			#self.logger.debug("msg=%s", msg)
			#f.write(msg)
			return 
		else:
			self.logger.debug("http error:%d, %s", self.http_status, self.http_reason)

			
def visit_job(id, sleep = 0.001 ):  
    try:  
        #urllib.urlopen('http://192.168.1.242:8080/').read()  
		start = time.time()
		ie = Dispatch('InternetExplorer.Application')    
		ie.Visible = 0
		url = 'http://blog.sina.com.cn/zgrwzj'
		ie.Navigate(url)
		state = ie.ReadyState    			
		logger.debug("visit: %s", url)
		while 1:
			state = ie.ReadyState    
			if state ==4:   
				break
			time.sleep(1)
		state = None
		# end
		end = time.time()
		run_time = end - start
		t_str = " Elipse Time:%.2f s" % run_time
		if ret == True:
			r_str = "OK"
		else:
			r_str = "Failed"
		r_str = r_str + '\t' + t_str
		return r_str
    except Exception, e:  
        #print '[%4d]' % id, sys.exc_info()[:2]  
		exstr = traceback.format_exc() 
		logger.debug("test_job exception:%s", exstr)
		return "Exception"
		
  

	
class Main():
	worker_num = 1
	job_num = 1
	request_num = 0
	requests = {}
	def __init__(self):
		logger.info("Main init start")
	def run(self):
		logger.debug("run")
		#UtilConfigData.load_data("config.xml")
		#socket.setdefaulttimeout(10)  
		config_data = BlogerData("config.xml")
		self.requests = config_data.get_request_items("zgrwzj")
		self.request_num = config_data.get_count();
		#self.test_task()
		#visit_job(1)
		self.test_thread()
	def test_thread(self):
		#init thread_pool
		thread_pool = []
		#init mutex
		g_mutex = threading.Lock()
		## g_mutex.acquire() , g_mutex.release()
		
		for i in range(self.worker_num):
			th = threading.Thread(target=visit_job, args=(i, 0.01) ) ;
			thread_pool.append(th)
			
		# start threads one by one        
		for i in range(self.worker_num):
			thread_pool[i].start()
		
		#collect all threads
		for i in range(self.worker_num):
			threading.Thread.join(thread_pool[i]) 	
	def test_task(self):  
		logger.info('Start Task:')  
		start = time.time()
		wm = WorkerManager(self.worker_num)  
		num = self.job_num
		for i in range(num):  
			wm.add_job( visit_job, i, i*0.001 )  
		wm.start()  
		wm.wait_for_complete()  
		end = time.time()
		logger.info("Total num=%d", num)
		logger.info("Total run time=%.2f", (end - start))
		logger.info("End Task")
	def test_job(self, id, sleep = 0.001 ):  
		try:  
			#urllib.urlopen('http://192.168.1.242:8080/').read()  
			start = time.time()
			#boker = BokerVisitor()
			#ret = boker.proc_http_requests(self.request_num, self.requests);
			#url = 'http://blog.sina.com.cn/zgrwzj'
			#webbrowser.open_new_tab(url)
			#ie = win32com.client.Dispatch("InternetExplorer.Application")   
			#ie = win32com.client.Dispatch('Excel.Application')    
			# end
			end = time.time()
			run_time = end - start
			t_str = " Elipse Time:%.2f s" % run_time
			if ret == True:
				r_str = "OK"
			else:
				r_str = "Failed"
			r_str = r_str + '\t' + t_str
			return r_str
		except Exception, msg:  
			#print '[%4d]' % id, sys.exc_info()[:2]  
			exstr = traceback.format_exc() 
			print exstr
			#self.logger.debug("test_job exception:%s", exstr)
			#return "Exception"
			


if __name__ == '__main__':
	app = Main()
	app.run()  
	f.close()
	