# -*- coding: utf-8 -*-
"""
Downloader App — Tkinter MVC width safe threading

   - Model      : البيانات + المهام + قائمة التنزيلات + الحفظ/الاستعادة
   - View       : الواجهة فقط (ويدجت + تحديثها)
   - Controller : المنطق والخيوط ومعالجات الرسائل on_<name>

 القاعدة الذهبية:
   خيوط العمل لا تلمس الويدجت أبدًا — ترسل فقط رسائل ("name", payload)
   إلى self.queue، وتُعالَج في الخيط الرئيسي كل 200ms.

   1) قائمة التنزيلات في Model — الواجهة تعرض فقط.
   2) تغيير القسم يفلتر القائمة عبر Model.items_for_category().
   3) القائمة تُحفظ في JSON وتُستعاد عند الإقلاع التالي.
"""

import os
import json
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from pathlib import Path

import time
import traceback

from pysmartdl2 import SmartDL
from pysmartdl2 import utils
import validators

import src.centered_mbox as messagebox
from src.mvc import Controller, View
from src.tkscrolledframe import ScrolledFrame
from src.utils import get_icon

# =========================================================
# الثوابت
# =========================================================
FONT_ICON = ('Segoe Fluent Icons', 12, '')
ACCENT_COLOR = '#00796B'
ACCENT_BG = '#B2DFDB'
BACKGROUND = '#F1F3F9'
BACKGROUND_2 = '#F8F9FC'

IMAGES_EXT = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.tiff', '.psd', '.raw', '.bmp', '.heif', '.indd', '.svg', '.ai', '.eps']
VIDEO_EXT = ['.webm', '.mkv', '.flv', '.ogg', '.avi', '.mov', '.ts', '.wmv', '.mp4', '.3gp']
ARCHIVE_EXT = ['.zip', '.rar', '.7z']
DOCS_EXT = ['.doc', '.docx', '.pdf', '.ppt', '.pptx', '.odt', '.ods', '.txt', '.html', '.htm', '.xls', '.xlsx']
AUDIO_EXT = ['.flac', '.alac', '.mp3', '.aac', '.m4a', '.wav', '.wma']

DEST_DIR = os.path.expanduser(r'~\Downloads')

TEST_LINKS = [
    'https://downloads.hindawi.org/books/49686353.pdf',
    'https://github.com/youssefhoummad/pdf-tools/releases/download/v4.0.21/pdftools-portable.zip',
    'https://downloads.hindawi.org/books/97913150.pdf',
    'https://github.com/youssefhoummad/pdf-tools/releases/download/v4.0.21/pdftools-setup.exe',
]

# =========================================================
# MODEL — البيانات فقط (بدون ويدجت، بدون شبكة في الخيط الرئيسي!)
# =========================================================

