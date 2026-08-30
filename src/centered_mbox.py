"""
centered_mbox - مثل tkinter.messagebox تمامًا، لكن يظهر في منتصف النافذة الأم (Windows)
الاستخدام:
    import centered_mbox as mbox
    mbox.showinfo(parent, "Title", "Message")
"""
import ctypes
import ctypes.wintypes
import threading
from tkinter import messagebox as _tkmbox

user32 = ctypes.windll.user32

SWP_NOSIZE   = 0x0001
SWP_NOZORDER = 0x0004


def _center_when_shown(parent, title):
    """يبحث عن نافذة الرسالة في thread منفصل ويوسّطها على الأب."""
    def poll():
        while True:
            hwnd = user32.FindWindowW(None, title)
            if hwnd:
                px = parent.winfo_rootx() + parent.winfo_width() // 2
                py = parent.winfo_rooty() + parent.winfo_height() // 2

                rect = ctypes.wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                w = rect.right - rect.left
                h = rect.bottom - rect.top

                user32.SetWindowPos(hwnd, 0, px - w // 2, py - h // 2,
                                    0, 0, SWP_NOSIZE | SWP_NOZORDER)
                break

    threading.Thread(target=poll, daemon=True).start()


# =========================================================
#  الوظائف — بنفس أسماء tkinter.messagebox تمامًا
# =========================================================

def showinfo(parent, title, message, **options):
    _center_when_shown(parent, title)
    return _tkmbox.showinfo(title, message, parent=parent, **options)

def showwarning(parent, title, message, **options):
    _center_when_shown(parent, title)
    return _tkmbox.showwarning(title, message, parent=parent, **options)

def showerror(parent, title, message, **options):
    _center_when_shown(parent, title)
    return _tkmbox.showerror(title, message, parent=parent, **options)

def askquestion(parent, title, message, **options):
    _center_when_shown(parent, title)
    return _tkmbox.askquestion(title, message, parent=parent, **options)

def askokcancel(parent, title, message, **options):
    _center_when_shown(parent, title)
    return _tkmbox.askokcancel(title, message, parent=parent, **options)

def askyesno(parent, title, message, **options):
    _center_when_shown(parent, title)
    return _tkmbox.askyesno(title, message, parent=parent, **options)

def askyesnocancel(parent, title, message, **options):
    _center_when_shown(parent, title)
    return _tkmbox.askyesnocancel(title, message, parent=parent, **options)

def askretrycancel(parent, title, message, **options):
    _center_when_shown(parent, title)
    return _tkmbox.askretrycancel(title, message, parent=parent, **options)
