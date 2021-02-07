import os
try:
  from .database import Database
  from .win10toast import ToastNotifier
except:
  from database import Database
  from win10toast import ToastNotifier

IMAGES_EXT = [ '.jpg', 'jpeg', '.png', '.gif', '.webp', '.tiff', '.psd', '.raw', '.bmp', '.heif', '.indd', '.jpeg', '.svg', '.ai', '.eps']

VIDEO_EXT = ['.webm', '.mkv', '.flv', '.ogg', '.avi', '.mov', '.ts', '.wmv', '.mp4', '.3gp']

ARCHIVE_EXT = ['.zip', '.rar', '.7z']

DOCS_EXT = ['.doc', '.docx', '.pdf', '.ppt', '.pptx', '.odt', '.ods', '.txt', '.html', '.htm' '.xls', '.xlsx']

AUDIO_EXT = ['.flac', '.alac', '.mp3', '.aac', '.m4a', '.wav', '.wma']

PAUSE_IMAGES = [r'.\img\pause.emf', r'.\img\pauseHover.emf',r'.\img\pausePress.emf']

PLAY_IMAGES = [r'.\img\play.tif', r'.\img\playHover.tif',r'.\img\playPress.tif']

OPEN_IMAGES = [r'.\img\points.tif', r'.\img\pointsHover.tif',r'.\img\pointsPress.tif']

SEARCH_ICO = r'.\img\search.tif'

APP_ICO = r'.\img\icon.ico'

DEST = os.path.expanduser(r'~\Downloads')

toaster = ToastNotifier()

DATABASE = Database()