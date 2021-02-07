import os
from datetime import datetime
import threading
import time
import ntpath

import tkinter as tk
from tkinter import ttk

from pySmartDL import SmartDL


try:
  from .win10toast import ToastNotifier
  from .imageLabel import ImageLabel
  from .buttons import *
  from .constants import *
  from .utils import *
except:
  from win10toast import ToastNotifier
  from imageLabel import ImageLabel
  from buttons import *
  from constants import *
  from utils import *

toaster = ToastNotifier()

class DownloadItem(tk.Frame):
  def __init__(self, parent, dl):
    tk.Frame.__init__(self, parent)
    self.config(bg=parent['bg'])
    self.parent = parent

    # self.url =s url
    # self.dl_object = dl
    
    self.progress = tk.StringVar()
    self.progress.set('0%')
    self.speed = tk.StringVar()
    self.speed.set('-- kB/s')
    self.size = tk.StringVar()
    self.size.set('-- MB')
    self.time = tk.StringVar()
    self.time.set('-m -s')

    # self.init_UI()
    

  def init_UI(self):
    _f = tk.Frame(self, bg=self['bg'])
    _f.pack(ipady=3)

    self.ico = get_icon(self.extension)
    self._icon = tk.Label(_f, text="", image=self.ico, bg=self['bg'])
    # self._progress = ttk.Progressbar(_f, length=100)
    self._name = tk.Label(_f, text=self.filename, bg=self['bg'], width=26, anchor='nw')
    self._progress = tk.Label(_f, textvariable=self.progress, bg=self['bg'], width=8)
    self._speed = tk.Label(_f, textvariable=self.speed, bg=self['bg'], width=10)
    self._size = tk.Label(_f, textvariable=self.size, bg=self['bg'], width=10)
    self._time = tk.Label(_f, textvariable=self.time, bg=self['bg'], width=12)
    self._pause = ButtonPause(_f, command=self.pause_download)
    self._cancel = ButtonCancel(_f, command=self.cancel_download)


    self._icon.pack(side='left', padx=(5,0))
    self._name.pack(side='left', padx=(5, 0))
    self._progress.pack(side='left', padx=(5, 0))
    self._speed.pack(side='left', padx=(5, 0))
    self._size.pack(side='left', padx=(5, 0))
    self._time.pack(side='left', padx=(5, 0))
    self._pause.pack(side='left', padx=(5, 0))
    self._cancel.pack(side='left', padx=(5, 10))
  

    _line = ImageLabel(self, image_path=r'.\img\line.png', width=500, height=10)
    _line.pack()
  

  def start(self):

    @threaded
    def start_downloading():
      try:
        self.dl_object.start()
      except Exception as e:
        # del DATABASE[-1]
        print(e)
        raise 'Download Faild'

    @threaded
    def show_progress():

      while not self.dl_object: continue

      while not hasattr(self.dl_object, 'get_speed'): continue
      
      self.init_UI()

      while not self.dl_object.isFinished():
        try:
          self.speed.set(self.dl_object.get_speed(human=True))
          self.time.set(self.dl_object.get_eta(human=True).replace(' minute,', 'm').replace(' minutes,', 'm').replace(' seconds', 's'))
          self.size.set(self.dl_object.get_dl_size(human=True))
          # self._progress['value'] = 100 * self.dl_object.get_progress()
          self.progress.set(f'{self.dl_object.get_progress():.0%}')
        except Exception as e:
          print(e)

    
        time.sleep(0.2)
  
        self.update_idletasks()

      if self.dl_object.isFinished():
        self.speed.set('Finished')
        self.time.set(str(self.dl_object.get_dl_time(human=True)).replace(' minute,', 'm').replace(' minutes,', 'm').replace(' seconds', 's'))
        self.size.set(self.dl_object.get_final_filesize(human=True))
        # self._progress['value'] = 100 
        self.progress.set('100%')
  

        self._pause.config(images=[r'.\img\points.tif', r'.\img\pointsHover.tif', r'.\img\pointsPress.tif'])
        self._pause.command = lambda : open_path(self.dl_object.get_dest(), DEST)

        self.update_idletasks()



        # show system notification 
        toaster.show_toast("download completed",
                  f"{self.filename} downloaded",
                  icon_path=APP_ICO,
                  callback_on_click=lambda a=None:open_path(self.dl_object.get_dest(), DEST),
                  duration=10,
                  threaded=True)

    start_downloading()
    show_progress()
  
  def cancel_download(self):
    if self.dl_object:
      self.dl_object.stop()
      # DATABASE.remove(self)
      self.destroy()


  def pause_download(self):
    # print('pause Download..')
    self.dl_object.pause()
    self._pause.config(images=PLAY_IMAGES)
    self._pause.command = self.resume_download


  def resume_download(self):
    # print('resume Download...')
    self.dl_object.resume()
    self._pause.command = self.pause_download
    self._pause.config(images=PAUSE_IMAGES)

  @property
  def status(self):
    if self.dl_object:
      return self.dl_object.get_status()
    return None

  @property
  def extension(self):
    dest = self.dl_object.get_dest()
    return os.path.splitext(dest)[1]

  @property
  def filename(self):
    head, tail = ntpath.split(self.dl_object.get_dest())
    return tail or ntpath.basename(head)


# if __name__ == "__main__":
  # root = tk.Tk()
  # root.config(bg="white")
  # # url = 'http://www.ovh.net/files/100Mio.dat'
  # url = 'https://github.com/iTaybb/pySmartDL/raw/master/test/7za920.zip'


  # dl = SmartDL(url, DEST)
  # item1 = DownloadItem(root, dl_object=dl)
  # # item2 = DownloadItem(root)
  # item1.pack()

  # # item2.pack()
  # root.mainloop()