class Model:
    """مصدر واحد للحقيقة: المهام الحية + بيانات كل عنصر + التخزين."""

    SAVE_FILE = Path.home() / '.downloader' / 'downloads.json'

    # امتدادات كل قسم (للفلترة)
    CATEGORY_EXTS = {
        'videos':    VIDEO_EXT,
        'images':    IMAGES_EXT,
        'musics':    AUDIO_EXT,
        'documents': DOCS_EXT,
        'archives':  ARCHIVE_EXT,
    }

    def __init__(self, root):
        self.root = root
        self.tasks = {}              # task_id -> SmartDL (مهام حية فقط)
        self.next_id = 0
        self.cancel_requested = set()

        self.items = {}              # task_id -> dict (بيانات كل تنزيل)
        self.category = 'all'        # الفلتر الحالي

        self.load()                  # استعادة الجلسة السابقة

    # ---------- المعرفات والمهام ----------
    def reserve_id(self):
        """احجز معرفًا فقط — بدون أي اتصال شبكة (فوري)."""
        task_id = self.next_id
        self.next_id += 1
        return task_id

    def register_task(self, task_id, task):
        """يُستدعى من الخيط الخلفي بعد إنشاء SmartDL."""
        self.tasks[task_id] = task

    def get_task(self, task_id):
        return self.tasks.get(task_id)

    # ---------- بيانات عناصر القائمة ----------
    def add_item(self, task_id, url):
        """عنصر جديد — الاسم المبدئي من الرابط (يُصحَّح لاحقًا من الترويسات)."""
        self.items[task_id] = {
            'task_id': task_id,
            'url': url,
            'filename': Path(url).name or 'download',
            'status': 'downloading',     # downloading | done | failed | stopped
            'pct': 0.0,
            'size': '--',
            'added_at': time.time(),
        }
        self.save()

    def update_item(self, task_id, **fields):
        item = self.items.get(task_id)
        if item is not None:
            item.update(fields)

    def pop_item(self, task_id):
        removed = self.items.pop(task_id, None)
        if removed is not None:
            self.tasks.pop(task_id, None)
            self.save()
        return removed

    # ---------- الفلترة حسب القسم ----------
    def items_for_category(self, category):
        items = list(self.items.values())

        if category == 'finished':
            items = [i for i in items if i['status'] == 'done']
        elif category == 'unfinished':
            items = [i for i in items if i['status'] != 'done']
        else:
            exts = self.CATEGORY_EXTS.get(category)
            if exts:     # videos / images / musics / documents / archives
                items = [i for i in items
                         if Path(i['filename']).suffix.lower() in exts]
            # 'all' (وأي قسم غير معروف) → كل العناصر

        return sorted(items, key=lambda i: i['task_id'])

    # ---------- الحفظ والاستعادة (JSON) ----------
    def save(self):
        """يُستدعى عند تغيّر الحالة + دوريًا أثناء التنزيل (مُقيَّد بالوقت)."""
        try:
            self.SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = sorted(self.items.values(), key=lambda i: i['task_id'])
            self.SAVE_FILE.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding='utf-8')
        except Exception as e:
            print('⚠ save failed:', e)

    def load(self):
        if not self.SAVE_FILE.exists():
            return
        try:
            data = json.loads(self.SAVE_FILE.read_text(encoding='utf-8'))
            for d in data:
                task_id = int(d['task_id'])
                # مهمة كانت شغّالة عند إغلاق التطبيق → أصبحت متوقفة
                if d.get('status') == 'downloading':
                    d['status'] = 'stopped'
                self.items[task_id] = d
                self.next_id = max(self.next_id, task_id + 1)
        except Exception as e:
            print('⚠ load failed:', e)


# =========================================================
# عناصر واجهة مساعدة
# =========================================================

class Progressbar(tk.Frame):
    def __init__(self, master, height=None, *args, **kwargs):
        super().__init__(master)

        self.progress_bar = ttk.Progressbar(self, **kwargs)
        self.progress_bar.place(relx=0, rely=0.5, anchor='w', relwidth=1)

        if height:
            self.config(height=height)
            self.pack_propagate(False)

    def __setitem__(self, key, new_value):
        self.progress_bar[key] = new_value

    def __getitem__(self, key):
        return self.progress_bar[key]


class ButtonSidebar(tk.Frame):
    """زر جانبي مخصص مع مؤشر وحالة نشطة."""
    instances = set()

    def __init__(self, root, icon, text, command=None, active=False, **kwargs):
        super().__init__(root, pady=6, **kwargs)
        self.root = root
        self.command = command if command else print
        self.active = False

        self.indicator = tk.Frame(self, width=4, height=18)
        self.indicator.pack(side='left')

        self.icon = tk.Label(self, text=icon, font=FONT_ICON, fg=ACCENT_COLOR)
        self.icon.pack(side='left', padx=8)

        self.text = tk.Label(self, text=text)
        self.text.pack(side='left')

        for widget in (self, self.indicator, self.icon, self.text):
            widget.bind("<ButtonPress-1>", self.on_press)
            widget.bind("<ButtonRelease-1>", self.on_release)
            widget.bind("<Enter>", self.on_hover)
            widget.bind("<Leave>", self.on_leave)

        self.set_inactive()
        if active:
            self.active = True
            self.set_active()

        ButtonSidebar.instances.add(self)

    def set_active(self):
        self.config(bg=ACCENT_BG)
        self.indicator.config(bg=ACCENT_COLOR)
        self.icon.config(fg=ACCENT_COLOR, bg=ACCENT_BG)
        self.text.config(fg=ACCENT_COLOR, bg=ACCENT_BG)

    def set_inactive(self):
        bg = self.root['bg']
        self.config(bg=bg)
        self.indicator.config(bg=bg)
        self.icon.config(fg=ACCENT_COLOR, bg=bg)
        self.text.config(fg='black', bg=bg)

    def on_hover(self, event=None):
        if not self.active:
            self.text.config(fg=ACCENT_COLOR)

    def on_leave(self, event=None):
        if self.active:
            self.set_active()
        else:
            self.set_inactive()

    def on_press(self, event=None):
        if not self.active:
            self.text.config(fg='gray')
            self.icon.config(fg='gray')
            self.indicator.config(bg='gray')

    def on_release(self, event=None):
        for btn in ButtonSidebar.instances:
            if btn is not self:
                btn.active = False
                btn.set_inactive()
        self.active = True
        self.set_active()
        self.command()


