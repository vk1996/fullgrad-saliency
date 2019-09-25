#
# Copyright (c) 2019 Idiap Research Institute, http://www.idiap.ch/
# Written by Suraj Srinivas <suraj.srinivas@idiap.ch>
#

""" Compute saliency maps of images from dataset folder 
    and dump them in a results folder """

import torch
import subprocess
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms, utils, models
import numpy as np
import os

from fullgrad import FullGrad
from vgg_imagenet import *
from misc_functions import *

# PATH variables
PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
dataset = PATH + 'dataset/'

batch_size = 1

cuda = torch.cuda.is_available()
device = torch.device("cuda" if cuda else "cpu")

# Dataset loader for sample images
sample_loader = torch.utils.data.DataLoader(
    datasets.ImageFolder(dataset, transform=transforms.Compose([
                       transforms.Resize((224,224)),
                       transforms.ToTensor(),
                       transforms.Normalize(mean = [0.485, 0.456, 0.406],
                                        std = [0.229, 0.224, 0.225])
                   ])),
    batch_size= batch_size, shuffle=False)

unnormalize = NormalizeInverse(mean = [0.485, 0.456, 0.406],
                           std = [0.229, 0.224, 0.225])


model = vgg16_bn(pretrained=True)

# Initialize FullGrad object
fullgrad = FullGrad(model)

save_path = PATH + 'results/'

def compute_saliency_and_save():
    for batch_idx, (data, target) in enumerate(sample_loader):
        data, target = data.to(device).requires_grad_(), target.to(device)

        # Compute saliency maps for the input data
        cam = fullgrad.saliency(data)

        # Save saliency maps
        for i in range(data.size(0)):
            filename = save_path + str( (batch_idx+1) * (i+1)) + '.jpg'

            image = unnormalize(data[i,:,:,:].cpu())
            save_saliency_map(image, cam[i,:,:,:], filename)


#---------------------------------------------------------------------------------#

create_folder(save_path)
compute_saliency_and_save()

#---------------------------------------------------------------------------------#
        
        




