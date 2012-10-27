# -*- coding: utf-8 -*-
#
#  Author: Jack Ding
#  E-Mail: jack.w.ding@gmail.com
#  Date: 09/14/2010
#  Version: 0.1
#

import os
import xml.parsers.expat
import threading
import logging
import subprocess
import traceback 

from xml.dom.minidom import parse, parseString, getDOMImplementation

import xml.parsers.expat  
#import xml.dom.minidom

from util import *

env_path = os.getenv('PATH')


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
			
#

class BlogerData():
	def __init__(self, filename):
		self.filename = filename
		self.level = 0
		self.requests = {}
		self.find_blog = False
		self.find_host = False
		self.find_uri = False
		self.find_referer = False
		self.index = 0;
	def get_request_items(self, blogname):
		self.index = 0;
		self.blogname = blogname
		p = xml.parsers.expat.ParserCreate()  
		p.StartElementHandler = self.start_element  
		p.EndElementHandler = self.end_element  
		p.CharacterDataHandler = self.char_data  
		p.returns_unicode = True  
		   
		f = file(self.filename)  
		p.ParseFile(f)  
		f.close()  
		return self.requests
	def start_element(self, name, attrs):  
		if name == 'blog':
			self.find_blog = True
		elif name == 'request':
			self.index += 1
		elif name == 'host':
			self.find_host = True
		elif name == 'uri':
			self.find_uri = True
		elif name == 'referer':
			self.find_referer = True
		self.level = self.level + 1  
	def end_element(self, name):  
		if name == 'blog':
			self.find_blog = False
		self.level = self.level - 1  
	def char_data(self, data):  
		data = data.strip(' ').strip('\n')
		if self.find_host:
			key = 'host_%d' % self.index
			value = data.encode('utf-8')
			self.requests[key] = value
			self.find_host = False
		if self.find_uri:
			key = 'uri_%d' % self.index
			value = data.encode('utf-8')
			self.requests[key] = value
			self.find_uri = False
		if self.find_referer:
			key = 'referer_%d' % self.index
			value = data.encode('utf-8')
			self.requests[key] = value
			self.find_referer = False
	def get_count(self):
		return self.index
	def print_data(self):
		print u""
