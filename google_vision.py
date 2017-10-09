import requests
import json
import base64
import os
import glob
import concurrent.futures 
import sys


GOOGLE_CLOUD_VISION_API_URL = 'https://vision.googleapis.com/v1/images:annotate?key='
API_KEY = os.environ['GOOGLE']
def goog_cloud_vison(image_content):
    api_url = GOOGLE_CLOUD_VISION_API_URL + API_KEY
    req_body = json.dumps({
        'requests': [{
            'image': {
                'content': image_content.decode()
            },
            'features': [{
                'type': 'LABEL_DETECTION',
                'maxResults': 100,
            }]
        }]
    })
    res = requests.post(api_url, data=req_body)
    return res.json()

def img_to_base64(filepath):
    with open(filepath, 'rb') as img:
        img_byte = img.read()
    return base64.b64encode(img_byte)

def mapper( name ):
  try:
    save_name = 'vision/' + name.split('/').pop().replace('.jpg', '').replace('.png', '') + '.json'
    if os.path.exists(save_name) is True:
      return None
    img = img_to_base64(name)
    res_json = goog_cloud_vison(img)
    raw_obj = json.dumps( res_json, indent=2 ) 
    open(save_name, 'w').write( raw_obj )
    print(name)
  except Exception as e:
    print(e) 


if '--minimize' in sys.argv:
  from concurrent.futures import ProcessPoolExecutor
  from PIL import Image
  def _minimize(name):
    save_name = 'minimize/' + name.split('/').pop()
    if os.path.exists(save_name):
      return
    try:
      img = Image.open(name)
    except OSError as e:
      return
    size = img.size
    by = int(size[0]/1000)
    if by != 0:
      resize = (size[0]//by, size[1]//by)
      try:
        img = img.resize( resize )
      except OSError as e:
        return
    img.save(save_name)
    print( by, name  )
  names = [name for name in glob.glob('./download/*')]
  with ProcessPoolExecutor(max_workers=8) as exe:
    exe.map( _minimize, names)

if '--remove' in sys.argv:
  for name in glob.glob('vision/*'):
    o = json.loads(open(name).read())
    if o.get('error') is not None:
      os.remove(name)
      print( o )

if '--scan' in sys.argv:
  names = [name for name in glob.glob('minimize/*')]
  #[mapper(name) for name in names#]
  with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
    executor.map( mapper, names )
