import argparse
import os
import sys
import time

import torch
import torch.nn as nn
import torch.optim as optim

from torch.autograd import Variable
from torch.utils.data import DataLoader

from loadData import Dataset
from networks import ForwardNet, InverseNet, StyleSwap

parser = argparse.ArgumentParser(description="Style Transfer")

parser.add_argument("--epochs", type=int, default=5,
                    help="number of training epoches.")
parser.add_argument("--batch_size", type=int, default=20,
                    help="batch size for training.")
parser.add_argument("--image_size", type=int, default=256,
                    help="size of training images, default is 256 x 256.")
parser.add_argument("--patch_size", type=int, default=15,
                    help="the size of patch, default is 15 x 15.")
parser.add_argument("-seed", type=int, default=42,
                    help="random seed for training.")
parser.add_argument("--lr", type=float, default=1e-3,
                    help="learning rate.")
parser.add_argument("--decay", type=float, default=1e-4,
                    help="learning rate decay.")
parser.add_argument("--tv", type=float, default=1e-6,
                    help="the coefficient for tv-loss.")
parser.add_argument("--content", type=str, required=True,
                    help="Path to the content images.")
parser.add_argument("--style", type=str, required=True,
                    help="path to the style images.")
parser.add_argument("--save", type=str, default="save/",
                    help="path to save the model.")
parser.add_argument("--forward_saved", type=str, default="NULL",
                    help="the path of the pre-trained forward networks.")
parser.add_argument("--log_interval", type=int, default=500,
                    help="print log_infor every log_interval.")
args = parser.parse_args()

###############################################################################
#Loading Dataset...
###############################################################################
train_content_loader = DataLoader(Dataset(args.content), batch_size=args.batch_size, shuffle=True)
train_style_loader = DataLoader(Dataset(args.style), batch_size=1, shuffle=True)

###############################################################################
#Building Networks...
###############################################################################
if args.forward_saved=="NULL":
    forwardNet = ForwardNet(pretrain=True)
    torch.save(forwardNet, os.path.join(args.save, "forward_model.pt"))
else:
    forwardNet = torch.load(args.forward_saved)
inverseNet = InverseNet()

args.save = '{}-{}-ep{}'.format(args.save, time.strftime("%d-%H%M"), epoch)

###############################################################################
#Define Loss and Optimizer...
###############################################################################
def tv_loss(y):
    tv = args.tv * (
    torch.sum( torch.abs( y[:,:,:,:-1] - y[:,:,:,1:])) + torch.sum( torch.abs( y[:,:,:-1,:] - y[:,:,1:,:])) )
    return tv

loss_func = nn.MSELoss(size_average=False)
optimizer = optim.Adam(inverseNet.parameters(), lr=args.lr, weight_decay=args.decay)

###############################################################################
#Training...
###############################################################################
for epoch in range(args.epochs):
    print("Now training the {}th epoch.".format(epoch))

    cnt=0
    for i, style in enumerate(train_style_loader):
        style = Variable(style, requires_grad=False)
        style_feature = forwardNet(style)
        style_feature = style_feature.squeeze(0)
        style_swap = StyleSwap(style_feature, args.patch_size)

        for j, content in enumerate(train_content_loader):
            
            optimizer.zero_grad()
            content = Variable(content, requires_grad=False)

            content_feature = forwardNet(content)
            #print("feature size: ", content_feature.size(), style_feature.size())
            feature_styled = style_swap(content_feature)
            #print("feature_swapped size: ", feature_styled.size())
            inversed_content_styled = inverseNet(feature_styled)
            #print("inversed_pic_size:", inversed_content_styled.size())
            inversed_feature_styled = forwardNet(inversed_content_styled)
            
            loss = loss_func(inversed_feature_styled, feature_styled) + tv_loss(inversed_content_styled)
            
            loss.backward()
            optimizer.step()

            cnt += 1
            if(cnt%args.log_interval == 0):
                print("Current Epoch:{.3d} | Batches_Cnt:{.3d} | Style_Idx:{.3d} | Content_Idx:{.3d} | Loss:{.3f}".format(epoch, cnt, i, j, loss))
    #save inverseNet.
    torch.save(inverseNet, os.path.join(args.save, 'inverse_model.pt'))


if __name__ == "__main__":
    print('here in main!')