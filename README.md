# Binary model for the Binary Super-Resolution Challenge, 2023

[Competition website](http://cscontest.ru/bsrc/)

## Description

### Models

The EBSR model (binary_scalex2_ebsr.py) is based on the [EBSR: Enhanced Binary Neural Network for Image Super-Resolution](https://arxiv.org/abs/2303.12270) paper.

## How to run

 1. Download Div2K, Set5, Set14, B100, Urban100 datasets.
 2. Edit `competition/dataloaders/datasets_info.py` to point to the location of the datasets.
 3. Install required python modules. One of the ways to do it is to run `python -m pip install -r requirements.txt`.
 4. Run `python main.py --config competition/config_files/scalex2_ebsr.yaml --logdir results/scalex2_ebsr --gpu=0`
 5. The model weights, as well as tensorboard logs will be saved into the specified log directory.

## Acknowledgements

This repository heavily uses [code](https://github.com/ilyazhara/BSRC-2023) provided as a baseline by the competition organizers to train the model.
