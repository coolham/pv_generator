# -*- coding: utf-8 -*-
#
#  Author: Jack Ding
#  E-Mail: jack.w.ding@gmail.com
#  Date: 09/14/2010
#　Version: 0.1
#

import ctypes
import sys
import win32com.client
import subprocess
import time


def check_exsit(process_name):
	WMI = win32com.client.GetObject('winmgmts:')
	processCodeCov = WMI.ExecQuery('select * from Win32_Process where Name="%s"' % process_name)
	if len(processCodeCov) > 0:
		print '%s is exists' % process_name
	else:
		print '%s is not exists' % process_name


TH32CS_SNAPPROCESS = 0x00000002
class PROCESSENTRY32(ctypes.Structure):
     _fields_ = [("dwSize", ctypes.c_ulong),
                 ("cntUsage", ctypes.c_ulong),
                 ("th32ProcessID", ctypes.c_ulong),
                 ("th32DefaultHeapID", ctypes.c_ulong),
                 ("th32ModuleID", ctypes.c_ulong),
                 ("cntThreads", ctypes.c_ulong),
                 ("th32ParentProcessID", ctypes.c_ulong),
                 ("pcPriClassBase", ctypes.c_ulong),
                 ("dwFlags", ctypes.c_ulong),
                 ("szExeFile", ctypes.c_char * 260)]

def getProcList():
    CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
    Process32First = ctypes.windll.kernel32.Process32First
    Process32Next = ctypes.windll.kernel32.Process32Next
    CloseHandle = ctypes.windll.kernel32.CloseHandle
    hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    pe32 = PROCESSENTRY32()
    pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
    if Process32First(hProcessSnap,ctypes.byref(pe32)) == False:
        print >> sys.stderr, "Failed getting first process."
        return
    while True:
        yield pe32
        if Process32Next(hProcessSnap,ctypes.byref(pe32)) == False:
            break
    CloseHandle(hProcessSnap)

def getChildPid(pid):
    procList = getProcList()
    for proc in procList:
        if proc.th32ParentProcessID == pid:
            yield proc.th32ProcessID
   
def killPid(pid):
    childList = getChildPid(pid)
    for childPid in childList:
        killPid(childPid)
    handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
    ctypes.windll.kernel32.TerminateProcess(handle,0)

def getPid(process_name):
	'''
		maybe more than one pid
	'''
	#print u"get %s pid" % process_name
	procList = getProcList()
	pids = []
	for proc in procList:
		if proc.szExeFile == process_name:
			pid = proc.th32ProcessID
			#print u"find process:%s pid=%s" % (process_name, str(pid))
			pids.append(pid)
	return pids
	
def killProcess(process_name):
	pids = getPid(process_name) 
	for pid in pids:
		killPid(pid)
		
def listProcess():
	procList = getProcList()
	for proc in procList:
		print proc.szExeFile + ',parent_id=' + str(proc.th32ParentProcessID) + ', pid=' + str(proc.th32ProcessID)

#----------------------
#
# Usage demo
#
#----------------------
def test_kill():
	timeout = 2
	process = subprocess.Popen("cmd /k ping localhost -t",shell = True)
	start = int(time.time())
	while process.poll()==None:
		now = int(time.time())
		if int (now - start) >timeout:
			pid = process.pid
			break

	winproc.killPid(pid)
	print "End"
	
if __name__ == '__main__':
    args = sys.argv
    if len(args) >1 :
        pid = int(args[1])
        killPid(pid)
    else:
		killProcess("iexplore.exe")
	#check_exsit('iexplore.exe')