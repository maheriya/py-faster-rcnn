dvia_train.prototxt is the base custom DVIANET network that was tested with Cifar data for classification. It is now integrated with Faster RCNN as train.prototxt and test.prototxt

Current version gives following result:
AP for stair = 0.4373
AP for curb = 0.1031
AP for doorframe = 0.4198
Mean AP = 0.3201

Input image size = 150min x 250max [autoscaled by Python layer from 300min x 500max]
