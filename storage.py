import os
import os.path
import hashlib
import string
import requests
import json
from PIL import Image

GOOD_CHARS = "-_.() %s%s" % (string.ascii_letters, string.digits)
IMG_LIST_FILE = "data/list.json"

class storage:
    def __init__(self) -> None:
        os.makedirs("data", exist_ok=True)
        if os.path.isfile("list.json"):
            os.rename("list.json", IMG_LIST_FILE)
        if not os.path.isfile(IMG_LIST_FILE):
            with open(IMG_LIST_FILE, "w") as f:
                f.write('[]')
                f.close()

    def sanitize(self, name):
        return ''.join(c for c in name if c in GOOD_CHARS)[:230].replace(' ', '_')
    
    def path(self, src):
        ext = src["img"].split(".")[-1]
        if len(ext)>4 or self.sanitize(ext)!=ext: ext = 'jpg'

        if not os.path.isdir('static'):
            os.makedirs('static')

        path = "static/" + self.sanitize(src["title"]) + "_" + hashlib.sha1(src["img"].encode()).hexdigest()[0:6] + "." + ext

        # check old filename format
        old_path = "static/" + hashlib.sha1(src["img"].encode()).hexdigest() + "." + ext
        if os.path.isfile(old_path): os.rename(old_path, path)

        # new format
        return path

    def download_img(self, src, path):
        print("Downloading", src, "to", path)
        res = requests.get(src)
        if not res.ok:
            return False
        if not res.headers.get("content-type").startswith("image/"):
            return False
        with open(path, 'wb') as f:
            f.write(res.content)
        return True

    def download(self, src):
        path = self.path(src)
        
        if os.path.isfile(path):
            return path
            
        if not self.download_img(src["img"], path):
            return None

        optimized_path, thumb_path = self.optimize_img(path)

        imgs = json.load(open(IMG_LIST_FILE, "r"))
        src["selected"] = 0
        src["original_path"] = path
        src["path"] = optimized_path
        src["thumb_path"] = thumb_path
        imgs.append(src)
        with open(IMG_LIST_FILE, "w") as f:
            json.dump(imgs, f)

        return path

    def open_img_as_rgb(self, path):
        img = Image.open(path)
        if img.mode != "RGB":
            converted = img.convert("RGB")
            img.close()
            return converted
        return img

    def optimize_img(self, path):
        optimized_path = path + ".opt.jpg"
        thumb_path = path + ".64.jpg"
        with self.open_img_as_rgb(path) as img:
            img.save(optimized_path, "JPEG", quality=70, optimize=True, progressive=True)
            img.thumbnail((64, 64))
            img.save(thumb_path, "JPEG", quality=50, optimize=True)
        return optimized_path, thumb_path
    
    def get_list(self):
        return json.load(open(IMG_LIST_FILE, "r"))

    def select(self, path, val):
        imgs = json.load(open(IMG_LIST_FILE, "r"))
        for i in imgs:
            if i["path"] == path:
                i["selected"] = val
                print("selected set.")
                break
        with open(IMG_LIST_FILE, "w") as f:
            json.dump(imgs, f)