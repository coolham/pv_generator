# -*- coding: utf-8 -*-
#
#  Author: Weijian Ding
#
#

import socket
import httplib
import logging
import traceback 



class MNetwork():
	def __init__(self, server_url, proxy_url=''):
		self.logger = logging.getLogger('PVLog')
		self.logger.debug("MNetwork: server=%s, proxy=%s", server_url, proxy_url)
		self.server_url = server_url
		self.proxy_url = proxy_url
	def post_http_request(self, request_url, req_headers, req_body = ""):
		temp = req_body
		temp = temp.decode('utf-8')
		self.logger.debug("MNetwork:post_request: server=%s request_url=%s, req_headers=%s, req_body=%s",\
					self.server_url, request_url, req_headers, temp )

		socket.setdefaulttimeout(15)

		flag = False
		try:
			#print u"proxy_url=%s" % self.proxy_url
			if self.proxy_url == '':
				self.logger.debug("HTTPConnection:%s", self.server_url)
				self.conn = httplib.HTTPConnection(self.server_url)		
			else:
				# connect server via proxy
				request_url = self.server_url + request_url
				self.logger.debug("HTTPConnection: via proxy=%s, Sever=%s, request=", self.proxy_url, self.server_url, request_url)
				self.conn = httplib.HTTPConnection(self.proxy_url)		
			
			#conn.set_debuglevel(5)
			if req_body == "":
				self.conn.request("GET", request_url, headers = req_headers)
			else:
				self.conn.request("GET", request_url, body = req_body, headers = req_headers )
			res = self.conn.getresponse()
			# close conn
			flag = True
		except socket.error, msg:
			exstr = traceback.format_exc() 
			self.logger.debug("socket.error:%s", exstr)
		except httplib.HTTPException, msg:
			exstr = traceback.format_exc() 
			self.logger.debug("httplib.HTTPException:%s", exstr)
		except Exception, msg:
			exstr = traceback.format_exc() 
			self.logger.debug("Exception:%s", exstr)
		
		# close connnection
		# you should not close connection at this time, since the caller class will read http body later (res.read())
		#self.conn.close()
		# 	
		if flag == True:
			self.logger.debug("post_http_request success:%s", request_url)
			return flag, res
		else:
			self.logger.debug("post_http_request failed:%s", request_url)
			return flag, exstr

	def close(self):
		"Note!: you should call this method after you finishe reading http body"
		self.conn.close()