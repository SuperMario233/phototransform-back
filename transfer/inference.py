import argparse
import os

import torch
import torch.nn as nn

from loadData import Dataset, load_image, save_image
from networks import ForwardNet, InverseNet, StyleSwap, img2Tensor

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
args = parser.parse_args()

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
    forwardNet = torch.load(args.forward_saved)
inverseNet = torch.load(args.inverse_saved)

###############################################################################
#Inference...
###############################################################################

style = Variable(style, requires_grad=False).unsqueeze(0)
style_feature = forwardNet(style)
style_feature = style_feature.squeeze(0)
style_swap = StyleSwap(style_feature, args.patch_size)

content = Variable(style, requires_grad=False).unsqueeze(0)
content_feature = forwardNet(content)
#do feature style swap.
feature_swapped = style_swap(content_feature)
#decode to get img.
target_img = inverseNet(feature_swapped).squeeze(0)

save_image(target_img, args.save)