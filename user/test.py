import os
import cv2

path = './shots'

images = []
class_name = []

img_list = os.listdir(path)
print(img_list)

for img in img_list:
    curr_img = cv2.imread(f'{path}/{img}')
    images.append(curr_img)
    class_name.append(os.path.splitext(img)[0])
print(class_name)