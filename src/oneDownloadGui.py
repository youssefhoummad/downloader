import os
from datetime import datetime
import threading
import time
import ntpath

import tkinter as tk
from tkinter import ttk

from .win10toast import ToastNotifier
from .imageLabel import ImageLabel
from .buttons import *
from .constants import *
from .utils import *


# toaster = ToastNotifier()


class OneDownloadGui(tk.Frame):
  # url, dst, filename=None, extension=None, size=None, progress=None, status=None
  def __init__(self, parent, **kwargs):
    tk.Frame.__init__(self, parent)
    self.config(bg=parent['bg'])
    self.parent = parent

    self.url = kwargs.get('url', None)
    self.destination = kwargs.get('destination', None)
    self.extension = kwargs.get('extension', None)
    self.filename = kwargs.get('filename', None)
    self.size = kwargs.get('size', '-- MB')
    self.status = kwargs.get('status', 'finished')

    self.progress = tk.StringVar()
    self.progress.set( kwargs.get('progress', '0%'))

    self.speed = tk.StringVar()
    self.speed.set('-- kB/s')

    self.time = tk.StringVar()
    self.time.set('-m -s')

    self.dl_object = kwargs.get('dl_object', None)

    self.icon = get_icon(self.extension)

    self.init_UI()

    if self.progress.get() == '100%':
      self.replace_pause_by_open_path()


  def init_UI(self):
    _f = tk.Frame(self, bg=self['bg'])
    self._iconLabel = tk.Label(_f, text="", image=self.icon, bg=self['bg'])
    self._nameLabel = tk.Label(_f, text=self.filename, bg=self['bg'], width=26, anchor='nw')
    self._progressLabel = tk.Label(_f, textvariable=self.progress, bg=self['bg'], width=8)
    self._speedLabel = tk.Label(_f, textvariable=self.speed, bg=self['bg'], width=10)
    self._sizeLabel = tk.Label(_f, text=self.size, bg=self['bg'], width=10)
    self._timeLabel = tk.Label(_f, textvariable=self.time, bg=self['bg'], width=12)
    self._pauseBtn = ButtonPause(_f, command=self.pause_download)
    self._cancelBtn = ButtonCancel(_f, command=self.cancel_download)
    _line = ImageLabel(self, image_path=r'.\img\line.png', width=500, height=10)


    self._iconLabel.pack(side='left', padx=(5,0))
    self._nameLabel.pack(side='left', padx=(5, 0))
    self._progressLabel.pack(side='left', padx=(5, 0))
    self._speedLabel.pack(side='left', padx=(5, 0))
    self._sizeLabel.pack(side='left', padx=(5, 0))
    self._timeLabel.pack(side='left', padx=(5, 0))
    self._pauseBtn.pack(side='left', padx=(5, 0))
    self._cancelBtn.pack(side='left', padx=(5, 10))
    _line.pack(side='bottom')
    _f.pack(ipady=3)
  
  
  def cancel_download(self):
    if self.dl_object:
      # stop download
      self.dl_object.stop()
    #   # DATABASE.remove(self)
    # remove this Frame
    self.destroy()


  def pause_download(self):
    if self.dl_object:
      # pause download
      self.dl_object.pause()
      # change icon button to play
      self._pauseBtn.config(images=PLAY_IMAGES)
      # change commad button to resume
      self._pauseBtn.command = self.resume_download


  def resume_download(self):
    self.dl_object.resume()
    # change icon button to pause
    self._pauseBtn.config(images=PAUSE_IMAGES)
    # change command button to pause
    self._pauseBtn.command = self.pause_download


  def replace_pause_by_open_path(self):
    # change icon buton to <...>
    self._pauseBtn.config(images=[r'.\img\points.tif', r'.\img\pointsHover.tif', r'.\img\pointsPress.tif'])
    # change command button to open folder destination
    self._pauseBtn.command = lambda : open_path(dst, DEST)


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

        # saved it in DATABASE
        if not self in DATABASE:
          print('------ add dl_ui to DATABASE ----------')
          print('------ here must be dl_ui >> dl_obj ----------')
          DATABASE.append(self)



        # show system notification 
        toaster.show_toast(
          "download completed",
          f"{self.filename} downloaded",
          icon_path=APP_ICO,
          callback_on_click=lambda a=None:open_path(self.dl_object.get_dest(), DEST),
          duration=10,
          threaded=True
            )

    start_downloading()
    show_progress()
  



if __name__ == "__main__":
  root = tk.Tk()
  root.config(bg="white")
  # url = 'http://www.ovh.net/files/100Mio.dat'
  url = 'https://github.com/iTaybb/pySmartDL/raw/master/test/7za920.zip'


  # dl = SmartDL(url, DEST)
  item1 = OneDownloadGui(root, url=url, extension='.psd', progress='37%', filename="app.exe")
  # item2 = DownloadItem(root)
  item1.pack()

  # # item2.pack()
  root.mainloop()

