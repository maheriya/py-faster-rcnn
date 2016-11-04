Input image size: 150x250

ROIPooling output:
6x6

1. For ZF network:
Output of final layer of the feature extractor portion of the network (conv5):
10x17

Ratio: 150/10 = 15, 250/17=14.70

In other words, each pixel in 10x17 represents roughly 16 pixels in input image.
This is the 'spatial_scale' parameter of the ROIPooling layer (1/16 = 0.0625)



2. For DVIANET network:
Output of final layer of the feature extractor portion of the network (conv3):
??

spatial_scale = ??
