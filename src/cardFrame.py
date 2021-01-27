import tkinter as tk
from .linkLabel import LinkLabel
# from .constant import *

class CardFrame(tk.Frame):
  def __init__(self, parent, title, content, background=None):
    tk.Frame.__init__(self, parent)
    
    self.bg = parent['background']
    self.configure(bg=self.bg)


    tk.Label(self, bg=self.bg, text=title, fg="#00B050", justify='left',  anchor="nw",font=('Calibre',14,"bold")).pack(padx=(20,0),fill="both", pady=(12,0))
    LinkLabel(self, text=content, link="https://github.com/youssefhoummad", bg=self.bg,fg='gray', anchor="nw",justify='left', font=('Calibre',8,"normal")).pack(fill='both', padx=(20,0))

if __name__ == "__main__":
    root = tk.Tk()
    f = CardFrame(root, "PDF tools", "PDF tools is a collections of tools \nthat will works with pdf fils")
    f.pack(fill='both', expand='True')
    root.mainloop()
