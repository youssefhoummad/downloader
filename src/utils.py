from os import path, remove
import subprocess
from threading import Thread
from urllib.parse import urlparse
import re

from win32com.shell import shell, shellcon  
from PIL import Image, ImageTk  
import win32api  
import win32con  
import win32ui  
import win32gui 

from pytube import YouTube

try:
  from constants import *
except:
  from .constants import *


def threaded(fn):
    """To use as decorator to make a function call threaded.
    Needs import
    from threading import Thread"""
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper




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


def get_filename_from_url(url):
  # https://stackoverflow.com/a/18727481
  a = urlparse(url)
  return os.path.basename(a.path)

def open_path(url, dst):
  head, tail = path.split(url)
  # print(dst, tail)
  subprocess.Popen(r'explorer /select,"{}"'.format(dst+ '\\' +tail))


def is_url(url):
  # https://stackoverflow.com/a/7160778
  regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

  return re.match(regex, url) is not None


def is_youtube_link(url):
  # https://stackoverflow.com/a/19161373
  return ('youtube.com' in url) or ('youtu.be' in url)
  # regex = (
  #       r'(https?://)?(www\.)?'
  #       '(youtube|youtu|youtube-nocookie)\.(com|be)/'
  #       '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
  # return re.match(regex, url) is not None


def validator(url, dst=DEST):
  if not url:
    return '* no URL given !!'

  if not is_url(url): 
    return '* Entre a valid URl please'

  if is_downloaded(url, dst):
    return '* This file is exist, delete it if you want redownload..'
  
  return 0


def youtube_direct_link(url):
  yt = YouTube(url)
  url = yt.streams.first().url
    
  title = yt.streams[0].title
  try:
    title = title[:20].replace(' ', '_') + '.mp4'
  except:
    title = title.replace(' ', '_') + '.mp4'

  dst = os.path.join(DEST, title)
  
  return url, dst, title




if __name__ == '__main__':
  get_icon('zip')