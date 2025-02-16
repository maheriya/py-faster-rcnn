#!/usr/bin/env python

# --------------------------------------------------------
# Faster R-CNN
# Copyright (c) 2015 Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Written by Ross Girshick
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.
"""

import _init_paths
from fast_rcnn.config import cfg, cfg_from_file, cfg_from_list, get_output_dir
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
from utils.timer import Timer
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
import caffe, os, sys, cv2
import argparse
from pprint import pprint 

cfgfile = 'experiments/cfgs/faster_rcnn_end2end_dvia.yml'
CLASSES = ('__background__',
           'stair', 'curb', 'doorframe')

NETS = {'vgg16': ('VGG16', 'VGG16_faster_rcnn_final_dvia.caffemodel'),
        'zf': ('ZF', 'ZF_faster_rcnn_final_dvia.caffemodel'),
        'dvia': ('DVIANET', 'DVIANET_faster_rcnn_DVIADetDB_450000iter.caffemodel')
        }
def vis_detections(im, class_name, dets, thresh=0.5):
    """Draw detected bounding boxes."""
    inds = np.where(dets[:, -1] >= thresh)[0]
    if len(inds) == 0:
        return

    im = im[:, :, (2, 1, 0)]
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.imshow(im, aspect='equal')
    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]

        ax.add_patch(
            plt.Rectangle((bbox[0], bbox[1]),
                          bbox[2] - bbox[0],
                          bbox[3] - bbox[1], fill=False,
                          edgecolor='red', linewidth=3.5)
            )
        ax.text(bbox[0], bbox[1] - 2,
                '{:s} {:.3f}'.format(class_name, score),
                bbox=dict(facecolor='blue', alpha=0.5),
                fontsize=14, color='white')

    ax.set_title(('{} detections with '
                  'p({} | box) >= {:.1f}').format(class_name, class_name,
                                                  thresh),
                  fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.draw()

def demo(net, image_name):
    """Detect object classes in an image using pre-computed object proposals."""

    # Load the demo image
    im_file = os.path.join(cfg.DATA_DIR, 'demo', image_name)
    im = cv2.imread(im_file)

    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(net, im)
    timer.toc()
    print ('Detection took {:.3f}s for '
           '{:d} object proposals').format(timer.total_time, boxes.shape[0])

    # Visualize detections for each class
    CONF_THRESH = 0.64
    NMS_THRESH = 0.3
    for cls_ind, cls in enumerate(CLASSES[1:]):
        cls_ind += 1 # because we skipped background
        cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]
        vis_detections(im, cls, dets, thresh=CONF_THRESH)

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Faster R-CNN demo')
    parser.add_argument('--gpu', dest='gpu_id', help='GPU device id to use [0]',
                        default=0, type=int)
    parser.add_argument('--cpu', dest='cpu_mode',
                        help='Use CPU mode (overrides --gpu)',
                        action='store_true')
    parser.add_argument('--net', dest='demo_net', help='Network to use [zf]',
                        choices=NETS.keys(), default='dvia')

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    cfg_from_file(cfgfile)
    cfg.TEST.HAS_RPN = True  # Use RPN for proposals
    #pprint(cfg)

    args = parse_args()

    print 'MODELS_DIR: {}'.format(cfg.MODELS_DIR)
    
    prototxt = os.path.join(os.path.realpath(cfg.MODELS_DIR), NETS[args.demo_net][0],
                            'faster_rcnn_end2end', 'test.prototxt')

    caffemodel = os.path.join(cfg.DATA_DIR, 'faster_rcnn_models', NETS[args.demo_net][1])
    #caffemodel = os.path.realpath('output/faster_rcnn_end2end_dvia/train/dvianet_faster_rcnn_iter_50000.caffemodel')


    print 'caffemodel: {}'.format(caffemodel)
    print 'prototxt: {}'.format(prototxt)

    if not os.path.isfile(caffemodel):
        raise IOError(('{:s} not found.\nDid you run ./data/script/'
                       'fetch_faster_rcnn_models_dvia.sh?').format(caffemodel))

    if args.cpu_mode:
        caffe.set_mode_cpu()
    else:
        caffe.set_mode_gpu()
        caffe.set_device(args.gpu_id)
        cfg.GPU_ID = args.gpu_id
    net = caffe.Net(prototxt, caffemodel, caffe.TEST)

    print '\n\nLoaded network {:s}'.format(caffemodel)

    # Warmup on a dummy image
    im = 128 * np.ones((300, 500, 3), dtype=np.uint8)
    for i in xrange(2):
        _, _= im_detect(net, im)

    #im_names = ['3_doorframe_00010_00_BASE_IMAGE.png', '00002_00_BASE_IMAGE.png', '000456.jpg', '000542.jpg', '001150.jpg',
    #            '001763.jpg', '004545.jpg']
    im_names = ['1_stair_001.jpg', '1_stair_002.png', '2_curb_001.jpg', '2_curb_002.jpg',
                '3_doorframe_001.jpg', '3_doorframe_002.png', '00120_00_BASE_IMAGE.png', 'mono_imgl_3.png']
#    im_names = ['mono_imgl_3.png', 'mono_imgl_4.png', 'mono_imgl_5.png', 'mono_imgr_2.png', 'mono_imgr_0.png', 'mono_imgr_1.png', 'multi_det_00178_00_BASE_IMAGE.png']
    for im_name in im_names:
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Demo for data/demo/{}'.format(im_name)
        demo(net, im_name)

    plt.show()
