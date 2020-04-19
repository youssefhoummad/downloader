import threading
import time

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from download import DownloadItem


headers = ["file name", "ext", "status", "url"]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.next_row = 0
    
    def initUI(self):
        self.setFixedSize(700, 400)
        self.setWindowTitle('Download Manager')
        self.setWindowIcon(QIcon('icons\\app.png'))    
        
        self.initToolbar()
        self.initStatusBar()
        self.initTable()

        self.show()


    def initToolbar(self):
        self.toolbar = self.addToolBar('Main')
        self.toolbar.setMovable(False)

        newAct = QAction(QIcon('icons/new.png'), 'new', self)
        newAct.setShortcut('Ctrl+N')
        newAct.setStatusTip('new downlaod')
        # newAct.triggered.connect(self.new)

        listAct = QAction(QIcon('icons/list.png'), 'list', self)
        listAct.setShortcut('Ctrl+shift+N')
        listAct.setStatusTip('new list to downlaod')
        # listAct.triggered.connect(self.new_list)

        youtubeAct = QAction(QIcon('icons/youtube.png'), 'youtube', self)
        youtubeAct.setShortcut('Ctrl+Y')
        youtubeAct.setStatusTip('download video from youtube')
        # youtubeAct.triggered.connect(self.remove)

        settingsAct = QAction(QIcon('icons/settings.png'), 'settings', self)
        settingsAct.setShortcut('Ctrl+U')
        settingsAct.setStatusTip('settings')
        # settingsAct.triggered.connect(self.settings)

        self.toolbar.addAction(newAct)
        self.toolbar.addAction(listAct)
        self.toolbar.addAction(youtubeAct)
        self.toolbar.addAction(settingsAct)


    def initStatusBar(self):
        self.status = self.statusBar()
        self.progress = QProgressBar(self.status)
        self.progress.setGeometry(290, 0, 400, 20)
        self.progress.setValue(0)


    def initTable(self):
        self.table = QTableWidget(self)

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setGeometry(QRect(5, 40, 690, 335))
        self.table.setRowCount(0)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(headers)

        self.table.verticalHeader().setVisible(False)

        self.table.setColumnWidth(0,180)
        self.table.setColumnWidth(1,60)
        self.table.setColumnWidth(2,85)
        self.table.setColumnWidth(3,360)


    def new_download(self, url, mode):
        self.table.insertRow(self.next_row)

        item = DownloadItem(url, mode)

        download = threading.Thread(target=item.download)
        download.start()

        def thread_table(item):
            while item.filename == '':
                _ = ''
            
            data = [item.filename, '.tst', item.status, item.url]
            
            for i, name in enumerate(data):
                self.table.setItem(self.next_row, i, QTableWidgetItem(str(name)))
            
            self.next_row += 1


        def thread_progressbar(item):
            while item.status != 'complete':
                self.progress.setValue(int(item.progress))

        t = threading.Thread(target=thread_table, args=(item,))
        t.start()

        p = threading.Thread(target=thread_progressbar, args=(item,))
        p.start()



if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = MainWindow()

    ex.new_download('https://www.youtube.com/watch?v=_RDxU7l05Nw', 'video')

    sys.exit(app.exec_())