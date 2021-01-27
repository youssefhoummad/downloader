from tkinter import Label, Frame

from PIL import Image, ImageTk, ImageMath


class ButtonSidebar(Frame):
  def __init__( self, parent, text, command=None,
                icons=[], icons_width=15,
                 **kwargs):
      
    Frame.__init__(self, parent, **kwargs)

    self.icons_width = icons_width
    self.command= command
    self.disabeld = False

 
    # background image
    while len(icons) < 4:
      icons.append(icons[0])
    
    self._ico = self.render_image(icons[0])
    self._icoHover = self.render_image(icons[1])
    self._icoPress = self.render_image(icons[2])
    self._icoDisable = self.render_image(icons[3])

    # text color
    self._fg = '#888'
    self._fgHover = '#66CC8F'
    self._fgPress = 'white'
    self._fgDisable = 'gray'

    self._bg = parent['bg']
    self._bgHover = '#E9F8EF'
    self._bgPress = '#66CC8F'
    self._bgDisable = parent['bg']

    self.mainFrame = Frame(self, bg=self._bg)
    self.mainFrame.pack(fill='x', expand=True)


    self.border = Frame(self.mainFrame, width=5, bg=self._bg)
    self.border.pack(side='left', fill='y')

    self.icon = Label(self.mainFrame, text="", image=self._ico, bg=self._bg)
    self.icon.pack(side='left', pady=5, padx=(20,15))
    
    self.text = Label(self.mainFrame, text=text, bg=self._bg, fg=self._fg, font=('Tahoma',9,'bold'))
    self.text.pack(side='left', pady=5, fill='x')


    self.bind_it(self)
    self.bind_it(self.mainFrame)
    self.bind_it(self.text)
    self.bind_it(self.icon)
 
  
    # self.on_disable()


  def bind_it(self, widget):
    widget.bind("<Enter>", self.on_enter)
    widget.bind("<Leave>", self.on_leave)
    widget.bind("<ButtonPress-1>", self.on_press)
    widget.bind("<ButtonRelease-1>", self.on_release)
    widget.bind("<Double-Button-1>", self.on_doubleClick)
    
  

  def render_image(self, ico):

    ico = Image.open(ico)

    if self.icons_width:
      #  maintain its aspect ratio
      wpercent = (self.icons_width/float(ico.size[0]))

      hsize = int((float(ico.size[1])*float(wpercent)))

      ico = ico.resize((self.icons_width, hsize), Image.ANTIALIAS)
    



    return ImageTk.PhotoImage(ico)


  def on_enter(self, event):
    if not self.disabeld:
      self.mainFrame.config(bg=self._bgHover)
      self.icon.config(image=self._icoHover, bg=self._bgHover)
      self.border.config(bg=self._bgPress)
      self.text.config(bg=self._bgHover, fg=self._fgHover)
    

  def on_leave(self, event):
    if not self.disabeld:
      self.mainFrame.config(bg=self._bg)
      self.icon.config(image=self._ico, bg=self._bg)
      self.border.config(bg=self._bg)
      self.text.config(bg=self._bg, fg=self._fg)


  def on_press(self, event):
    if not self.disabeld:
      self.mainFrame.config(bg=self._bgPress)
      self.icon.config(image=self._icoPress, bg=self._bgPress)
      self.border.config(bg=self._bgPress)
      self.text.config(bg=self._bgPress, fg=self._fgPress)


  def on_release(self, event):
    # if self['state']!="disabled":
    if not self.disabeld:
      self.on_enter(event=None)
      if self.command: self.command()
  
  def on_doubleClick(self, event):
    pass


  def on_disable(self, event=None):
    self.disabeld = True
    self.icon.config(image=self._icoDisable, fg=self._fgDisable)


  def on_unable(self, event=None):
    self.disabeld = False
    self.icon.config(image=self._ico, fg=self._fg)


class ButtonSidebarWithChildrens(ButtonSidebar):
  def __init__(self, parent, text, command=None, icons=[], icons_width=15):

    super().__init__(parent, text, command, icons, icons_width)

    self.childrens = []
    self.collapsed = False

    self.arrow = Label(self.mainFrame, text="▲", bg=self._bg, fg='gray')
    self.arrow.pack(side='right', padx=5)

    super().bind_it(self.arrow)

  
  def add_children(self, child):
    pass

  
  def toggle_arrow(self, event=None):
    self.arrow['text']="▼" if self.arrow['text']=='▲' else "▲"
  
  
  def toggle_collapse(self, event=None):
    if self.collapsed:
      self.pack_childrens()
    else:
      for child in self.childrens:
        child.pack_forget()
    
    self.collapsed = not self.collapsed
    self.toggle_arrow()

    
  def pack_childrens(self):
    for children in self.childrens:
      children.border.pack_forget()
      children.pack(padx=(15, 0), fill='x', expand=True)


  def on_enter(self, event=None):
    super().on_enter(event=None)

    if not self.disabeld:
      self.arrow.config(bg=self._bgHover)


  def on_leave(self, event=None):
    super().on_leave(event=None)

    if not self.disabeld:
      self.arrow.config(bg=self._bg)


  def on_press(self, event=None):
    super().on_press(event=None)

    if not self.disabeld:
      self.arrow.config(bg=self._bgPress)


  def on_release(self, event=None):
    super().on_release(event=None)
    # self.toggle_collapse()

    if not self.disabeld:
      self.arrow.config(bg=self._bgHover)

  
  def on_doubleClick(self, event=None):
    super().on_doubleClick(event=None)

    self.toggle_collapse()



if __name__ == "__main__":
    from tkinter import Tk
    root = Tk()

    b = ButtonSidebarWithChildrens(root, text='downloding', icons=[r'.\img\x.tif'], icons_width=10)
    b.pack(fill='x')

    root.mainloop()