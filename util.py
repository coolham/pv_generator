# -*- coding: utf-8 -*-
#
#  Author: Weijian Ding
#  Date: 05/14/2010


import sys
import httplib
import uuid
import logging
import hashlib

from xml.dom.minidom import parse, parseString, getDOMImplementation

"""
import pdb
pdb.set_trace()
	
p(print) 查看一个变量值
n(next) 下一步
s(step) 单步,可进入函数
c(continue)继续前进
l(list)看源代码


"""
version = "1.0.0"

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
logger = logging.getLogger('AppLog')

# # create console handler and set level to debug
ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter("%(asctime)-15s - %(name)-10s - %(levelname)-8s - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

logger = logging.getLogger('Module')
# # create console handler and set level to debug
ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter("%(asctime)-15s - %(name)-10s - %(levelname)-8s - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

logger = logging.getLogger('Network')
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


'''
<coolham>
	<register>
		<uid></uid>
		<mac></mac>
		<hostname></hostname>
		<client>
			<name></name>
			<version></version>
		<checksum></checksum>
'''
class RegisterClient():
	def __init__(self, client_name, client_ver):
		self.server_addr = 'maotoud.appspot.com'
		#self.server_addr = 'localhost:8888'
		self.server_uri = '/maotoud/register'
		self.clent_name = client_name
		self.client_ver = client_ver
		self.uid = None
		self.mac = None
		self.hostname = ''
	def get_node_id(self):
		self.uid = str(uuid.getnode())
		return self.uid 
	def get_mac_addr(self):
		node = uuid.getnode()
		self.uuid_mac = uuid.UUID(int=node)
		self.mac = self.uuid_mac.hex[-12:]
		return self.mac 
	def do_regist(self):
		print u"do_regist"
		self.get_node_id()
		self.get_mac_addr()
		
		self.conn = httplib.HTTPConnection(self.server_addr)
		request_url = self.server_addr + self.server_uri
		req_headers = {}
		req_headers['User-Angent'] = 'Mozilla/4.0'
		req_headers['Host'] = self.server_addr
		req_headers['Connection'] = 'Keep-Alive'
		
		h_str = u'<?xml version="1.0" encoding="utf-8"?>\n'
		b_str = self.encode_xml_data()
		req_body = h_str + b_str
		req_body = req_body.encode('utf-8')
		print u"body=", req_body
		self.conn.request("POST", self.server_uri, body = req_body, headers = req_headers )
		res = self.conn.getresponse()
		status = self.proc_reister_result(res)
		return status
	def proc_reister_result(self, res):
		if res.status == 200:
			result = res.getheader("Result")
			if result == "SUCCESS":
				print u"Register success."
			else:
				print u"Register failed:%s " % result
			return True
		else:
			print u"Register failed:." + res.reason
			return False
	def encode_xml_data(self):
		impl = getDOMImplementation()
		doc = impl.createDocument(None, "coolham", None)
		top_element = doc.documentElement
		
		snode = doc.createElement("register")
		
		node1 = doc.createElement("uid")
		tt = str(self.uid)
		text = doc.createTextNode(tt)
		node1.appendChild(text)
		snode.appendChild(node1)
		
		node1 = doc.createElement("mac")
		tt = str(self.mac)
		text = doc.createTextNode(tt)
		node1.appendChild(text)
		snode.appendChild(node1)

		node1 = doc.createElement("hostname")
		text = doc.createTextNode(self.hostname)
		node1.appendChild(text)
		snode.appendChild(node1)

		node1 = doc.createElement("client")
		node2 = doc.createElement("name")
		text = doc.createTextNode(self.clent_name)
		node2.appendChild(text)
		node1.appendChild(node2)
		node2 = doc.createElement("version")
		text = doc.createTextNode(self.client_ver)
		node2.appendChild(text)
		node1.appendChild(node2)
		snode.appendChild(node1)

		node1 = doc.createElement("checksum")
		tt = self.md5sum(self.uid)
		text = doc.createTextNode(tt)
		node1.appendChild(text)
		snode.appendChild(node1)

		top_element.appendChild(snode)
		
		return top_element.toxml()
	def md5sum(self, input):
		text = 'mahlooc728:' + input
		m = hashlib.md5()
		m.update(text)
		ret = m.hexdigest()
		return ret
		
def md5sum111(fname):   
	try:
		f = file(fname, 'rb')
	except:
		return 'Failed to open file'

	m = hashlib.md5()
	#m = md5.new()
	while True:
		d = f.read(8096)
		if not d:
			break
		m.update(d)
	ret = m.hexdigest()
	f.close()
	return ret

	
def cn_str(x):
	return x.decode("utf-8")
	
def check_str_type(ss):
	if isinstance(ss, unicode):
		print u"## unicode"
	else:
		#print u"## no unicode"
		try:
			unicode(ss, "ascii")
		except UnicodeError:
			#print u"## not ascii"
			try:
				unicode(ss, "utf-8")
			except UnicodeError:
				print u"## not utf-8"
			else:
				print u"## utf-8"
		else:
			# str was valid ASCII data
			print u"## ASCII"
			#pass
			

			
			