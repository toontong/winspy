#coding:utf-8
#Author: ChuanTong.Huang@Gmail.com 
#Dete: 2016-06-06

import os, re
import time
import win32gui
import win32api
import win32con
import win32com
import win32com.client
import win32process
import traceback

def set_foreground(hwnd):
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(hwnd)

def find_process_pids(porcess_name):
    pids = []  
    for pid in win32process.EnumProcesses():  
        try:  
            hProcess = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)  
            hProcessFirstModule = win32process.EnumProcessModules(hProcess)[0]  
            processName = os.path.basename(win32process.GetModuleFileNameEx(hProcess, hProcessFirstModule))

            if processName.find(porcess_name) >= 0:  
                pids.append(pid)  
        except Exception, e:  
            # print "on list_process(): ", e 
            # traceback.print_exc()
            pass
    return pids

def get_hwnds_form_pid (pid):
    def callback (hwnd, hwnds):
        if win32gui.IsWindowVisible (hwnd) and win32gui.IsWindowEnabled (hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId (hwnd)
            if found_pid == pid:
                #print "find PID:[ ", pid, "] of hwnd=", hwnd
                hwnds.append (hwnd)
            return True
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds

def main():
    pids = find_process_pids("LedPlayer_K_")
    print pids
    for pid in pids:
        print get_hwnds_form_pid(pid)

if __name__ == '__main__':
    main()