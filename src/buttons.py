import tkinter as tk


from PIL import Image, ImageTk

class ButtonImage(tk.Label):
  def __init__(self, parent, text, images=[], command=None, icon_w=15, **kwargs):
    tk.Label.__init__(self, parent, text=text, **kwargs)
    self.config(compound="center", cursor='hand2', bd=0, bg=parent['bg'],font=('Calibri',12,"bold"))

    self.command= command
    self.disabeld = False
    self.icon_w = icon_w
    
    self.render_images(images)

    self._color = 'black'
    self._colorHover = 'black'
    self._colorPress = 'black'
    self._colorDisable = 'gray'


    self.bind("<Enter>", self.on_enter)
    self.bind("<Leave>", self.on_leave)
    self.bind("<ButtonPress-1>", self.on_press)
    self.bind("<ButtonRelease-1>", self.on_release)

    # self.on_disable()
  
  
  def render_images(self, images):
    while len(images) < 4:
      images.append(images[0])
    
    self._img = self.path_to_image(images[0])
    self._imgHover = self.path_to_image(images[1])
    self._imgPress = self.path_to_image(images[2])
    self._imgDisable = self.path_to_image(images[3])

    self.config(image=self._img)
  

  def path_to_image(self, img):

    img = Image.open(img)

    if self.icon_w:
      #  maintain its aspect ratio
      wpercent = (self.icon_w/float(img.size[0]))

      hsize = int((float(img.size[1])*float(wpercent)))

      img = img.resize((self.icon_w, hsize), Image.ANTIALIAS)

    return ImageTk.PhotoImage(img)


  def on_enter(self, event):
    if not self.disabeld:
      self.config(image=self._imgHover, fg=self._colorHover)
    

  def on_leave(self, event):
    if not self.disabeld:
      self.config(image=self._img, fg=self._color)


  def on_press(self, event):
    if not self.disabeld:
      self.config(image=self._imgPress, fg=self._colorPress)


  def on_release(self, event):
    # if self['state']!="disabled":
    if not self.disabeld:
      self.on_enter(event=None)
      if self.command: self.command()


  def config(self, **kwargs):
    if 'images' in kwargs:
      self.render_images(kwargs['images'])
      kwargs.pop('images')

    if 'command' in kwargs:
      self.command = kwargs['command']
      kwargs.pop('command')

    super().config(**kwargs)


  def on_disable(self, event=None):
    self.disabeld = True
    self.config(image=self._imgDisable, fg=self._colorDisable)


  def on_unable(self, event=None):
    self.disabeld = False
    self.config(image=self._img, fg=self._color)


class ButtonPause(ButtonImage):
  def __init__(self, parent, command, *args, **kwargs):
    ButtonImage.__init__(self, parent, text='', 
                    images=[r'.\img\pause.emf',r'.\img\pauseHover.emf',r'.\img\pausePress.emf'],
                    command=command, *args, **kwargs
                    )
    

class ButtonPlay(ButtonImage):
  def __init__(self, parent, command, *args, **kwargs):
    ButtonImage.__init__(self, parent, text='', 
                    images=[r'.\img\play.emf', r'.\img\playHover.emf',r'.\img\playPress.emf'],
                    command=command, *args, **kwargs
                    )
    

class ButtonCancel(ButtonImage):
  def __init__(self, parent, command, *args, **kwargs):
    ButtonImage.__init__(self, parent, text='', 
                    images=[r'.\img\exit.emf', r'.\img\exitHover.emf', r'.\img\exitPress.emf'],
                    command=command, *args, **kwargs
                    )

class ButtonPlus(ButtonImage):
  def __init__(self, parent, command, *args, **kwargs):
    super().__init__(parent, text='', 
                    images=[r'.\img\plus.tif', r'.\img\plusHover.tif', r'.\img\plusPress.tif', r'.\img\plusDisable.tif'],
                    command=command, icon_w=26, *args, **kwargs
                    )


class ButtonPath(ButtonImage):
  def __init__(self, parent, command, *args, **kwargs):
    ButtonImage.__init__(self, parent, text='', 
                    images=[r'.\img\points.tif', r'.\img\pointsHover.tif', r'.\img\pointsPress.tif'],
                    command=command, *args, **kwargs
                    )
    



if __name__ == "__main__":
    root  = tk.Tk()

    ButtonCancel(root , command=None).pack()

    root.mainloop()




