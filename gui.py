
from src.constants import *
from src.utils import *
from src.tkscrolledframe import *
from src.cardFrame import * 
from src.buttons import *
from src.sidebarItem import *
from src.downloadItem import *
from src.customEntry import EntryWidthValidator
from src.customEntry import SearchEntry


class GuiApp(tk.Frame):

  def __init__(self, master, queue, download_command):
    super().__init__(master)
    self.queue = queue
    # Set up the GUI
    # Add more GUI stuff here depending on your specific needs
    self.download_command = download_command
    
    self.url = tk.StringVar()

    self.sidebar = tk.Frame(self, width=200, height=600)
    self.sidebar.pack(side='left', anchor='nw', expand=True, fill='x')

    self.mainarea = tk.Frame(self, bg='white', width=550, height=500)
    self.mainarea.pack(expand=True, fill='both', side='left')

    self.sidebare_init()
    self.mainarea_init()

    self.pack(fill='both', expand=True)

    # self.load_database()


  def processIncoming(self):
    """ Handle all messages currently in the queue, if any. """
    while self.queue.qsize():
      try:
        msg = self.queue.get_nowait()
        # Check contents of message and do whatever is needed. As a
        # simple example, let's print it (in real life, you would
        # suitably update the GUI's display in a richer fashion).
        print(msg)
      except queue.Empty:
        # just on general principles, although we don't expect this
        # branch to be taken in this case, ignore this exception!
        pass
  

  def sidebare_init(self):
    CardFrame(self.sidebar, 'Downloader', content='by @youssefhoummad').pack(fill='x')

    self.searchEntry = SearchEntry(self.sidebar, on_change=self.search)
    self.searchEntry.pack(fill='x', padx=(20,10), pady=20)

    btn_all = ButtonSidebar(self.sidebar, text='All', icons=[r'img\all.tif'], command=lambda :self.filter(None))
    btn_all.pack(fill='x')

    btn_downloading = ButtonSidebar(self.sidebar, text='downloding', icons=[r'img\download.tif', r'img\downloadHover.tif'], command=lambda :self.filter('downloding'))
    btn_downloading.pack(fill='x')

    btn_finished = ButtonSidebarWithChildrens(self.sidebar, text='Finished', icons=[r'img\ok.tif', r'img\okHover.tif'], command=lambda :self.filter('finished'))
    btn_finished.pack(fill='x', expand=True)


    btn_finished.childrens = [
      ButtonSidebar(btn_finished, text='Videos', icons=[r'img\video.tif', r'img\videoHover.tif'], command=lambda :self.filter(VIDEO_EXT)),
      ButtonSidebar(btn_finished, text='Images', icons=[r'img\images.tif', r'img\imagesHover.tif'], command=lambda :self.filter(IMAGES_EXT)),
      ButtonSidebar(btn_finished, text='Musics', icons=[r'img\music.tif', r'img\musicHover.tif'], command=lambda :self.filter(AUDIO_EXT)),
      ButtonSidebar(btn_finished, text='Documents', icons=[r'img\document.tif', r'img\documentHover.tif'], command=lambda :self.filter(DOCS_EXT)),
      ButtonSidebar(btn_finished, text='Archives', icons=[r'img\archive.tif', r'img\archiveHover.tif'], command=lambda :self.filter(ARCHIVE_EXT)),
    ]

    btn_finished.pack_childrens()

    btn_unfinished = ButtonSidebar(self.sidebar, text='Unfinished', icons=[r'img\ban.tif', r'img\banHover.tif'], command=lambda :self.filter('unfinished'))
    btn_unfinished.pack(fill='x')

  
  def mainarea_init(self):
    _f = tk.Frame(self.mainarea, bg='white')

    self.url_input = EntryWidthValidator(_f, validator=validator, textvariable=self.url)
    self.url_input.entry.bind('<Return>',lambda x: self.download_command()) # becouse entry has an other entry insid
    self.url_input.pack(side='left', fill='x', expand=True, ipady=2)

    self.downloadButton = ButtonPlus(_f,  command=self.download_command)
    self.downloadButton.pack(side='top', padx=(15,5))
    _f.pack(fill='x', padx=(20, 10), pady=10)


    sf = ScrolledFrame(self.mainarea, width=600, height=480)
    sf.pack(side="top", expand=1, fill="both")

    sf.bind_arrow_keys(self)
    sf.bind_scroll_wheel(self)

    # Create a frame within the ScrolledFrame
    self.downloadsFrame = sf.display_widget(tk.Frame, fit_width=True, bg='white')

    self.display_no_item_label()


  def disable_input(self):
    self.downloadButton.on_disable()
    self.url_input.on_disable()


  def unable_input(self):
    self.url.set('')
    self.downloadButton.on_unable()
    self.url_input.on_unable()


  def clear_downloads(self):
    self.remove_no_item_label()
    # clean frame for downloads
    for widget in self.downloadsFrame.grid_slaves():
      widget.grid_forget()

  
  def display_no_item_label(self):
    if len(self.downloadsFrame.grid_slaves()):
      return
    self.no_item_label =tk.Label(self.downloadsFrame, text='No item', bg='white', font=('Calibre',16, 'normal'), fg='gray')
    self.no_item_label.pack(fill='both', expand=True, ipady=160)


  def remove_no_item_label(self):
    try: self.no_item_label.pack_forget()
    except: pass


  def search(self):
    query = self.searchEntry.get()

    if not query: 
      filterd = DATABASE
    else:
      filterd = list(filter(lambda item: query in str(item.filename), DATABASE))

    self.clear_downloads()

    if not filterd:
      self.display_no_item_label()
      return

    for i, item in enumerate(filterd):
      try: item.grid(row=i, column=0)
      except: pass


  def filter(self, by=None):
    if by == None:
      filterd = DATABASE

    elif by == 'downloading':
      filterd = list(filter(lambda item: item.status=='downloading', DATABASE))

    elif by == 'finished':
      filterd = list(filter(lambda item: item.status=='finished', DATABASE))

    elif by == 'unfinished':
      filterd = list(filter(lambda item: item.status!='finished', DATABASE))

    else:
      filterd = list(filter(lambda item: (item.extension in by) and (item.status=='finished'), DATABASE))

    self.clear_downloads()

    if not filterd:
      self.display_no_item_label()
      return
    
    for i, item in enumerate(filterd):
      item.grid(row=i, column=0)
      # print(item.filename)
  


