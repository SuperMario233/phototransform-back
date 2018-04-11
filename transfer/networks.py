import torch
import copy
import torch.nn.functional
import torch.nn as nn

from torch.nn import Conv2d
from torch.nn import InstanceNorm2d
from torch.nn import ReLU
from torch.nn import Parameter
from torch.autograd import Variable
from torchvision import models

class ForwardNet(nn.Module):
    def __init__(self, pretrain=False, requires_grad=False):
        super(ForwardNet, self).__init__()
        vgg19_pretrained_features = models.vgg19(pretrained=pretrain).features
        self.slice = torch.nn.Sequential()
        """
        Truncated features of vgg19:
        (0): Conv2d(3, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (1): ReLU(inplace)
        (2): Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (3): ReLU(inplace)
        (4): MaxPool2d(kernel_size=(2, 2), stride=(2, 2), dilation=(1, 1), ceil_mode=False)
        (5): Conv2d(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (6): ReLU(inplace)
        (7): Conv2d(128, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (8): ReLU(inplace)
        (9): MaxPool2d(kernel_size=(2, 2), stride=(2, 2), dilation=(1, 1), ceil_mode=False)
        (10): Conv2d(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        (11): ReLU(inplace)
        """
        for i in range(12):
            self.slice.add_module(str(i), vgg19_pretrained_features[i])
        if not requires_grad:
            for param in self.parameters():
                param.requires_grad = False

    def forward(self, x):
        return self.slice(x)

class InverseNet(nn.Module):
    def __init__(self):
        super(InverseNet, self).__init__()
        self.slice = torch.nn.Sequential()
        self.slice.add_module(str(0), Conv2d(256, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)))
        self.slice.add_module(str(1), InstanceNorm2d(128, affine=True))
        self.slice.add_module(str(2), ReLU())
        self.slice.add_module(str(3), nn.Upsample(scale_factor=2, mode="nearest"))
        self.slice.add_module(str(4), Conv2d(128, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)))
        self.slice.add_module(str(5), InstanceNorm2d(128, affine=True))
        self.slice.add_module(str(6), ReLU())
        self.slice.add_module(str(7), Conv2d(128, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)))
        self.slice.add_module(str(8), InstanceNorm2d(64, affine=True))
        self.slice.add_module(str(9), ReLU())
        self.slice.add_module(str(10), nn.Upsample(scale_factor=2, mode="nearest"))
        self.slice.add_module(str(11), Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)))
        self.slice.add_module(str(12), InstanceNorm2d(64, affine=True))
        self.slice.add_module(str(13), ReLU())
        self.slice.add_module(str(14), Conv2d(64, 3, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)))

    def forward(self, x):
        return self.slice(x)

"""
class UpsampleConvLayer(nn.Module):
    #UpsampleConvLayer
    #Upsamples the input and then does a convolution. This method gives better results
    #compared to ConvTranspose2d.
    #ref: http://distill.pub/2016/deconv-checkerboard/

    def __init__(self, in_channels, out_channels, kernel_size, stride, upsample=None):
        super(UpsampleConvLayer, self).__init__()
        self.upsample = upsample
        if upsample:
            self.upsample_layer = torch.nn.Upsample(scale_factor=upsample, mode="nearest")
        reflection_padding = kernel_size // 2
        self.reflection_pad = torch.nn.ReflectionPad2d(reflection_padding)
        self.conv2d = torch.nn.Conv2d(in_channels, out_channels, kernel_size, stride)

    def forward(self, x):
        x_in = x
        if self.upsample:
            x_in = self.upsample_layer(x_in)
        out = self.reflection_pad(x_in)
        out = self.conv2d(out)
        return out
"""

class StyleSwap(nn.Module):
    def __init__(self, style_img, patch_size, stride=1, shuffle=False, interpolate=True):
        super(StyleSwap, self).__init__()
        self.style_img = style_img
        self.patch_size = patch_size
        self.stride = stride
        self.shuffle = shuffle
        self.interpolate = interpolate
        
        #patches extracted from the style_image
        self.patches = self.getPatch(self.style_img)
        #convolution function used for style transferring.
        if self.interpolate:
            self.conv_enc, self.conv_dec, self.conv_intra = self.build(self.patches)
        else:
            self.conv_enc, self.conv_dec = self.build(self.patches)

    def getPatch(self, style):
        #style with size (channel, width, height)
        assert style.dim() == 3
        kh, kw = self.patch_size, self.patch_size
        dh, dw = self.stride, self.stride
        #get patches with size (channel, p_wnum, p_hnum, p_width, p_height)
        patches = style.unfold(1, kw, dw).unfold(2, kh, dh)
        n1, n2, n3, n4, n5 = patches.size(0), patches.size(1), patches.size(2), patches.size(3), patches.size(4)
        #permute patches with size (patch_num, features, p_width, p_height)
        patches = patches.permute(1, 2, 0, 3, 4).contiguous().view(n2*n3, n1, n4, n5)
        #shuffle the patches if needed.
        if self.shuffle:
            shuf = torch.randperm(patches.size(0)).long()
            patches = patches.index(shuf)
        #return patches with size(patch_num, features, p_width, p_height)
        return patches

    def forward(self, content):
        """
        content with size (batch, channel, width, height)
        """
        assert content.dim() == 4
        assert content.size(1) == self.style_img.size(0)

        mid_feature = self.conv_enc(content)
        mid_feature = self.maxCoord(mid_feature)
        output = self.conv_dec(mid_feature)
        if self.interpolate:
            weights = self.conv_intra(mid_feature)
            output /= weights
        output = output.detach()
        return output
    
    def build(self, target_patches):
        enc_patches = target_patches
        npatches, c = enc_patches.size(0), enc_patches.size(1)
        #for each patch, divide by its l2-norm (normalize)
        for i in range(npatches):
            enc_patches[i].mul(1 / (torch.norm(enc_patches[i], 2)+1e-8) )
        
        #conv_enc: 2D Convolution With Normalized Style Patches as Filters.
        conv_enc = Conv2d(c, npatches, kernel_size=(self.patch_size, self.patch_size), stride=(self.stride, self.stride))
        conv_enc.weight = Parameter(enc_patches.data)

        #conv_dec: 2D Transposed Convolution With Style Patches as Filters.
        conv_dec = nn.ConvTranspose2d(npatches, c, kernel_size=(self.patch_size, self.patch_size), stride=(self.stride, self.stride))
        conv_dec.weight = Parameter(target_patches.data)
        
        if self.interpolate:
            """
            #Here Could Remain Problems.!!!!!!!
            """
            conv_intra = nn.ConvTranspose2d(npatches, c, kernel_size=(self.patch_size, self.patch_size), stride=(self.stride, self.stride))
            conv_intra.weight = Parameter(torch.ones(npatches, c, self.patch_size, self.patch_size))
            return conv_enc, conv_dec, conv_intra
        else:
            
            return conv_enc, conv_dec

    def maxCoord(self, feature):
        nInputDim = feature.dim()
        if feature.dim() == 3:
            feature.unsqueeze(0)
        #feature with size (batch, channel, width, height)
        assert(feature.dim() == 4)
        
        _, argmax = torch.max(feature, 1)
        
        output = torch.zeros(feature.size())
        for i in range(feature.size(0)):
            for w in range(feature.size(2)):
                for h in range(feature.size(3)):
                    ind = argmax[i, w, h].data[0]
                    output[i, ind, w, h] = 1
        
        if nInputDim == 3:
            output.squeeze(0)

        output = Variable(output, requires_grad=False)

        return output