#coding:utf-8
#Author: ChuanTong.Huang@Gmail.com 
#Dete: 2016-06-06

import os, re
import ctypes
import math
import operator
import time
import win32gui
import win32api
import win32con
import win32process
import socket, threading, time
import traceback
import winmgr
import logging


EXE_NAME = "LedPlayer_"
click_sleep = 0.1

class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_int),  
                ('top', ctypes.c_int),  
                ('right', ctypes.c_int),  
                ('bottom', ctypes.c_int)]
   

class LedPlayer(object):
    """docstring for LedPlayer"""
    def __init__(self,  hwnd, rect):
        super(LedPlayer, self).__init__()
        self.hwnd = hwnd
        if rect.left == rect.right or rect.top == rect.bottom:
            rect.left = 0
            rect.top = 0
            # 直接使用屏幕大小
            rect.right = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            rect.bottom = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        self.rect = rect

    def isplaying(self):
        winmgr.set_foreground(self.hwnd)
        self.playBar = win32gui.FindWindow("TJingJian_Player_form", "JingJian_Player_form")
        if not self.playBar:
            raise Exception("windows(classname=TJingJian_Player_form) not Found.")

        self.playing = bool(win32gui.IsWindowVisible(self.playBar))

        if self.playing and self.hwnd != self.playBar:
            self.hwnd = self.playBar
            winmgr.set_foreground(self.hwnd)
            ctypes.windll.user32.GetWindowRect(self.playBar, ctypes.byref(self.rect))

        return self.playing
        logging.info("parent\t->%#X", self.hwnd)
        logging.info("playBar\t->%#X" % self.playBar)
        logging.info("playing\t->%s",self.playing)
        return self.playing

    def get_main_hwnds(self):
        hwnds = []
        result = []
        retry = 10  # 窗口从播放切换回主窗体的间隔，可能会看不见，所以使用retry+sleep
        sleep = 0.1  
        while retry > 0:
            pids = winmgr.find_process_pids(EXE_NAME)
            for pid in pids:
                hwnds.extend(winmgr.get_hwnds_form_pid(pid))
            for hwnd in hwnds:
                winmgr.set_foreground(hwnd)
                time.sleep(0.1)
                rect = RECT()
                # 必需把主窗置前后，并能获取大于零的rect，才是正确的hwnd
                ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect)) 
                if rect.left == rect.right or rect.top == rect.bottom:
                    logging.warning("\trect not found, hwnd can not used. ")
                    continue
                result.append((hwnd, rect))
            if result:
                break
            time.sleep(sleep * (11 - retry ))
            retry -= 1
        return result

    def get_play_button_pos(self):
        if not self.isplaying():
            return self.rect.left + 400, self.rect.top + 65
        else:
            return self.rect.left + 28, self.rect.top + 28

    def get_stop_button_pos(self):
        if self.isplaying():
            return self.rect.left + 105, self.rect.top + 25
        else:
            return self.rect.left + 800, self.rect.top + 145

    def get_pause_button_pos(self):
        if self.isplaying():
            return self.rect.left + 65, self.rect.top + 25
        else:
            return self.rect.left + 695, self.rect.top + 145

    def get_preview_button_pos(self):
        return self.rect.left + 638, self.rect.top + 145
    
    def get_play_as_video_button_pos(self):
        return self.rect.left + 225, self.rect.top + 145
    
    def get_play_as_screenshots_button_pos(self):
        return self.rect.left + 305, self.rect.top + 145

    def get_mode_button_pos(self, index):
        if not (1 <= index <= 16):
            raise Exception("mode index must be 1~16.")
        offset_x, offset_y =  60, 130
        if self.isplaying():
            offset_x, offset_y = 170, 16 # 播放状态下，“模式1”位置
            W = 55
            if index > 8:
                offset_y = 45
                index -= 8
            offset_x +=(index-1) * W

        else:
            offset_x, offset_y =  60, 130
            H, W = 30, 70
            if index % 2 == 0: # 偶数
               offset_x += 70
            offset_y += ((index-1)/2) * H
        
        return (self.rect.left + offset_x, 
                self.rect.top + offset_y)

    def click_mode(self, index=14):
        x,y = self.get_mode_button_pos(index)
        self.click(x, y , "mode-%d" % index)
    
    def _left_click(self, x, y, name):
        logging.info("\tclick-> [%s]  pos(%d,%d)" , name, x, y)
        win32api.SetCursorPos([x, y])
        try:
            ctypes.windll.user32.SwitchToThisWindow(self.hwnd, True)
        except Exception, e:
            logging.warning("SwitchToThisWindow err=[%s] used mouse click.", e)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0,0,0) 
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0,0,0)

        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0,0,0) 
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0,0,0)
        time.sleep(click_sleep)

    def click_jiemu(self):
        if self.isplaying():
            return

        # 点击 "节目" tab
        x, y = self.rect.left + 70, self.rect.top + 90
        self._left_click(x, y, "tab")
        

    def click(self, x, y, name=""):
        self.click_jiemu()
        self._left_click(x, y, name)

    def click_play(self):
        x, y = self.get_play_button_pos()
        self.click(x, y, "play")

    def click_stop(self):
        x, y = self.get_stop_button_pos()
        self.click(x, y, "stop")

    def click_pause(self):
        x, y = self.get_pause_button_pos()
        self.click(x, y, "pause")

    def click_preview(self):
        if self.isplaying():
            self.click_stop()

        x, y = self.get_preview_button_pos()
        self.click(x, y, "preview")

    def click_play_as_video(self):
        if self.isplaying():
            self.click_stop()

        x, y = self.get_play_as_video_button_pos()
        self.click(x, y, "play_as_video")

    def click_play_as_screenshots(self):
        if self.isplaying():
            self.click_stop()

        x, y = self.get_play_as_screenshots_button_pos()
        self.click(x, y, "play_as_screenshots")

