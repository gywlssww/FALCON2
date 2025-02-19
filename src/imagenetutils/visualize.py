'''
The following codes are from https://github.com/d-li14/mobilenetv2.pytorch
'''

# pylint: disable=W0401,C0103,E1101,C0200,E0402,E0602
import matplotlib.pyplot as plt
import torch
import torchvision
import numpy as np
from .misc import *

__all__ = ['make_image', 'show_batch', 'show_mask', 'show_mask_single']

# functions to show an image
def make_image(img, mean=(0,0,0), std=(1,1,1)):
    """
    image generation function
    
    :param img: target image
    :param mean: mean value of the image
    :param std: standard deviation of the image
    :return: np.transpose(npimg, (1, 2, 0)): unnormalized image
    """
    for i in range(0, 3):
        img[i] = img[i] * std[i] + mean[i]    # unnormalize
    npimg = img.numpy()
    return np.transpose(npimg, (1, 2, 0))

def gauss(x,a,b,c):
    """
    gauss function
    refer to https://en.wikipedia.org/wiki/Gaussian_function
    
    return torch.exp(-torch.pow(torch.add(x,-b),2).div(2*c*c)).mul(a): normalized value
    """
    return torch.exp(-torch.pow(torch.add(x,-b),2).div(2*c*c)).mul(a)

def colorize(x):
    ''' 
    Converts a one-channel grayscale image to a color heatmap image 
    
    :param x: image
    :return: cl: color heatmap image
    '''
    if x.dim() == 2:
        torch.unsqueeze(x, 0, out=x)
    if x.dim() == 3:
        cl = torch.zeros([3, x.size(1), x.size(2)])
        cl[0] = gauss(x,.5,.6,.2) + gauss(x,1,.8,.3)
        cl[1] = gauss(x,1,.5,.3)
        cl[2] = gauss(x,1,.2,.3)
        cl[cl.gt(1)] = 1
    elif x.dim() == 4:
        cl = torch.zeros([x.size(0), 3, x.size(2), x.size(3)])
        cl[:,0,:,:] = gauss(x,.5,.6,.2) + gauss(x,1,.8,.3)
        cl[:,1,:,:] = gauss(x,1,.5,.3)
        cl[:,2,:,:] = gauss(x,1,.2,.3)
    return cl

def show_batch(images, Mean=(2, 2, 2), Std=(0.5,0.5,0.5)):
    """
    batch images showing function
    
    :param images: batch images
    :param Mean: mean value of the image
    :param Std: standard deviation of the image
    """
    images = make_image(torchvision.utils.make_grid(images), Mean, Std)
    plt.imshow(images)
    plt.show()


def show_mask_single(images, mask, Mean=(2, 2, 2), Std=(0.5,0.5,0.5)):
    """
    batch images with mask showing function
    
    :param images: batch images
    :param mask: mask
    :param Mean: mean value of the image
    :param Std: standard deviation of the image
    """
    im_size = images.size(2)

    # save for adding mask
    im_data = images.clone()
    for i in range(0, 3):
        im_data[:,i,:,:] = im_data[:,i,:,:] * Std[i] + Mean[i]    # unnormalize

    images = make_image(torchvision.utils.make_grid(images), Mean, Std)
    plt.subplot(2, 1, 1)
    plt.imshow(images)
    plt.axis('off')

    mask_size = mask.size(2)
    mask = (upsampling(mask, scale_factor=im_size/mask_size))

    mask = make_image(torchvision.utils.make_grid(0.3*im_data+0.7*mask.expand_as(im_data)))
    plt.subplot(2, 1, 2)
    plt.imshow(mask)
    plt.axis('off')

def show_mask(images, masklist, Mean=(2, 2, 2), Std=(0.5,0.5,0.5)):
    """
    mask showing function
    
    :param images: batch images
    :param masklist: target masks
    :param Mean: mean value of the image
    :param Std: standard deviation of the image
    """
    im_size = images.size(2)

    # save for adding mask
    im_data = images.clone()
    for i in range(0, 3):
        im_data[:,i,:,:] = im_data[:,i,:,:] * Std[i] + Mean[i]    # unnormalize

    images = make_image(torchvision.utils.make_grid(images), Mean, Std)
    plt.subplot(1+len(masklist), 1, 1)
    plt.imshow(images)
    plt.axis('off')

    for i in range(len(masklist)):
        mask = masklist[i].data.cpu()
        # for b in range(mask.size(0)):
        #     mask[b] = (mask[b] - mask[b].min())/(mask[b].max() - mask[b].min())
        mask_size = mask.size(2)
        # print('Max %f Min %f' % (mask.max(), mask.min()))
        mask = (upsampling(mask, scale_factor=im_size/mask_size))
        # mask = colorize(upsampling(mask, scale_factor=im_size/mask_size))
        # for c in range(3):
        #     mask[:,c,:,:] = (mask[:,c,:,:] - Mean[c])/Std[c]

        # print(mask.size())
        mask = make_image(torchvision.utils.make_grid(0.3*im_data+0.7*mask.expand_as(im_data)))
        # mask = make_image(torchvision.utils.make_grid(0.3*im_data+0.7*mask), Mean, Std)
        plt.subplot(1+len(masklist), 1, i+2)
        plt.imshow(mask)
        plt.axis('off')



# x = torch.zeros(1, 3, 3)
# out = colorize(x)
# out_im = make_image(out)
# plt.imshow(out_im)
# plt.show()