class FrameItemDownload(tk.Frame):
    """عنصر عرض مهمة تنزيل واحدة — عرض فقط، يقرأ من بيانات الموديل."""

    STATUS_TEXT = {
        'downloading': '⏳ جاري التنزيل',
        'done':        '✓ اكتمل',
        'failed':      '✗ فشل التنزيل',
        'stopped':     '⏸ متوقف',
    }

    def __init__(self, root, controller, task_id, filename, **kwargs):
        super().__init__(root, pady=6, **kwargs)
        self.controller = controller
        self.task_id = task_id
        self.filename = Path(filename).name

        # متغيرات العرض
        self.progress_var = tk.StringVar(value='0%')
        self.speed_var = tk.StringVar(value='0 B/s')
        self.size_var = tk.StringVar(value='--')
        self.time_var = tk.StringVar(value='--')
        self.status_var = tk.StringVar(value=self.STATUS_TEXT['downloading'])

        icon = get_icon(Path(filename).suffix)
        self.icon = tk.Label(self, image=icon, font=FONT_ICON)
        self.icon.image = icon

        self.name = tk.Label(self, text=self.filename, width=26, anchor='w')
        self.progress = tk.Label(self, textvariable=self.progress_var, width=8)
        self.speed = tk.Label(self, textvariable=self.speed_var, width=12)
        self.size = tk.Label(self, textvariable=self.size_var, width=10)
        self.time = tk.Label(self, textvariable=self.time_var, width=12)

        self.cancel_btn = tk.Button(self, text='\uf78a', fg='red',
                                    command=self._on_cancel)

        self.progress_bar = Progressbar(self, maximum=100, length=100,
                                        mode='determinate', height=2)

        self.grid_columnconfigure(1, weight=1)
        self.icon.grid(row=0, column=0, padx=(5, 0))
        self.name.grid(row=0, column=1, sticky='w', padx=(5, 0))
        self.progress.grid(row=0, column=2, padx=(5, 0))
        self.speed.grid(row=0, column=3, padx=(5, 0))
        self.size.grid(row=0, column=4, padx=(5, 0))
        self.time.grid(row=0, column=5, padx=(5, 0))
        self.cancel_btn.grid(row=0, column=7, padx=(5, 10))
        self.progress_bar.grid(row=1, column=0, columnspan=8,
                               sticky='ew', padx=24, pady=(12, 0))

    def _on_cancel(self):
        self.controller.cancel_download(self.task_id)

    # ----- تحديث العرض — يُستدعى فقط من معالجات الـ Controller -----

    def update_progress(self, pct, speed_str, size_str=None, eta_str=None):
        self.progress_var.set(f"{int(pct * 100)}%")
        self.progress_bar['value'] = pct * 100
        self.speed_var.set(speed_str)
        if size_str and size_str != '--':
            self.size_var.set(size_str)
        if eta_str and eta_str != '--':
            self.time_var.set(eta_str)

    def set_filename(self, filename):
        """تصحيح الاسم بعد معرفته من SmartDL (Content-Disposition)."""
        self.filename = Path(filename).name
        self.name.config(text=self.filename)

    def apply_state(self, d):
        """بناء العرض من بيانات الموديل (بعد الإقلاع أو إعادة الفلترة)."""
        status = d.get('status', 'downloading')
        pct = 1.0 if status == 'done' else float(d.get('pct') or 0.0)

        self.progress_var.set(f"{int(pct * 100)}%")
        self.progress_bar['value'] = pct * 100

        size = d.get('size', '--')
        if size and size != '--':
            self.size_var.set(size)
        if status == 'done':
            self.speed_var.set('--')

        self.status_var.set(self.STATUS_TEXT.get(status, status))
        if status in ('failed', 'stopped'):
            self.name.config(fg='gray')


