# -*- coding: utf-8 -*-
#
#  Author: Jack Ding
#  E-Mail: jack.w.ding@gmail.com
#  Date: 09/14/2010
#  Version: 0.1
#

'''
python mysetup.py py2exe
'''
from distutils.core import setup
import py2exe

includes = ["encodings", "encodings.gbk", "encodings.utf_8", "util", "config_pv"]
#excludes = [ "MSVCP90.dll" ]
excludes = [ "" ]
options = {"py2exe":
					{"compressed" : 1, #压缩
					 "optimize" : 2,
					 "ascii" : 1,
					 "includes" : includes,
					 "dll_excludes" : excludes,
					 "bundle_files": 1 #所有文件打包成一个exe文件 }
					}
		}

#console=[{"script": "hello.py", "icon_resources": [(1, "hello.ico")] }]#源文件，程序图标
			
setup( windows=[{"script": "pv_generator.py", "icon_resources": [(1, "python.ico")]}], options = options,  version="1.0.0", zipfile = None)
#setup(console=[{"script": "run_pv_mp.py"}], options = options,  zipfile = None)
	
	