import tkinter as tk, threading, queue, os

from pySmartDL import SmartDL

from gui import GuiApp
from src import *



class ThreadedApp(object):
  """
  Launch the main part of the GUI and the worker thread. periodic_call()
  and end_application() could reside in the GUI part, but putting them
  here means that you have all the thread controls in a single place.
  """
  def __init__(self, master):
    """
    Start the GUI and the asynchronous threads.  We are in the main
    (original) thread of the application, which will later be used by
    the GUI as well.  We spawn a new thread for the worker (I/O).
    """
    self.master = master
    # Create the queue
    self.queue = queue.Queue()



    # self.load_from_db()

    # Set up the GUI part
    self.gui = GuiApp(master, self.queue, self.download)


    # Set up the thread to do asynchronous I/O
    # More threads can also be created and used, if necessary
    self.running = True
    
    # Start the periodic call in the GUI to check the queue
    self.periodic_call()


    self.display_old_downloads()




  def periodic_call(self):
    """ Check every 200 ms if there is something new in the queue. """
    self.master.after(200, self.periodic_call)
    self.gui.processIncoming()
    # if not self.running:
    #   # This is the brutal stop of the system.  You may want to do
    #   # some cleanup before actually shutting it down.
    #   import sys
    #   self.master.destroy()
    #   sys.exit(1)


  def display_old_downloads(self):
    if DATABASE:
      self.gui.remove_no_item_label()

      for dl_object in DATABASE:
        DownloadItem(self.gui.downloadsFrame, 
            dl=None, 
            url = dl_object.url,
            dst= dl_object.dst,
            filename= dl_object.filename, 
            ext = dl_object.extension,
            progress = dl_object.progress,
            size = dl_object.size
            ).grid(row=len(self.gui.downloadsFrame.grid_slaves()), column=0)


  @threaded
  def download(self):
      # self.queue.put(msg) # send msg to GuiApp

      # disable url input
      self.gui.disable_input()

      # check if given url is valid
      is_valid = self.gui.url_input.validate()
      if not is_valid: 
        self.gui.unable_input() # if not valid unable url input
        return
      
      # store url in variable <url>
      url = self.gui.url.get()



      dst, ext, filename= DEST, None, None
      if is_youtube_link(url):
        url, dst, name = youtube_direct_link(url)
        ext = '.mp4'


      # remove <No item Found> from interface
      self.gui.remove_no_item_label()

      options = {'url':url, 'dsrt':dst, "filename":filename, 'extension':ext }

      dl_ui = DownloadItem(self.gui.downloadsFrame, dl=None, url=url, dst=dst, filename=filename, ext=ext)
      dl_ui.grid(row=len(self.gui.downloadsFrame.grid_slaves()), column=0)

      
      print('------ add dl_ui to DATABASE ----------')
      DATABASE.append(dl_ui)

      try:
        # create download object
        dl_ui.dl_object = SmartDL(url, dst, progress_bar=False)
      except Exception as e:
        raise e

      # start download
      dl_ui.start()

      # active url input
      self.gui.unable_input()



if __name__ == '__main__':
  root = tk.Tk()
  root.geometry('800x500')
  root.resizable(False, False)
  root.title('Downloader')
  root.iconbitmap(APP_ICO)
  # root.protocol('WM_DELETE_WINDOW', doSomething) #ovveride x button in titlebar
  App = ThreadedApp(root)
  root.mainloop()
