from tkinter import Entry, Menu
import time


class CostumEntry(Entry):
  def __init__(self, *args, **kwargs):
    Entry.__init__(self, *args, **kwargs)
    self.config(highlightthickness=1, relief='flat')

    self.changes = [""]
    self.steps = int()

    self.context_menu = Menu(self, tearoff=0)
    self.context_menu.add_command(label="Cut")
    self.context_menu.add_command(label="Copy")
    self.context_menu.add_command(label="Paste")


    self.bind("<Key>", self.on_change)

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

    self.config(highlightbackground="#CCC", highlightcolor="#CCC")



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



if  __name__  == '__main__':
  from tkinter import Tk, Button
  root = Tk()
  c = CostumEntry(root)
  c.pack()

  b = Button(root, text='flash', command=c.flash)
  b.pack()

  root.mainloop()






