import os
import pickle
# from src.constants import DEST


class DL_Object:
  def __init__(self, url, dst, filename, extension, size, progress='100%', status='finished'):
    self.url = url
    self.dst = dst
    self.filename = filename
    self.extension = extension
    self.size = size
    self.progress = progress
    self.status = status
  

  @property
  def args(self):
    return [self.url, self.dst, self.filename, self.extension, self.size, self.progress, self.status]


class Database:
  def __init__(self):
    self._data = self.load()
    
  def __getitem__(self, index):
    return self._data[index]

  def __delitem__(self, index):
    del self._data[index]

  def __contains__(self, value):
    return value in self._data

  def __len__(self):
    return len(self._data)

  def __repr__(self):
    return repr(self._data)
  
  def __iter__(self):
    for d in self._data:
      yield d

  def append(self, obj):
    if obj.dl_object:
      print('------- obj removed ---------')
      self._data.remove(obj)
      obj = DL_Object(obj.url, obj.dst, obj.filename, obj.extension, obj.size.get())
    self._data.append(obj)
  
  def remove(self, obj):
    self._data.remove(obj)
  

  def revision(self, obj):
    obj = DL_Object(obj.url, obj.dst, obj.filename, obj.ext, obj.get_progress(),obj.get_dl_size())
      # 'time':obj.get_dl_time(),

    return [obj]

  
  def save(self, obj):
    # obj = self.revision(obj)
    self.data.append(obj)

    if not os.path.exists('database'):
      os.makedirs('database')

    with open('database\\file.pkl', 'wb') as f:
      pickle.dump(obj, f)


  def load(self):
    # directory = 'database'
    # for file in os.listdir(directory):
    #   if file.endswith(".pkl"): 
    #     with open(os.path.join(directory, file), 'rb') as file:
    #       obj = pickle.load(file)
    #       print(obj)
    #       self.database.append(obj)
    DEST = os.path.expanduser(r'~\Downloads')

    dict_from_obj = DL_Object(
      url ='https=//github.com/iTaybb/pySmartDL/raw/master/test/7za920.zip',
      dst = DEST + '\\7za920.zip',
      filename ='7za920.zip',
      extension = '.zip',
      progress ='100%',
      size ='327 Kb'
      # 'time':obj.get_dl_time(),
    )
    return [dict_from_obj]

    
if __name__ == '__main__':
  d = Database()
  d.load()
  # obj = [1, 2, 3, 4]
  # d.save(obj)