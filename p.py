#encoding:utf-8

import requests
import time
import os
import pickle
import json

LIST_URL = 'https://apis.qupeiyin.com/course/get_course_list?sign=37424885dff971f806afdfe93c21dba1&timestamp=%s&uid=-1&level=all&sort=new&start=%s&category_id=2&ishow=0&rows=%s&nature_id=all'

DETAIL_URL = "https://apis.qupeiyin.com/course/detail_new?sign=72ee4ff75aa4d70e01b77bee95294d40&timestamp=%s&uid=-1&course_id=%s"

def get_lst(start = 0, per_page = 100, retry = 3):
  lst = []
  while retry > 0:
    timestamp = int(time.time())
    url  = LIST_URL % (str(timestamp), start, per_page)
    start += per_page
    try:
      r = requests.get(url)
    except Exception as e:
      print e
      retry -= 1
      continue
    try:
      data = r.json()
      if data['status'] != 1:
        continue
        retry -= 1
      if len(data['data']) == 0:
        print 'no data'
        break
    except Exception as e:
      print e
      retry -= 1
      continue
    return data['data']

def get_detail(cid = 0, retry = 3):
  while retry > 0:
    timestamp = int(time.time())
    url = DETAIL_URL % (timestamp, cid)
    try:
      r = requests.get(url)
    except Exception as e:
      print e
      retry -= 1
      continue
    try:
      data = r.json()
      if data['status'] != 1:
        continue
        retry -= 1
      if len(data['data']) == 0:
        print 'no data'
        break
    except Exception as e:
      print e
      retry -= 1
      continue
    return data['data']

def download(url, path):
  local_filename = url.split('/')[-1]  
  print "Download File=", local_filename  
  r = requests.get(url, stream=True)
  with open(path + local_filename, 'wb') as f:  
    for chunk in r.iter_content(chunk_size=1024):  
      if chunk:
        f.write(chunk)  
        f.flush()
    f.close()  
  return local_filename 
    

if __name__ == "__main__":
  start = 0
  per_page = 100
  j = []
  while True:
    lst = get_lst(start, per_page)
    if len(lst) == 0:
      break
    start += per_page
    for i in lst:
      cid = i['id']
      info = get_detail(cid)
      o = {"title": info['title'], "desc": info["description"], "image": {"url": info["pic"], "width": 0, "height": 0}, "video": info["video"], "length": 0}
      j.append(o)
      if not os.path.isdir('./data/%s' % (cid, )):
        os.mkdir('./data/%s' % (cid, ))
      with open('./data/%s/%s' % (cid, 'info.json'), 'wb') as f:
        f.write(json.dumps(info))
        f.close()
      keys = ["video", "video_srt", "video_small", "audio", "pic", "subtitle_en"]
      for k in keys:
        try:
          if not os.path.isfile('./data/%s/%s' % (cid, info[k].split('/')[-1])):
            try:
              download(info[k], './data/%s/' % (cid, ))
            except Exception as e:
              print "exception@ %s" % (info[k], )
              print e
          else:
            print "skip %s" % (info[k], )
        except:
          pass
  with open("./data/%s" % ("lst.json"), "wb") as f:
    f.write(json.dumps(j))
    f.close()
