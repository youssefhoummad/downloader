from tkinter import Label

from webbrowser import open_new_tab



class LinkLabel(Label):
  def __init__(self, parent, text, link='', **kw):
    super().__init__(parent, **kw)
    
    self.config(cursor='hand2',anchor='nw', justify='left', text=text, bg=parent['bg'])
    self.bind("<Button-1>", lambda e: open_new_tab(link))
