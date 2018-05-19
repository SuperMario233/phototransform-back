import argparse
import os

import torch
import torch.nn as nn
from torch.autograd import Variable

from loadData import Dataset, load_image, save_image, img2Tensor
from networks import ForwardNet, InverseNet, StyleSwap

parser = argparse.ArgumentParser(description="Style Transfer")

parser.add_argument("--image_size", type=int, default=256,
                    help="size of training images, default is 256 x 256.")
parser.add_argument("--patch_size", type=int, default=15,
                    help="the size of patch, default is 15 x 15.")
parser.add_argument("--content", type=str, required=True,
                    help="Path to the content images.")
parser.add_argument("--style", type=str, required=True,
                    help="path to the style images.")
parser.add_argument("--save", type=str, default="save/demo.jpg",
                    help="path to save the model.")
parser.add_argument("--forward_saved", type=str, default="NULL",
                    help="the path of the pre-trained forward networks. (NULL: online loading)")
parser.add_argument("--inverse_saved", type=str, required=True,
                    help="the path of the pre-trained inverse networks.")
parser.add_argument("--gpuid", type=int, default=-1,
                    help="the gpu device to be used(default -1 means cpu).")
args = parser.parse_args()

args.cuda = (args.gpuid != -1)
#set device.
if args.cuda:
    assert torch.cuda.is_available() == True
    cuda.set_device(args.gpuid)
    torch.cuda.manual_seed_all(args.seed)

###############################################################################
#Loading Pictures(content and style)...
###############################################################################
content = img2Tensor(load_image(args.content), image_size=args.image_size)
style = img2Tensor(load_image(args.style), image_size=args.image_size)

###############################################################################
#Loading Model...
###############################################################################
if args.forward_saved=="NULL":
    forwardNet = ForwardNet(pretrain=True)
else:
    forwardNet = torch.load(args.forward_saved, map_location=lambda storage, loc: storage)
inverseNet = torch.load(args.inverse_saved, map_location=lambda storage, loc: storage)

if args.cuda:
    #model
    forwardNet = forwardNet.cuda()
    inverseNet = InverseNet.cuda()
    #data
    content = content.cuda()
    style = style.cuda()

forwardNet.eval()
inverseNet.eval()

###############################################################################
#Inference...
###############################################################################

style = Variable(style, requires_grad=False).unsqueeze(0)
style_feature = forwardNet(style)
style_feature = style_feature.squeeze(0)
style_swap = StyleSwap(style_feature, args.patch_size, cuda=args.cuda)
if args.cuda:
    style_swap = style_swap.cuda()

content = Variable(content, requires_grad=False).unsqueeze(0)
content_feature = forwardNet(content)
#do feature style swap.
feature_swapped = style_swap(content_feature)
#decode to get img.
target_img = inverseNet(feature_swapped).squeeze(0).cpu()
target_img = target_img.data

save_image(target_img, args.save)