# =========================================================
# VIEW — ويدجت فقط + عرض بيانات الموديل
# =========================================================

class DownloaderView(View):

    def setup(self, controller, model):
        self.controller = controller
        self.model = model
        self.url = tk.StringVar()
        self.item_widgets = {}       # task_id -> FrameItemDownload (عرض فقط)

        # الأقسام الرئيسية
        self.sidebar = tk.Frame(self.parent, width=200, bg=BACKGROUND)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        tk.Frame(self.parent, width=1, bg='#E9EAED').pack(side='left', fill='y')

        self.mainarea = tk.Frame(self.parent, bg=BACKGROUND_2)
        self.mainarea.pack(side='left', fill='both', expand=True)

        self.sidebar_setup()
        self.downloading_setup()

        # عرض العناصر المستعادة من الجلسة السابقة وفق الفلتر الافتراضي
        self.refresh_items()

    def sidebar_setup(self):
        title_frame = tk.Frame(self.sidebar, bg=BACKGROUND)
        title_frame.pack(fill='x', pady=(12, 0))
        tk.Label(title_frame, text='Downloader', fg=ACCENT_COLOR,
                 font=('Segoe UI', 14, 'bold'), bg=BACKGROUND).pack()
        tk.Label(title_frame, text='by @youssefhoummad', fg='gray',
                 font=('Segoe UI', 8), bg=BACKGROUND).pack(pady=(0, 24))

        self.buttons = {}
        categories = [
            ('all', '\ue895', 'All', True),
            ('finished', '\ue73e', 'Finished', False),
            ('videos', '\ue714', 'Videos', False),
            ('images', '\ue91b', 'Images', False),
            ('musics', '\uec4f', 'Musics', False),
            ('documents', '\ue8a5', 'Documents', False),
            ('archives', '\uf012', 'Archives', False),
            ('unfinished', '\ue733', 'UnFinished', False),
            ('settings', '\ue713', 'Settings', False),
        ]
        for key, icon, text, active in categories:
            btn = ButtonSidebar(
                self.sidebar, icon=icon, text=text, active=active,
                command=lambda k=key: self.controller.change_category(k))
            if key in ('videos', 'images', 'musics', 'documents', 'archives'):
                btn.pack(fill='x', padx=(24, 0))
            elif key == 'settings':
                btn.pack(fill='x', side='bottom')
            else:
                btn.pack(fill='x')
            self.buttons[key] = btn

    def downloading_setup(self):
        top_frame = tk.Frame(self.mainarea, bg=BACKGROUND_2)
        top_frame.pack(fill='x', padx=6, pady=(6, 0))

        self.entry_url = ttk.Entry(top_frame, textvariable=self.url)
        self.entry_url.pack(side='left', fill='x', expand=True,
                            padx=(0, 6), ipady=3)
        self.entry_url.bind('<Return>', self.controller.start_download)

        self.btn_download = tk.Button(
            top_frame, text='\uf8aa', fg=ACCENT_COLOR,
            command=self.controller.start_download)
        self.btn_download.pack(side='right')

        sf = ScrolledFrame(self.mainarea)
        sf.pack(fill="both", expand=True, padx=6, pady=6)

        self.frame_downloads = sf.interior(fit_width=True, fit_height=True)

        # تُعرض/تُخفى داخل refresh_items() حسب حالة القائمة
        self.empty_label = tk.Label(self.frame_downloads,
                                    text="No downloads yet", fg='gray')
        self.btn_test = ttk.Button(self.frame_downloads, text='Test',
                                   command=self.controller.test_downloads)

    # ---------- إدارة العرض (ويدجت فقط — البيانات من الموديل) ----------

    def refresh_items(self):
        """إعادة بناء القائمة المعروضة من الموديل وفق الفلتر الحالي."""
        for w in self.item_widgets.values():
            w.destroy()
        self.item_widgets.clear()

        items = self.model.items_for_category(self.model.category)
        for data in items:
            item = FrameItemDownload(self.frame_downloads, self.controller,
                                     data['task_id'], data['filename'])
            item.apply_state(data)
            item.pack(fill='x', pady=2)
            self.item_widgets[data['task_id']] = item

        if items:
            self.empty_label.pack_forget()
            self.btn_test.pack_forget()
        else:
            self.empty_label.pack(expand=True, fill='both')
            self.btn_test.pack()

    def clear_url(self):
        self.url.set('')

    def get_url(self):
        return self.url.get().strip()


