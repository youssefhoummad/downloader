import tkinter as tk
from tkinter import ttk
import threading
import time

from pySmartDL import SmartDL
import validators


DEST = 'C:\\Users\\youssef\\Downloads\\'


from src.tkscrolledframe import *
from src.cardFrame import * 
from src.buttons import *
from src.sidebarItem import *
from src.downloadItem import *
from src.customEntry import CostumEntry as Entry





class AppGUI(tk.Tk): 
  
  def __init__(self):
    tk.Tk.__init__(self)
    self.geometry('800x400')
    self.title('PyDownloader')
    self.iconbitmap(r'.\img\icon.ico')

    self.url = tk.StringVar()

    # self.collpsed = False

    self.queues = []

    self.downloads = []


    self.sidebar = tk.Frame(self, width=150, height=600)
    self.sidebar.pack(side='left', anchor='nw')

    # main content area
    self.mainarea = tk.Frame(self, bg='white', width=550, height=500)
    self.mainarea.pack(expand=True, fill='both', side='left')


    self.sidebare_init()
    self.mainarea_init()
    self.entry.focus_set()

  
  def sidebare_init(self):
    CardFrame(self.sidebar, 'Downloader', content='mini tool utils for download files...').pack(pady=(0,20), fill='x')

    bs = ButtonSidebarWithChildrens(self.sidebar, text='downloding', icons=[r'img\download.tif'])

    bs.chilrens = [
      ButtonSidebar(bs, text='All', icons=[r'img\all.tif']),
      ButtonSidebar(bs, text='Videos', icons=[r'img\video.tif']),
      ButtonSidebar(bs, text='Images', icons=[r'img\images.tif']),
      ButtonSidebar(bs, text='Music', icons=[r'img\music.tif']),
      ButtonSidebar(bs, text='Archives', icons=[r'img\archive.tif']),
    ]

    bs.pack_childrens()

    bs.pack(fill='x', expand=True)

    ButtonSidebar(self.sidebar, text='Finished', icons=[r'img\ok.tif']).pack(fill='x')
    ButtonSidebar(self.sidebar, text='Unfinished', icons=[r'img\ban.tif']).pack(fill='x')
    ButtonSidebar(self.sidebar, text='Queues', icons=[r'img\queue.tif']).pack(fill='x')

  
  def mainarea_init(self):
    _f = tk.Frame(self.mainarea, bg='white')
    self.entry = Entry(_f, textvariable=self.url)
    self.entry.bind('<Return>',lambda x: self.add_download())
    self.entry.pack(side='left', fill='x', expand=True, ipady=2)

    ButtonPlus(_f,  command=self.add_download).pack(side='left', padx=(15,5))
    _f.pack(fill='x', padx=(20, 10), pady=10)


    sf = ScrolledFrame(self.mainarea, width=600, height=480)
    sf.pack(side="top", expand=1, fill="both")

    sf.bind_arrow_keys(self)
    sf.bind_scroll_wheel(self)

    # Create a frame within the ScrolledFrame
    self.downloadsFrame = sf.display_widget(tk.Frame, bg='white')


  def add_download(self):
    if not validators.url(self.url.get()): 
      self.entry.flash()
      return

    try: self.row += 1
    except: self.row = 0

    d = DownloadItem(self.downloadsFrame, url=self.url.get())
    d.grid(row=self.row, column=0)

    d.start_downloading()
    self.url.set('')
    
    # add download to db
    self.downloads.append(d)

    




if __name__ == "__main__":
  app = AppGUI()
  app.mainloop()