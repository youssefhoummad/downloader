from tkinter import Entry, Menu, Frame, Label
import time


try: 
  from .imageLabel import ImageLabel
  from .constants import *
except: 
  from imageLabel import ImageLabel
  from constants import *



class CostumEntry(Entry):
  def __init__(self, *args, **kwargs):
    Entry.__init__(self, *args, **kwargs)
    self.config(highlightthickness=1, relief='flat')
    self.config(highlightbackground="#AAA", highlightcolor="#AAA")

    self.changes = [""]
    self.steps = int()

    self.context_menu = Menu(self, tearoff=0)
    self.context_menu.add_command(label="Cut")
    self.context_menu.add_command(label="Copy")
    self.context_menu.add_command(label="Paste")


    self.bind("<KeyRelease>", self.on_change)

    self.bind("<Control-z>", self.undo)
    self.bind("<Control-Shift-Z>", self.redo)

    self.bind("<Button-3>", self.popup)

    # self.focus_set()

  def flash(self):

    self.config(highlightbackground="red", highlightcolor="red" )
    self.update_idletasks()
    time.sleep(0.06)
    self.config(highlightbackground="white", highlightcolor="white")
    self.update_idletasks()

    time.sleep(0.05)
    self.config(highlightbackground="red", highlightcolor="red")
    self.update_idletasks()
    time.sleep(0.04)
    self.config(highlightbackground="white", highlightcolor="white")
    self.update_idletasks()
    
    time.sleep(0.03)
    self.config(highlightbackground="red", highlightcolor="red")
    self.update_idletasks()
    time.sleep(0.02)
    self.config(highlightbackground="white", highlightcolor="white")
    self.update_idletasks()

    self.config(highlightbackground="#DDD", highlightcolor="#DDD")


  def on_change(self, event=None):
    if self.get() != self.changes[-1]:
      self.changes.append(self.get())
      self.steps += 1


  def popup(self, event):
    self.context_menu.post(event.x_root, event.y_root)
    self.context_menu.entryconfigure("Cut", command=lambda: self.event_generate("<<Cut>>"))
    self.context_menu.entryconfigure("Copy", command=lambda: self.event_generate("<<Copy>>"))
    self.context_menu.entryconfigure("Paste", command=lambda: self.event_generate("<<Paste>>"))


  def undo(self, event=None):
    if self.steps != 0:
      self.steps -= 1
      self.delete(0, 'end')
      self.insert('end', self.changes[self.steps])


  def redo(self, event=None):
    if self.steps < len(self.changes):
      self.delete(0, 'end')
      self.insert('end', self.changes[self.steps])
      self.steps += 1



class SearchEntry(Frame):
  def __init__(self, parent, on_change=None, *args, **kwargs):
    super().__init__(parent, *args, **kwargs)
    self.config(bg='white' )

    self.command = on_change

    icon = ImageLabel(self, image_path=SEARCH_ICO, width=12, height=12)
    icon.config(bg='white')
    icon.pack(side='left', padx=5)

    self.entry = CostumEntry(self)
    self.entry.config(highlightthickness=0, fg='gray')
    self.entry.pack(side='left', pady=2)

    self.entry.bind("<KeyRelease>", self.on_change)
  
  def on_change(self, event=None):
    self.entry.on_change()
    self.command()
  
  def get(self):
    return self.entry.get()



class EntryWidthValidator(Frame):
  def __init__(self, parent, validator=None, *args, **kwargs):
    super().__init__(parent)
    self.config(bg=parent['bg'])
    self.command = validator
    

    self.entry = CostumEntry(self, *args, **kwargs)
    self.entry.config(highlightthickness=1)
    self.entry.pack(pady=2, fill='x', ipady=1)

    self.notifications = Label(self, text='', fg='red')
    self.notifications.config(bg=parent['bg'])
    self.notifications.pack(fill='x')
    
    self.entry.focus_set()

    # self.entry.bind("<Return>", self.validate)
    # self.bind("<Return>", self.validate)
  
  def on_disable(self):
    self.entry.config(state='disable')
  

  def on_unable(self):
    self.entry.config(state='normal')
  
  
  def validate(self, event=None):

    errors = self.command(self.entry.get())

    if not errors:
      self.notifications.config(text='')
      return True
    else:
      self.entry.flash()
      self.notifications.config(text=errors)
      self.after(4000, lambda : self.notifications.config(text=''))
      return False

  
  def get(self):
    return self.entry.get()
    

if  __name__  == '__main__':
  from tkinter import Tk, Button
  root = Tk()

  def validator(value):
    r = value.isdigit()
    if r: return 0
    return '* not a number'

  c = EntryWidthValidator(root, validator=validator)
  c.pack()

  # b = Button(root, text='flash', command=c.flash)
  # b.pack()

  root.mainloop()






