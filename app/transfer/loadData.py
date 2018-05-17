import torch

from PIL import Image

import os
from os import listdir
from os.path import join

import torch.utils.data as data
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision import datasets

import numpy

def is_image_file(filename):
    return any(filename.endswith(extension) for extension in [".png", ".jpg", ".jpeg"])

def load_image(filename, size=None, scale=None):
    img = Image.open(filename)
    if size is not None:
        img = img.resize((size, size), Image.ANTIALIAS)
    elif scale is not None:
        img = img.resize((int(img.size[0]/scale), int(img.size[1]/scale)), Image.ANTIALIAS)
    return img

def save_image(imgTensor, filename):
    img = transforms.ToPILImage(mode="RGB")(imgTensor)
    img.show()
    img.save(filename)
    return

def img2Tensor(img, image_size=None):
    img = img.convert("RGB")
    if image_size:
        img = transforms.Resize(image_size)(img)
    tensor = transforms.ToTensor()(img)
    return tensor

class Dataset(data.Dataset):
    def __init__(self, folderPath, image_size=256):
        super(Dataset, self).__init__()
        self.folderpath = folderPath
        self.image_size = image_size
        self.transform = transforms.Compose([
            transforms.Resize(image_size),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
        ])
        self.image_list = [x for x in listdir(folderPath) if is_image_file(x)]

    def __getitem__(self, index):
        img_path = os.path.join(self.folderpath, self.image_list[index])
        img = load_image(img_path)
        img = img.convert("RGB")
        img = self.transform(img)
        return img

    def __len__(self):
        return len(self.image_list)

if __name__=='__main__':
    data = Dataset("../data/")
    for i in data:
        img = transforms.ToPILImage(mode="RGB")(i)
        img.show()
        break
