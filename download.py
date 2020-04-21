import os
import urllib.request

from pytube import YouTube, Playlist

from progress import printProgressBar


default_download_path = os.path.expanduser(r'~\Downloads')

default_resolution = "720p"


class DownloadItem():
    def __init__(self, url, mode='file'):
        self.url = url
        self.progress = 0
        self.totalsize = None
        self.filename = None
        self.save_as = None
        self.status = None
        self.mode = mode



    def download(self):
        if self.mode in ('video', 'v', '-v'):
            self.download_video()

        elif self.mode in ('playlist', 'p', '-p'):
            self.download_playlist()

        else:
            self.download_file()


    def download_playlist(self):
        pl = Playlist(self.url)

        for url in pl.video_urls:
            self.url = url
            self.download_video()
 

    def download_video(self):
        yt = YouTube(self.url)

        self.filename = yt.title
        yt.register_on_progress_callback(self.progress_video)

        printProgressBar(0, 100)
    
        try:
            self.status = 'downloading'
            yt.streams.get_by_resolution(default_resolution).download(output_path=default_download_path)
            self.status = 'complete'
        except:
            yt.streams.get_highest_resolution().download(output_path=default_download_path)
            print(f'downloading highesrt resolution possible')


    def download_file(self):
        self.filename = self.url[self.url.rfind("/")+1:]
        self.save_as = os.path.join(default_download_path, self.filename)
        printProgressBar(0, 100)
        try:
            self.status = 'downloading'
            urllib.request.urlretrieve(self.url, self.save_as, self.progress_file)
            self.status = 'complete'
        except:
            self.status = 'Faild'


    def progress_file(self, blocknum, blocksize, totalsize):
        readsofar = blocknum * blocksize
        if totalsize > 0:
            self.progress = readsofar * 100 / totalsize

            printProgressBar(int(self.progress), 100)


    def progress_video(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining 
        self.progress = bytes_downloaded / total_size * 100

        printProgressBar(int(self.progress), 100)



        


if __name__ == "__main__":
    import sys, getopt


    try:
        url = sys.argv[1]
    except:
        print("enter the url")


    if len(sys.argv) > 2:
        mode = sys.argv[2]
    else:
        mode = 'file'
 

    item = DownloadItem(url, mode=mode)
    # print(item.status)
    item.download()
    # print(item.filename)