#
#
class UtilConfigData(object):
	logger = logging.getLogger('PVLog')

	platform = ""
	compile_target = "" # "Emulator WINSCW UDEB", "Phone GCCE DEBUG", "Phone GCCE RELEASE"
	sdk_path_dict = {}
	project_build_files = []
	# build_options[project_id][]
	build_options = [["" for x in range(10)] for y in range(10)]
	__inst = None # make it so-called private  
	__lock = threading.Lock() # used to synchronize code  
	
	def __init__():  
		"disable the __init__ method"  
	@staticmethod  
	def getInst():  
		UtilConfigData.__lock.acquire()  
		if not UtilConfigData.__inst:  
			UtilConfigData.__inst = object.__new__(UtilConfigData)  
			object.__init__(UtilConfigData.__inst) 
		UtilConfigData.__lock.release()  
		return UtilConfigData.__inst  
	@staticmethod  
	def __reset_data():
		UtilConfigData.platform = ""
		UtilConfigData.sdk_path = ""
		UtilConfigData.symbian_project = []
	
	@staticmethod  
	def load_data(file_name):
		UtilConfigData.logger.debug("UtilConfigData:load_data()")
		UtilConfigData.__reset_data()
		try:
			f = open(file_name, 'r')
			str = f.read()
			#print u"str=", str
			f.close()
			UtilConfigData.handle_input_xml(str)
		except:
			UtilConfigData.logger.error("UtilConfigData:load_data() failed!")
			print u"Can not load data:", file_name
			UtilConfigData.__reset_data()
	@staticmethod  
	def save_data(file_name):
		UtilConfigData.logger.debug("UtilConfigData:save_data()")
		str = UtilConfigData.encode_xml_data()
		f = open(file_name,'w')
		t = str.encode('utf=8')
		f.write(t)
		f.close()
	@staticmethod  
	def handle_input_xml(xml_data):
		try:
			#UtilConfigData.logger.debug("UtilConfigData:handle_input_xml=%s", xml_data.decode('utf-8').encode('gb2312'))
			dom = parseString(xml_data)
			blog_node = dom.getElementsByTagName('visit-blog')[0]
			print blog_node
			UtilConfigData.parse_visti_blog(blog_node)
		except Exception, e:
			exstr = traceback.format_exc() 
			print exstr
			
	@staticmethod  
	def parse_visti_blog(blog_node):
		node2ss = blog_node.getElementsByTagName('blog')
		
		for node2s in node2ss:
			print u"blog=", node2s.toxml()
			blog_name = node2s.attributes['name'].value
			print u"blog_name=", blog_name
			#node_items = node2s.getElementsByTagName('request-items')[0]

	@staticmethod  
	def parse_platform_data(client_node):
		print u"client_node=", client_node.toxml()
		node1s = client_node.getElementsByTagName('platform')[0]
		#print u"node1s=", node1s
		for node1 in node1s.childNodes:
			if node1.nodeType == node1.TEXT_NODE:
				UtilConfigData.platform = node1.data
				UtilConfigData.logger.debug("platform=%s", UtilConfigData.platform)
				return True
			
		UtilConfigData.logger.debug("Error:parse_platform_data: can not find platform")
		return False
	@staticmethod  
	def parse_compile_target(client_node):
		#print u"client_node=", client_node.toxml()
		node1s = client_node.getElementsByTagName('build-config')[0]
		#print u"node1s=", node1s
		for node1 in node1s.childNodes:
			if node1.nodeType == node1.TEXT_NODE:
				UtilConfigData.compile_target = node1.data
				UtilConfigData.logger.debug("compile_target=%s", UtilConfigData.compile_target)
				return True
			
		UtilConfigData.logger.debug("Error:parse_platform_data: can not find compile_target")
		return False
	@staticmethod  
	def parse_project_info(client_node):
		node1s = client_node.getElementsByTagName('symbian-projects')[0]
		node2ss = node1s.getElementsByTagName('project')
		
		project_id = 0
		for node2s in node2ss:
			print u"node2s=", node2s.toxml()
			node_bld = node2s.getElementsByTagName('build-file')[0]
			for node_bld_t in node_bld.childNodes:
				if node_bld_t.nodeType == node_bld_t.TEXT_NODE:
					print u"bld file=", node_bld_t.data
					UtilConfigData.project_build_files.append(node_bld_t.data)
			node_options = node2s.getElementsByTagName('build-options')[0]		
			mode_cmds = node_options.getElementsByTagName('command')
			
			for node_cmd in mode_cmds:
				print u"node_cmd=", node_cmd.toxml()
				cmd = node_cmd.childNodes[0]
				if cmd.nodeType == cmd.TEXT_NODE:
					print u"cmd=", cmd.data
					UtilConfigData.build_options[project_id].append(cmd.data)


			project_id += 1
			
	@staticmethod  
	def encode_xml_data():
		print u"encode_xml_data"
		impl = getDOMImplementation()
		newdoc = impl.createDocument(None, "mas", None)
		top_element = newdoc.documentElement
		
		snode = newdoc.createElement("env")
		# SDK config
		for sdk_str in UtilConfigData.sdk_path_dict.keys():
			print u"sdk=%s,path=%s" % (sdk_str, UtilConfigData.sdk_path_dict[sdk_str])
			sdk_node = newdoc.createElement("sdk")
			sdk_ver_node = newdoc.createElement("sdk-ver")
			text = newdoc.createTextNode(sdk_str)
			sdk_ver_node.appendChild(text)
			sdk_path_node = newdoc.createElement("sdk-path")
			text = newdoc.createTextNode(UtilConfigData.sdk_path_dict[sdk_str])
			sdk_path_node.appendChild(text)
			sdk_node.appendChild(sdk_ver_node)
			sdk_node.appendChild(sdk_path_node)
			snode.appendChild(sdk_node)
		top_element.appendChild(snode)
		
		snode = newdoc.createElement("mobile-client")
		# platform
		p_node = newdoc.createElement("platform")
		text = newdoc.createTextNode(UtilConfigData.platform)
		print u"platform=", UtilConfigData.platform
		p_node.appendChild(text)
		snode.appendChild(p_node)
		
		# build config: Emulator, Debug GCCE....
		p_node = newdoc.createElement("build-config")
		text = newdoc.createTextNode(UtilConfigData.compile_target)
		print u"compile_target=", UtilConfigData.compile_target
		p_node.appendChild(text)
		snode.appendChild(p_node)

		# SDK path
		# p_node = newdoc.createElement("sdk-path")
		# text = newdoc.createTextNode(UtilConfigData.sdk_path)
		# print u"sdk=", UtilConfigData.sdk_path
		# p_node.appendChild(text)
		# snode.appendChild(p_node)
		
		# Symbian Project
		ps_node = newdoc.createElement("symbian-projects")
		id = 0
		for x in UtilConfigData.project_build_files:
			print u"symbian-projects=", x
			p_node = newdoc.createElement("project")
			bld_node = newdoc.createElement("build-file")
			text = newdoc.createTextNode(x)
			bld_node.appendChild(text)
			p_node.appendChild(bld_node)
			o_node = newdoc.createElement("build-options")
			tt = UtilConfigData.build_options[id]
			for cmd in tt:
				if cmd <> '':
					c_node = newdoc.createElement("command")
					cmd_text = newdoc.createTextNode(cmd)
					c_node.appendChild(cmd_text)
					o_node.appendChild(c_node)
			p_node.appendChild(o_node)
			ps_node.appendChild(p_node)
			id += 1
		snode.appendChild(ps_node)

		top_element.appendChild(snode)
		
		return top_element.toxml()
		
	@staticmethod  
	def get_sdk_list():
		print u"sdk list=", UtilConfigData.sdk_path_dict.keys()
		return UtilConfigData.sdk_path_dict.keys()
	@staticmethod  
	def set_platform(platform_str):
		UtilConfigData.platform = platform_str
	@staticmethod  
	def get_platform():
		return UtilConfigData.platform
	@staticmethod  
	def set_sdk_path(sdk, sdk_path):
		UtilConfigData.logger.debug("set_sdk_path:%s=%s", sdk, sdk_path)
		UtilConfigData.sdk_path_dict[sdk] = sdk_path
	@staticmethod  
	def get_sdk_path(sdk):
		if sdk in UtilConfigData.sdk_path_dict.keys():
			return UtilConfigData.sdk_path_dict[sdk]
		else:
			return ""
	@staticmethod  
	def set_project_info_list(bld_file_list):
		UtilConfigData.logger.debug("set_project_info:%s", bld_file_list)
		UtilConfigData.project_build_files = bld_file_list
	@staticmethod  
	def get_project_build_files():
		# project_build_files[]
		return UtilConfigData.project_build_files
	@staticmethod  
	def get_compile_target():
		return UtilConfigData.compile_target
	@staticmethod  
	def set_compile_target(config):
		UtilConfigData.compile_target = config
	@staticmethod  
	def get_build_option(project_id):
		return UtilConfigData.build_options[project_id]
	@staticmethod  
	def set_build_option(project_id, options):
		print u"set_build_option=", options
		UtilConfigData.build_options[project_id] = options
		
	@staticmethod  
	def gen_script_file():
		f = open('run.bat','w')
		# SET EPOCROOT
		sdk_path = UtilConfigData.sdk_path_dict[UtilConfigData.platform]
		tt = sdk_path.split(':')
		#print u"sdk_path=", sdk_path
		epocroot = "%s\\" % (tt[1])
		t_str = "SET EPOCROOT=%s\n" % epocroot
		f.write(t_str)
		#
		t_str = "REM \n"
		f.write(t_str)
		drive = "C:"
		count = 0
		for project in UtilConfigData.project_build_files:
			#
			UtilConfigData.logger.info("gen_script_file:project=%s", project)
			t_str = "REM project:%s\n" % project
			f.write(t_str)
			path = os.path.dirname(project)
			print u"path=%s" % path
			t_str = "cd %s\n" % path
			f.write(t_str)
			#
			cmd_list = UtilConfigData.build_options[count]
			print u"cmd_list=", cmd_list
			t_str = ""
			for x in cmd_list:
				if x <> "":
					tt = ''
					if x.find('bldmake') >= 0:
						# set EPOCROOT && C: && cd path && bldmake xxxx
						#tt = "SET EPOCROOT=%s && %s && cd %s && %s\n" % (epocroot, drive, path, x)
						tt = "%s && cd %s && %s\n" % (drive, path, x)
					elif x.find('abld') >= 0:
						# set EPOCROOT && C: && path/abld ...
						#tt = "SET EPOCROOT=%s && %s && %s\\%s\n" % (epocroot, drive, path, x)
						tt = "%s && %s\\%s\n" % (drive, path, x)
					t_str += tt
			t_str += "\n"
			f.write(t_str)
		f.close()
	@staticmethod  
	def run_script_file():
		f = open('run.bat', 'r')
		cmds = f.readlines()
		f.close()
		#print cmds
		for command in cmds:
			print u"command=%s" % command
			#check_str_type(command)
			tt = command.encode('ascii')
			#check_str_type(tt)
			#print u"command=%s" % tt
			#p = os.popen(tt)
			#print p.readlines()
			p = subprocess.Popen(tt, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
					env={"EPOCROOT" : "\\Symbian\\9.1\\S60_3rd_MR\\", "PATH" : env_path })
			stdoutdata, stderrdata = p.communicate()
			print stderrdata
			print u"returncode=", p.returncode
			if p.returncode != 0:
				print u"command failed!"
				print stderrdata
				return
			else:
				print u"command success"
	@staticmethod  
	def print_all():
		print u"----- All Service Data ------"
		
	# @staticmethod  
	# def print_caller_notify():
		# print u"Caller Notify:"
		# for x in UtilConfigData.notify_array:
			# if x[0] <> "":
				# print x		

	# @staticmethod  
	# def print_caller_notify_to_str():
		# str = "Caller Notify Data:\n"
		# for x in UtilConfigData.notify_array:
			# if x[0] <> "":
				# str = str + x[0] + u" " + x[1] + u" " + x[2] + u" " + x[3]
		# return str
	# @staticmethod  
	# def print_voice_mail():
		# print u"Voice Mail:"
		# for x in UtilConfigData.voice_mail:
			# if x[0] <> "":
				# print x		
				