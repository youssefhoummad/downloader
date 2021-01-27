import tkinter as tk

try: 
  from .customEntry import CostumEntry
  from .imageLabel import ImageLabel
  from .constants import *
except: 
  from customEntry import CostumEntry
  from imageLabel import ImageLabel
  from constants import *


class SearchEntry(tk.Frame):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.config(bg='white' )

    icon = ImageLabel(self, image_path=SEARCH_ICO, width=12, height=12)
    icon.pack(side='left', padx=5)

    self.entry = CostumEntry(self)
    self.entry.config(highlightthickness=0, fg='gray')
    self.entry.pack(side='left', pady=2)




if __name__ == '__main__':
  root = tk.Tk()

  s = SearchEntry(root)
  s.pack()

  root.mainloop()