def iter_windows():
    retry = 120 # 
    sleep = 1
    hwnds = []
    pids = []
    while retry > 0:
        retry -= 1
        
        pids = winmgr.find_process_pids(EXE_NAME)
        if not pids:
            logging.error("[LedPlayer] not running ???")
            time.sleep(sleep)
            continue

        if len(pids) > 1: 
            logging.error("[LedPlayer] running more then 1 process ? Pls kill other.")
            time.sleep(sleep)
            continue
        
        for pid in pids:
            hwnds.extend( winmgr.get_hwnds_form_pid(pid) )
        
        if not hwnds:
            time.sleep(sleep)
            continue
        else:
            break

    rect = RECT()

    for hwnd in hwnds:
        winmgr.set_foreground(hwnd)
        time.sleep(0.1)
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))#获取当前窗口坐标
        
        if rect.left == rect.right or rect.top == rect.bottom:
            continue

        win = LedPlayer(hwnd, rect)
        logging.info("\tretry[%d]s then found LedPlayer HWND:->%#x",(120 - retry), hwnd)
        logging.info("\tHWND[%d] Rect->(%s,%s,%s,%s) playing=[%s] hwnds-len=[%d]",
            hwnd, rect.left, rect.top, rect.right, rect.bottom,  win.isplaying(), len(hwnds))
        return win

    logging.error("hwnd and rect not found. in the hwnds=%s ; pids=%s",hwnds, pids)
    return None

def main():
    win =  iter_windows()
    assert(win)
    global click_sleep
    click_sleep=2
    
    iter_windows().click_preview()
    time.sleep(click_sleep)
    iter_windows().click_play_as_video()
    return
    for i in range(1, 5):
        iter_windows().click_mode(i)
        iter_windows().click_play()
        time.sleep(1)
        if i &0x1: iter_windows().click_stop()


    return

    for c in clicks:
        getattr(iter_windows(), c)()
        time.sleep(1)

if __name__ == '__main__':
    main()