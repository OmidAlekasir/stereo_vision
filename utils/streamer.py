import os
import cv2

class Streamer():
    def __init__(self, path):

        self.path = path
        self.files = os.listdir(self.path)
        self.files.sort()
        self.idx = 0

    def get(self):

        if self.idx >= len(self.files):
            return None

        last_image = self.files[self.idx]
        img_path = os.path.join(self.path, last_image)
        self.idx += 1

        return cv2.imread(img_path)