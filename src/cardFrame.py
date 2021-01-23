import tkinter as tk
# from .constant import *

class CardFrame(tk.Frame):
  def __init__(self, parent, title, content, background=None):
    tk.Frame.__init__(self, parent)
    
    self.bg = parent['background']
    self.configure(bg=self.bg)


    tk.Label(self, bg=self.bg, text=title, fg="#00B050", justify='left',  anchor="nw",font=('Tahoma',14,"bold")).pack(padx=(12,0),fill="both", pady=(12,0))
    tk.Label(self, bg=self.bg, text=content,  fg='gray', anchor="nw",justify='left', font=('Tahoma',8,"normal")).pack(fill='both', padx=(12,0))


if __name__ == "__main__":
    root = tk.Tk()
    f = CardFrame(root, "PDF tools", "PDF tools is a collections of tools \nthat will works with pdf fils")
    f.pack(fill='both', expand='True')
    root.mainloop()