# =========================================================
# CONTROLLER — المنطق والخيوط ومعالجات الرسائل
# =========================================================
class DownloadController(Controller):

    # ---------- بدء التنزيل ----------

    def _start(self, url):
        """مسار موحد لبدء مهمة: موديل ← عرض ← خيط خلفي."""
        task_id = self.model.reserve_id()
        self.model.add_item(task_id, url)
        self.view.refresh_items()
        self.thread(self._download_worker, args=(task_id, url))

    def start_download(self, event=None):
        url = self.view.get_url()
        if not validators.url(url):
            messagebox.showwarning(self.parent, "تنبيه", "أدخل رابطًا صحيحًا")
            return
        self._start(url)
        self.view.clear_url()

    def test_downloads(self):
        for url in TEST_LINKS:
            self._start(url)

    # ---------- الأقسام ----------

    def change_category(self, category):
        if category == 'settings':
            print('Settings: غير منفذة بعد')
            return
        self.model.category = category
        self.view.refresh_items()

    # ---------- الخيط الخلفي ----------

    def _download_worker(self, task_id, url):
        try:
            task = SmartDL(url, DEST_DIR, progress_bar=False)

            # ✅ حارس 1: أُلغيت أثناء إنشاء الاتصال؟
            if task_id in self.model.cancel_requested or task_id not in self.model.items:
                return

            self.model.register_task(task_id, task)

            # ✅ حارس 2: أُلغيت بين الفحص والتسجيل؟
            if task_id in self.model.cancel_requested or task_id not in self.model.items:
                return

            try:
                task.start(blocking=False)
            except TypeError:
                task.start(blocking=True)

            # اسم الملف الحقيقي (من الترويسات)
            try:
                dest = self._get_dest_path(task)
                if dest and dest.name:
                    self.queue.put(("renamed", (task_id, dest.name)))
            except Exception:
                pass

            last_size = "--"
            while not task.isFinished():

                # ✅ حارس 3: أُلغيت أثناء التنزيل؟ اخرج فورًا
                if task_id not in self.model.items:
                    return

                try:
                    pct = task.get_progress()
                    if isinstance(pct, str):
                        pct = float(pct.rstrip('%')) / 100
                    if pct > 1:
                        pct = pct / 100
                except Exception:
                    pct = 0.0

                try:
                    if task.filesize:
                        last_size = utils.sizeof_human(task.filesize)
                except Exception:
                    pass

                speed = "--"
                ct = getattr(task, 'control_thread', None)
                if ct is not None:
                    try:
                        speed = "{}/s".format(
                            utils.sizeof_human(ct.get_speed()))
                    except Exception:
                        pass

                eta = "--"
                try:
                    eta = utils.time_human(task.get_eta(), trim_miliseconds=True)
                except Exception:
                    pass

                self.queue.put(("progress",
                                (task_id, pct, speed, last_size, eta)))
                time.sleep(0.3)

            # ✅ حارس 4: أُلغيت لحظة النهاية؟ لا ترسل حالة لعنصر محذوف
            if task_id not in self.model.items:
                return

            if task.isSuccessful():
                try:
                    size = utils.sizeof_human(task.filesize)
                except Exception:
                    size = last_size
                self.queue.put(("task_done", (task_id, size)))
            else:
                self.queue.put(("task_failed", task_id))

        except Exception as e:
            traceback.print_exc()
            self.queue.put(("error", (task_id, str(e))))

    # ---------- أزرار التحكم ----------

    def pause_download(self, task_id):
        task = self.model.get_task(task_id)
        if task:
            try:
                task.pause()
            except Exception as e:
                self.queue.put(("error", (task_id, str(e))))

    def cancel_download(self, task_id):
        """
        يقرأ الحالة من الموديل — لا يعتمد على وجود SmartDL حي.
        task = None يعني: ما زالت تتصل، أو عنصر مستعاد من الجلسة السابقة.
        """
        data = self.model.items.get(task_id)
        if data is None:
            return
        task = self.model.get_task(task_id)
        status = data.get('status', 'downloading')
        filename = data.get('filename', '?')

        # ---- 1) مهمة حية مكتملة: اسأل عن حذف الملف من النظام ----
        if task is not None and self._is_completed(task):
            answer = messagebox.askyesnocancel(
                self.parent, 'Delete Entry',
                'Do you want delete file also from system?')
            if answer is None:                 # أغلق الحوار → لا شيء
                return
            if answer:
                self._delete_file(task)        # حذف الملف + الأجزاء
            self._remove_entry(task_id)        # No → حذف السجل فقط
            return

        # ---- 2) مهمة حية ما زالت تنزّل: تأكيد الإلغاء ----
        if task is not None and not self._is_stopped_or_failed(task):
            if not messagebox.askyesno(
                    self.parent, "تأكيد الإلغاء",
                    f"هل تريد إلغاء تنزيل:\n{filename}؟", icon='warning'):
                return
            self._remove_entry(task_id)
            self.thread(self._cancel_worker, args=(task_id, task))
            return

        # ---- 3) مهمة حية متوقفة/فاشلة: حذف مباشر (كالسلوك الأصلي) ----
        if task is not None:
            self._remove_entry(task_id)
            self.thread(self._cancel_worker, args=(task_id, task))
            return

        # ---- 4) لا توجد مهمة حية (SmartDL لم يُنشأ أو عنصر مستعاد) ----

        # 4-أ) ما زالت في مرحلة الاتصال → تأكيد الإلغاء
        if status == 'downloading':
            if not messagebox.askyesno(
                    self.parent, "تأكيد الإلغاء",
                    f"هل تريد إلغاء تنزيل:\n{filename}؟", icon='warning'):
                return
            self.model.cancel_requested.add(task_id)   # الخيط الخلفي سيتحقق
            self._remove_entry(task_id)
            return

        # 4-ب) عنصر مستعاد ومكتمل → اسأل عن ملف النظام (بلا SmartDL)
        if status == 'done':
            answer = messagebox.askyesnocancel(
                self.parent, 'Delete Entry',
                'Do you want delete file also from system?')
            if answer is None:
                return
            if answer:
                self._delete_file_by_name(filename)
            self._remove_entry(task_id)
            return

        # 4-ج) عنصر مستعاد متوقف/فاشل → حذف مباشر
        self._remove_entry(task_id)

    def _remove_entry(self, task_id):
        """إزالة السجل من الموديل وتحديث العرض — الخيط الرئيسي فقط."""
        self.model.pop_item(task_id)
        self.view.refresh_items()

    def _cancel_worker(self, task_id, task):
        """stop → انتظار حقيقي (حاجب هنا لا مشكلة) → حذف الأجزاء."""
        if task is not None:
            try:
                task.stop()
            except Exception:
                pass
            self._wait_stopped_sync(task)
            self._delete_temp_file(task)

    def _wait_stopped_sync(self, task, timeout=5.0):
        start = time.time()
        while time.time() - start < timeout:
            try:
                if task.isFinished():
                    break
            except Exception:
                break
            time.sleep(0.1)
        time.sleep(0.3)

    # ---------- دوال مساعدة ----------

    def _is_completed(self, task):
        try:
            return task.isFinished() and task.isSuccessful()
        except Exception:
            return False

    def _is_stopped_or_failed(self, task):
        try:
            return task.isFinished() and not task.isSuccessful()
        except Exception:
            return False

    def _get_dest_path(self, task):
        try:
            if hasattr(task, 'get_dest'):
                return Path(task.get_dest())
            if hasattr(task, 'dest'):
                return Path(task.dest)
            if hasattr(task, 'filepath'):
                return Path(task.filepath)
        except Exception:
            pass
        return None

    def _delete_file(self, task, item=None):
        """حذف الملف النهائي المكتمل (لعنصر له SmartDL حي)."""
        try:
            dest = self._get_dest_path(task)
            if dest and dest.exists():
                dest.unlink()
                print(f"تم حذف الملف من النظام: {dest.name}")
            self._delete_temp_file(task)
        except Exception as e:
            messagebox.showerror(self.parent, "خطأ في الحذف", str(e))

    def _delete_file_by_name(self, filename):
        """حذف ملف مكتمل مستعاد من القرص — بالاسم فقط (لا SmartDL موجود)."""
        try:
            dest = Path(DEST_DIR) / filename
            if dest.exists():
                dest.unlink()
                print(f"تم حذف الملف من النظام: {dest.name}")
            self._cleanup_temp_files(dest)
        except Exception as e:
            messagebox.showerror(self.parent, "خطأ في الحذف", str(e))

    def _delete_temp_file(self, task, retries=3, delay=0.5):
        dest = self._get_dest_path(task)
        if dest is None:
            return
        self._cleanup_temp_files(dest, retries, delay)

    def _cleanup_temp_files(self, dest, retries=3, delay=0.5):
        """حذف الملف + .part + الأجزاء الرقمية — مع إعادة المحاولة للمقفل."""
        try:
            folder = dest.parent
            name = dest.name

            candidates = [dest, Path(str(dest) + '.part')]
            for f in folder.glob(name + '.*'):
                if f.suffix.lstrip('.').isdigit():
                    candidates.append(f)

            remaining = list(candidates)
            for attempt in range(retries):
                still_locked = []
                for path in remaining:
                    try:
                        if path.exists():
                            path.unlink()
                    except Exception:
                        still_locked.append(path)
                remaining = still_locked
                if not remaining:
                    break
                time.sleep(delay)

            if remaining:
                print(f"⚠ تعذر حذف {len(remaining)} ملف (مقفل): "
                      + ", ".join(p.name for p in remaining))
        except Exception:
            pass

    # =====================================================
    # معالجات رسائل القائمة — تعمل في الخيط الرئيسي فقط
    # =====================================================

    def on_progress(self, data):
        task_id, pct, speed, size, eta = data

        self.model.update_item(task_id, **({'pct': pct, **({'size': size} if size != '--' else {})}))

        item = self.view.item_widgets.get(task_id)
        if item:
            item.update_progress(pct, speed, size, eta)

        now = time.time()
        if now - getattr(self, '_last_save', 0.0) > 10:
            self._last_save = now
            self.model.save()

    def on_renamed(self, data):
        task_id, name = data
        self.model.update_item(task_id, filename=name)
        self.model.save()
        item = self.view.item_widgets.get(task_id)
        if item:
            item.set_filename(name)

    def on_task_done(self, data):
        task_id, size = data
        self.model.update_item(task_id, status='done', pct=1.0, size=size)
        self.model.save()
        self.view.refresh_items()

    def on_task_failed(self, task_id):
        self.model.update_item(task_id, status='failed')
        self.model.save()
        self.view.refresh_items()

    def on_error(self, data):
        task_id, msg = data
        messagebox.showerror(self.parent, "خطأ", msg)
        self._remove_entry(task_id)

    def on_remove_item(self, task_id):
        self._remove_entry(task_id)

# =========================================================
# التنسيق العام
# =========================================================

def style_tkinter(root: tk.Tk) -> None:
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(family="Segoe UI", size=9)

    root.configure(bg=BACKGROUND_2)
    root.option_add('*Ttk*background', BACKGROUND_2)
    root.option_add('*Button*relief', 'flat')
    root.option_add('*Button*font', FONT_ICON)
    root.option_add('*Frame*background', BACKGROUND_2)
    root.option_add('*Label*background', BACKGROUND_2)


# =========================================================
# نقطة البداية
# =========================================================

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('860x550')
    root.title('Downloader')
    root.iconbitmap(r'src/icon.ico')

    style_tkinter(root)

    app = DownloadController(root, DownloaderView, Model)

    app.mainloop()