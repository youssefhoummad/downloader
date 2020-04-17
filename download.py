import os
import urllib.request


default_download_path = os.path.expanduser(r'~\Downloads')


class DownloadItem():
    def __init__(self, url):
        self.url = url
        self.progress = 0
        self.filename = ''
        self.save_as = ''
        self.status = ''

        self.get_info()


    def download(self):
        try:
            self.status = 'downloading'
            urllib.request.urlretrieve(self.url, self.save_as, self.report)
            self.status = 'complete'
        except:
            self.status = 'Faild'


    def report(self, blocknum, blocksize, totalsize):
        readsofar = blocknum * blocksize
        if totalsize > 0:
            percent = readsofar * 100 / totalsize
            self.progress = int(percent)


    def get_info(self):
        self.filename = self.url[self.url.rfind("/")+1:]
        self.save_as = os.path.join(default_download_path, self.filename)


if __name__ == "__main__":
    import sys

    url = sys.argv[1]
    item = DownloadItem(url)
    print(item.status)
    item.download()
    print(item.filename)
