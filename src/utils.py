from os import path
import subprocess
from threading import Thread
from urllib.parse import urlparse
import re

try:
  from constants import *
except:
  from .constants import *


def render_icon_file(ext):

  file_types = {
                '.zip':ZIP_ICO, 

                '.7z':ARCHIVE_ICO, 
                '.rar':ARCHIVE_ICO, 
                '.sfx':ARCHIVE_ICO, 

                '.pdf':PDF_ICO, 

                '.jpg':IMAGE_ICO, 
                '.jpeg':IMAGE_ICO, 
                '.png':IMAGE_ICO, 

                '.mp4':VIDEO_ICO, 
                '.mkv':VIDEO_ICO, 

                '.mp3':AUDIO_ICO, 
              }
  return file_types.get(ext.lower(), FILE_ICO)


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



def threaded(fn):
    """To use as decorator to make a function call threaded.
    Needs import
    from threading import Thread"""
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper