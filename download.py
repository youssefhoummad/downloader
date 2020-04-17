import os
import urllib.request

from pytube import YouTube


default_download_path = os.path.expanduser(r'~\Downloads')


class DownloadItem():
    def __init__(self, url, video=False):
        self.url = url
        self.progress = 0
        self.filename = ''
        self.save_as = ''
        self.status = ''
        self.is_video = video


    def download(self):
        if self.is_video:
            self.download_video()
        else:
            self.download_file()


    def download_video(self):
        df_res = '720p'
        yt = YouTube(url)

        self.filename = yt.title
        yt.register_on_progress_callback(self.progress_video)

        try:
            self.status = 'downloading'
            yt.streams.get_by_resolution(df_res).download(output_path=default_download_path)
            self.status = 'complete'
        except:
            yt.streams.get_highest_resolution().download(output_path=default_download_path)
            print(f'downloading highesrt resolution possible')


    def download_file(self):
        self.filename = self.url[self.url.rfind("/")+1:]
        self.save_as = os.path.join(default_download_path, self.filename)

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
            print(self.progress)


    def progress_video(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining 
        self.progress = bytes_downloaded / total_size * 100
        print(self.progress)



        


if __name__ == "__main__":
    import sys

    url = sys.argv[1]
    if len(sys.argv) > 2:
        video = True
    else:
        video = False
    
    print(f'is video: {video}')

    item = DownloadItem(url, video=video)
    print(item.status)
    item.download()
    print(item.filename)
