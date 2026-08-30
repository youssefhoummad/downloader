from os import path, remove
import subprocess
from urllib.parse import urlparse
import re
import os

import subprocess
import threading
from urllib.parse import urlparse
from typing import Callable, Any
from os import path, remove

from win32com.shell import shell, shellcon # type: ignore
from PIL import Image, ImageTk  
import win32api  
import win32con  
import win32ui  
import win32gui 

# from pytube import YouTube




def is_youtube_link(url: str) -> bool:
    return 'youtube.com' in url or 'youtu.be' in url


def open_path(dst: str) -> None:
    """فتح المجلد الذي يحتوي على الملف بأمان"""
    try:
        os.startfile(dst) # أكثر أماناً من subprocess.Popen
    except AttributeError: # لنظام غير Windows
        subprocess.run(['open', dst] if os.name == 'posix' else ['xdg-open', dst])


def youtube_direct_link(url: str, dest: str):
    from pytube import YouTube
    yt = YouTube(url)
    stream = yt.streams.first()
    if not stream:
        raise ValueError("لم يتم العثور على مقاطع صالحة لهذا الفيديو.")
    
    dl_url = stream.url
    # تنظيف اسم الملف من الأحرف غير الصالحة
    safe_title = re.sub(r'[^\w\-_\. ]', '_', stream.title)[:40]
    filename = f"{safe_title}.mp4"
    dst = path.join(dest, filename)
    
    return dl_url, dst, filename


def get_icon(ext, size='large'):  

  file = open(f"temp{ext}", "w") 
  file.close() 

  PATH = f'temp{ext}'

  SHGFI_ICON = 0x000000100  
  SHGFI_ICONLOCATION = 0x000001000  
  if size == "small":  
    SHIL_SIZE= 0x00001  
  elif size == "large":  
    SHIL_SIZE= 0x00002  
  else:  
    raise TypeError("Invalid argument for 'size'. Must be equal to 'small' or 'large'")  
  ret, info = shell.SHGetFileInfo(PATH, 0, SHGFI_ICONLOCATION | SHGFI_ICON | SHIL_SIZE)  
  hIcon, iIcon, dwAttr, name, typeName = info  
  ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)  
  hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))  
  hbmp = win32ui.CreateBitmap()  
  hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_x)  
  hdc = hdc.CreateCompatibleDC()  
  hdc.SelectObject(hbmp)  
  hdc.DrawIcon((0, 0), hIcon)  
  win32gui.DestroyIcon(hIcon)  
  
  bmpinfo = hbmp.GetInfo()  
  bmpstr = hbmp.GetBitmapBits(True)  
  img = Image.frombuffer(  
    "RGBA",  
    (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),  
    bmpstr, "raw", "BGRA", 0, 1  
  )  

  remove(PATH)
  
  if size == "small":  
    img = img.resize((16, 16), Image.ANTIALIAS)  

  img = ImageTk.PhotoImage(img)
  return img


def is_downloaded(url, dst):
  head, tail = path.split(url)
  return path.exists(dst+tail)


def open_path(url, dst):
  head, tail = path.split(url)
  # print(dst, tail)
  subprocess.Popen(r'explorer /select,"{}"'.format(dst+ '\\' +tail))





if __name__ == '__main__':
  import tkinter as tk
  root = tk.Tk()
  ext = get_icon('.mp4')
  tk.Label(image=ext).pack()
  root.mainloop()