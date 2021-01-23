import tkinter as tk

from PIL import Image, ImageTk


class ImageLabel(tk.Label):
  def __init__(self, parent, image_path, width=None, height=None, **kwargs):
    tk.Label.__init__(self, parent, **kwargs)
    self.config(bg = parent['bg'])
    
    self._img = Image.open(image_path)
    if width or height:
      self._img.thumbnail((width , height), Image.ANTIALIAS)
    self._img = ImageTk.PhotoImage(self._img)
    self.config(image=self._img)

  
if __name__ == "__main__":
  root = tk.Tk()
  iL = ImageLabel(root, image_path=r'.\img\file.png')
  iL.pack()
  root.mainloop()
