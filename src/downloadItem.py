import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk

from pySmartDL import SmartDL

try:
  from .imageLabel import ImageLabel
  from .buttons import *
except:
  from imageLabel import ImageLabel
  from buttons import *


PAUSE_IMAGES = [r'.\img\pause.emf', r'.\img\pauseHover.emf',r'.\img\pausePress.emf']
PLAY_IMAGES = [r'.\img\play.tif', r'.\img\playHover.tif',r'.\img\playPress.tif']

DEST = 'C:\\Users\\youssef\\Downloads\\'


class DownloadItem(tk.Frame):
  def __init__(self, parent, url, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.config(bg=parent['bg'])

    self.url = url
    self.dl_object = None

    self.speed = tk.StringVar()
    self.speed.set('-- kB/s')
    self.size = tk.StringVar()
    self.size.set('-- MB')
    self.time = tk.StringVar()
    self.time.set('-m -s')

    # self.start_downloading()


  def render_icon_file(self):
    file_types = {
                  '.zip':r'.\img\zip.png', 

                  '.7z':r'.\img\archive.png', 
                  '.rar':r'.\img\archive.png', 
                  '.sfx':r'.\img\archive.png', 

                  '.pdf':r'.\img\pdf.png', 

                  '.jpg':r'.\img\image.png', 
                  '.jpeg':r'.\img\image.png', 
                  '.png':r'.\img\image.png', 

                  '.mp4':r'.\img\video.png', 
                  '.mkv':r'.\img\video.png', 

                  '.mp3':r'.\img\audio.png', 
                }
    return file_types.get(self.file_type, r'.\img\file.png')
    

  def init_UI(self):
    _f = tk.Frame(self, bg=self['bg'])
    _f.pack(ipady=3)

    self._icon = ImageLabel(_f, image_path=self.render_icon_file(), width=24, height=24)
    self._name = None
    self._progress = ttk.Progressbar(_f, length=100)
    self._speed = tk.Label(_f, textvariable=self.speed, bg=self['bg'], width=8)
    self._size = tk.Label(_f, textvariable=self.size, bg=self['bg'], width=8)
    self._time = tk.Label(_f, textvariable=self.time, bg=self['bg'], width=8)
    self._pause = ButtonPause(_f, command=self.pause_download)
    self._cancel = ButtonCancel(_f, command=self.cancel_download)


    self._icon.pack(side='left', padx=(10,0))
    self._progress.pack(side='left', padx=(10, 0))
    self._speed.pack(side='left', padx=(50, 0))
    self._size.pack(side='left', padx=(50, 0))
    self._time.pack(side='left', padx=(50, 0))
    self._pause.pack(side='left', padx=(50, 0))
    self._cancel.pack(side='left', padx=(5, 10))
  

    _line = ImageLabel(self, image_path=r'.\img\line.png', width=500, height=10)
    _line.pack()
  

  def start_downloading(self):


    def start(sem):
      with sem:
        self.dl_object = SmartDL(self.url, DEST, progress_bar=False)
        self.dl_object.start()
    

    def show_progress(sem):

      with sem:

        while not self.dl_object: continue
        
        self.init_UI()

        while not self.dl_object.isFinished():
          if self.dl_object.get_status()=='downloading':
            self.speed.set(self.dl_object.get_speed(human=True))
            self.time.set(self.dl_object.get_eta(human=True).replace(' minute,', 'm').replace(' minutes,', 'm').replace(' seconds', 's'))
          # try:
          self.size.set(self.dl_object.get_dl_size(human=True))
          self._progress['value'] = 100 * self.dl_object.get_progress()
      
          time.sleep(0.2)
    
          self.update_idletasks()

        if self.dl_object.isFinished():
          self.speed.set('Finished')
          self.time.set(self.dl_object.get_dl_time(human=True))
          self.size.set(self.dl_object.get_final_filesize(human=True))
          self._progress['value'] = 100 
    

          self._pause.config(images=[r'.\img\points.tif', r'.\img\pointsHover.tif', r'.\img\pointsPress.tif'])
          self._pause.command = self.open_path

          self.update_idletasks()

    sem = threading.Semaphore(2)

    threading.Thread(target=start, args=(sem,)).start()
    threading.Thread(target=show_progress, args=(sem,)).start()
  

  def open_path(self):
    head, tail = os.path.split(self.url)
    subprocess.Popen(r'explorer /select,"{}"'.format(DEST+tail))

  
  def cancel_download(self):
    if self.dl_object:
      self.dl_object.stop()
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
    return 'faild'

  @property
  def file_type(self):
    dest = self.dl_object.get_dest()
    return os.path.splitext(dest)[1]

if __name__ == "__main__":
    root = tk.Tk()
    root.config(bg="white")
    # url = 'http://www.ovh.net/files/100Mio.dat'
    url = 'https://github.com/iTaybb/pySmartDL/raw/master/test/7za920.zip'
    item1 = DownloadItem(root, url=url)
    # item2 = DownloadItem(root)
    item1.pack()

    # item2.pack()
    root.mainloop()

  


