import os
import queue
import threading
from abc import ABC, abstractmethod

from src.centered_mbox import askyesno


class Model:
    def __init__(self, parent):
        self.parent = parent  # for tkinter variables if needed



# =========================================================
# الإطار العام (Framework)
# =========================================================

class Controller(ABC):
    
    """كل التحكم في الخيوط والرسائل في مكان واحد."""

    def __init__(self, parent, view_cls, model_cls):
        self.parent = parent
        self.queue = queue.Queue()
        self.running = True

        self.model = model_cls(self.parent)
        self.view = view_cls(self.parent,
                             controller=self,
                             model=self.model,
                             queue=self.queue)
        self.view.setup(self, self.model)

        # ✅ ربط زر إغلاق النافذة (X) بدالة التنظيف
        self.parent.protocol("WM_DELETE_WINDOW", self.on_close)

        self.periodic_call()


    def _active_downloads_count(self):
        """عدد التنزيلات غير المكتملة."""
        count = 0
        for task in list(self.model.tasks.values()):
            try:
                if not task.isFinished():
                    count += 1
            except Exception:
                count += 1   # لا نعرف حالته؟ نعتبره نشطًا (الأأمن)
        return count


    def on_close(self):
        """يُستدعى عند النقر على X — يحذّر إن كان هناك تنزيلات نشطة."""
        active = self._active_downloads_count()

        if active > 0:
            # answer = messagebox.askyesno(
            answer = askyesno(self.parent,
                "تنزيلات نشطة",
                f"يوجد {active} تنزيل قيد التقدم.\n"
                "إغلاق البرنامج سيوقفها.\n\n"
                "هل تريد الإغلاق بالتأكيد؟",
                icon='warning'
            )
            if not answer:
                return   # ← المستخدم تراجع — لا نغلق شيئًا

        # المستخدم أكد (أو لا توجد تنزيلات نشطة) — أغلق كل شيء
        self.running = False

        for task in list(self.model.tasks.values()):
            try:
                task.stop()
            except Exception:
                pass

        self.parent.destroy()
        os._exit(0)

    def periodic_call(self):
        if not self.running:
            return
        self.parent.after(200, self.periodic_call)
        self.process_incoming()

    def process_incoming(self):
        """يعالج رسائل القائمة وينفّذ on_<name> في الخيط الرئيسي."""
        while True:
            try:
                kind, payload = self.queue.get_nowait()
            except queue.Empty:
                break
            handler = getattr(self, f"on_{kind}", None)
            if handler:
                handler(payload)
            else:
                print("رسالة غير معالجة:", kind, payload)

    def thread(self, target, args=(), kwargs=None):
        """تشغيل مهمة في خيط خلفي دون تجميد الواجهة."""
        kwargs = kwargs or {}
        t = threading.Thread(target=target, args=args,
                             kwargs=kwargs, daemon=True)
        t.start()
        return t

    def mainloop(self):
        self.parent.mainloop()

    def end_application(self):
        import sys
        self.running = False
        self.parent.destroy()
        sys.exit(0)


class View(ABC):
    """الأساس: الواجهة فقط — لا منطق ولا خيوط هنا."""

    def __init__(self, parent, controller, model, queue):
        self.parent = parent
        self.controller = controller
        self.model = model
        self.queue = queue

    @abstractmethod
    def setup(self, controller, model):
        """أضف هنا جميع عناصر الواجهة (widgets)."""
        pass

