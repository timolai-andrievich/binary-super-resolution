import math

import torch
import torch.nn as nn

from competition.libs.binarizers import Binarizer
from competition.libs.binary_modules import BinaryConv2d
from competition.libs.sign_approximators import ParabolaSignApproximator, STESignApproximator, STEWithClipSignApproximator
from competition.libs.transformations import L1Scaling


class EConv(nn.Module):
    def __init__(self, channels, mlp_hidden_layer=None):
        super().__init__()
        self.channels = channels
        self.mlp_hidden_layer = mlp_hidden_layer if mlp_hidden_layer is not None else channels * 2
        self.spatial_rescale = nn.Sequential(
            nn.Conv2d(self.channels, 1, 1),  # 1x1 convolution
            nn.Sigmoid(),
        )
        self.channel_wise_shift_and_rescale = nn.Sequential(
            # Described as Global Average Pooling label in the paper
            nn.AdaptiveAvgPool2d((1, 1)),
            # 1x1 convolution, equivalent to linear layers
            nn.Conv2d(self.channels, self.mlp_hidden_layer, 1),
            nn.ReLU(),
            nn.Conv2d(self.mlp_hidden_layer, self.channels * 2, 1),
        )
        input_binarizer = Binarizer(
            sign_approximator=ParabolaSignApproximator(),
        )
        weight_binarizer = Binarizer(
            sign_approximator=STEWithClipSignApproximator(),
            transformation=L1Scaling(dim=[1, 2, 3]),
            channel_wise=True,
        )
        self.conv = BinaryConv2d(input_binarizer, weight_binarizer, in_channels=channels,
                                 out_channels=channels, kernel_size=3, stride=1, padding=1)

    def forward(self, x):
        shortcut = x
        spatial_scale = self.spatial_rescale(x)
        channels_shift_scale_logits = self.channel_wise_shift_and_rescale(x)
        channels_shift, channels_scale_logits = torch.split(channels_shift_scale_logits, self.channels, dim=1)
        channels_scale = torch.sigmoid(channels_scale_logits)
        x = x + channels_shift 
        x = self.conv(x)
        x = x * spatial_scale 
        x = x * channels_scale
        x = x + shortcut
        return x

class BasicBlock(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        self.conv1 = EConv(channels)
        self.act = nn.LeakyReLU()
        self.conv2 = EConv(channels)
    
    def forward(self, x):
        x = self.conv1(x)
        x = self.act(x)
        x = self.conv2(x)
        return x
        

class MeanShift(nn.Module):
    def __init__(self, rgb_range=255, rgb_mean=(0.4488, 0.4371, 0.4040), sign=-1):
        super(MeanShift, self).__init__()
        mean_shift = sign * rgb_range * torch.Tensor(rgb_mean)
        self.register_buffer("mean_shift", mean_shift.view(1, 3, 1, 1))

    def forward(self, x):
        return x + self.mean_shift


class Upsampler(nn.Sequential):
    def __init__(self, scale, n_features):
        modules = []
        if (scale & (scale - 1)) == 0:  # check if scale == 2^n
            for _ in range(int(math.log(scale, 2))):
                modules.append(nn.Conv2d(n_features, 4 * n_features,
                               kernel_size=3, padding=1, bias=True))
                modules.append(nn.PixelShuffle(2))
        else:
            raise NotImplementedError

        super(Upsampler, self).__init__(*modules)


class BinaryScalex2EBSR(nn.Module):
    """
    Model architecture is based on the EBSR model.
    """

    def __init__(self, in_channels=3, out_channels=3, feature_channels=64, n_residual_blocks=8, scale=2, **kwargs):
        super().__init__(**kwargs)

        # define head modules
        modules_head = [
            nn.Conv2d(in_channels, feature_channels, kernel_size=3, padding=1, bias=True)]

        # define body modules
        modules_body = [BasicBlock(feature_channels)
                        for _ in range(n_residual_blocks)]
        modules_body.append(nn.Conv2d(
            feature_channels, feature_channels, kernel_size=3, padding=1, bias=True))

        # define tail modules
        modules_tail = [
            Upsampler(scale, feature_channels),
            nn.Conv2d(feature_channels, out_channels,
                      kernel_size=3, padding=1, bias=True),
        ]

        self.sub_mean = MeanShift(sign=-1)
        self.add_mean = MeanShift(sign=1)
        self.head = nn.Sequential(*modules_head)
        self.body = nn.Sequential(*modules_body)
        self.tail = nn.Sequential(*modules_tail)

    def forward(self, x):
        x = self.sub_mean(x)
        x = self.head(x)
        x = x + self.body(x)
        x = self.tail(x)
        x = self.add_mean(x)

        return x
