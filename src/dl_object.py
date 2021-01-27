import os
import pickle
import ntpath
import uuid

from pySmartDL import SmartDL


class ItemDL(SmartDL):
  def __init__(self, url, dest, *args, **kwargs):
    super().__init__(url, dest, *args, **kwargs)

    self.id = uuid.uuid4()


  
  @property
  def filename(self):
    head, tail = ntpath.split(self.get_dest())
    return tail or ntpath.basename(head)

  @property
  def extension(self):
    dest = self.get_dest()
    return os.path.splitext(dest)[1]


  def save(self):
    dict_to_save = {
      'id': self.id,
      'url': self.url,
      'filename': self.filename,
      'extension': self.extension,
      'progress': self.get_progress(),
      'size': self.get_dl_size()

    }
    with open(f'{self.id}.pkl', 'wb') as itemDL_file:
      pickle.dump(dict_to_save, itemDL_file)
    print('itemDL saved..')
    

  # def load(self):
  #   with open('file1.pkl', 'rb') as itemDL_file:
  #     item = pickle.load(itemDL_file)
  #     print(item)



if __name__ == '__main__':
  from constants import DEST
  utl = 'https://image.freepik.com/free-vector/business-card-template-with-home-schooling-logo-design-pemium-vector_154104-125.jpg'
  item = ItemDL(utl, DEST)
  # item.save()
  # item.load()