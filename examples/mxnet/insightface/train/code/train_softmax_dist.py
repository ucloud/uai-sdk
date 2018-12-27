from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import math
import random
import logging
import pickle
import numpy as np
from image_iter import FaceImageIter
from image_iter import FaceImageIterList
import mxnet as mx
from mxnet import ndarray as nd
import argparse
import mxnet.optimizer as optimizer
sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
import face_image
sys.path.append(os.path.join(os.path.dirname(__file__), 'eval'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'symbols'))
import fresnet
import finception_resnet_v2
import fmobilenet 
import fmobilenetv2
import fmobilefacenet
import fxception
import fdensenet
import fdpn
import fnasnet
import spherenet
import verification
import sklearn
#sys.path.append(os.path.join(os.path.dirname(__file__), 'losses'))
#import center_loss

logger = logging.getLogger()
logger.setLevel(logging.INFO)

args = None

class AccMetric(mx.metric.EvalMetric):
  def __init__(self):
    self.axis = 1
    super(AccMetric, self).__init__(
        'acc', axis=self.axis,
        output_names=None, label_names=None)
    self.losses = []
    self.count = 0

  def update(self, labels, preds):
    self.count+=1
    label = labels[0]
    pred_label = preds[1]
    if pred_label.shape != label.shape:
        pred_label = mx.ndarray.argmax(pred_label, axis=self.axis)
    pred_label = pred_label.asnumpy().astype('int32').flatten()
    label = label.asnumpy()
    if label.ndim==2:
      label = label[:,0]
    label = label.astype('int32').flatten()
    assert label.shape==pred_label.shape
    self.sum_metric += (pred_label.flat == label.flat).sum()
    self.num_inst += len(pred_label.flat)

class LossValueMetric(mx.metric.EvalMetric):
  def __init__(self):
    self.axis = 1
    super(LossValueMetric, self).__init__(
        'lossvalue', axis=self.axis,
        output_names=None, label_names=None)
    self.losses = []

  def update(self, labels, preds):
    loss = preds[-1].asnumpy()[0]
    self.sum_metric += loss
    self.num_inst += 1.0
    gt_label = preds[-2].asnumpy()
    #print(gt_label)

def parse_args():
  parser = argparse.ArgumentParser(description='Train face network')

  # UAI Related
  parser.add_argument('--work_dir', type=str, default="/data", help='Default work path')
  parser.add_argument('--output_dir', type=str, default="/data/output", help="Default output path")
  parser.add_argument('--log_dir', type=str, default="/data/output", help="Default log path")
  parser.add_argument('--num_gpus', type=int, help="Num of avaliable gpus")
  parser.add_argument('--data_dir', default='/data/data/', help='training set directory')
  
  # Dist Train
  parser.add_argument('--kv-store', type=str, default='device', help='key-value store type')
  parser.add_argument('--gc-type', type=str, default='none',
                       help='type of gradient compression to use, takes `2bit` or `none` for now')
  parser.add_argument('--optimizer', type=str, default='sgd', help='the optimizer type')
   
  # general
  parser.add_argument('--prefix', default='../model/model', help='directory to save model.')
  parser.add_argument('--pretrained', default='', help='pretrained model to load')
  parser.add_argument('--ckpt', type=int, default=1, help='checkpoint saving option. 0: discard saving. 1: save when necessary. 2: always save')
  parser.add_argument('--loss-type', type=int, default=4, help='loss type')
  parser.add_argument('--verbose', type=int, default=2000, help='do verification testing every verbose batches')
  parser.add_argument('--max-steps', type=int, default=0, help='max training batches')
  parser.add_argument('--end-epoch', type=int, default=100000, help='training epoch size.')
  parser.add_argument('--network', default='r50', help='specify network')
  parser.add_argument('--image-size', default='112,112', help='specify input image height and width')
  parser.add_argument('--version-se', type=int, default=0, help='whether to use se in network')
  parser.add_argument('--version-input', type=int, default=1, help='network input config')
  parser.add_argument('--version-output', type=str, default='E', help='network embedding output config')
  parser.add_argument('--version-unit', type=int, default=3, help='resnet unit config')
  parser.add_argument('--version-multiplier', type=float, default=1.0, help='filters multiplier')
  parser.add_argument('--version-act', type=str, default='prelu', help='network activation config')
  parser.add_argument('--use-deformable', type=int, default=0, help='use deformable cnn in network')
  parser.add_argument('--lr', type=float, default=0.1, help='start learning rate')
  parser.add_argument('--lr-steps', type=str, default='', help='steps of lr changing')
  parser.add_argument('--wd', type=float, default=0.0005, help='weight decay')
  parser.add_argument('--fc7-wd-mult', type=float, default=1.0, help='weight decay mult for fc7')
  parser.add_argument('--fc7-lr-mult', type=float, default=1.0, help='lr mult for fc7')
  parser.add_argument("--fc7-no-bias", default=False, action="store_true" , help="fc7 no bias flag")
  parser.add_argument('--bn-mom', type=float, default=0.9, help='bn mom')
  parser.add_argument('--mom', type=float, default=0.9, help='momentum')
  parser.add_argument('--emb-size', type=int, default=512, help='embedding length')
  parser.add_argument('--per-batch-size', type=int, default=128, help='batch size in each context')
  parser.add_argument('--margin-m', type=float, default=0.5, help='margin for loss')
  parser.add_argument('--margin-s', type=float, default=64.0, help='scale for feature')
  parser.add_argument('--margin-a', type=float, default=1.0, help='')
  parser.add_argument('--margin-b', type=float, default=0.0, help='')
  parser.add_argument('--easy-margin', type=int, default=0, help='')
  parser.add_argument('--margin', type=int, default=4, help='margin for sphere')
  parser.add_argument('--beta', type=float, default=1000., help='param for sphere')
  parser.add_argument('--beta-min', type=float, default=5., help='param for sphere')
  parser.add_argument('--power', type=float, default=1.0, help='param for sphere')
  parser.add_argument('--scale', type=float, default=0.9993, help='param for sphere')
  parser.add_argument('--rand-mirror', type=int, default=1, help='if do random mirror in training')
  parser.add_argument('--cutoff', type=int, default=0, help='cut off aug')
  parser.add_argument('--color', type=int, default=0, help='color jittering aug')
  parser.add_argument('--images-filter', type=int, default=0, help='minimum images per identity filter')
  parser.add_argument('--target', type=str, default='lfw,cfp_fp,agedb_30', help='verification targets')
  parser.add_argument('--ce-loss', default=False, action='store_true', help='if output ce loss')
  args = parser.parse_args()
  return args

def get_symbol(args, arg_params, aux_params):
  data_shape = (args.image_channel,args.image_h,args.image_w)
  image_shape = ",".join([str(x) for x in data_shape])
  margin_symbols = []
  if args.network[0]=='d':
    embedding = fdensenet.get_symbol(args.emb_size, args.num_layers,
        version_se=args.version_se, version_input=args.version_input, 
        version_output=args.version_output, version_unit=args.version_unit)
  elif args.network[0]=='m':
    print('init mobilenet', args.num_layers)
    if args.num_layers==1:
      embedding = fmobilenet.get_symbol(args.emb_size, 
          version_input=args.version_input, 
          version_output=args.version_output,
          version_multiplier = args.version_multiplier)
    else:
      embedding = fmobilenetv2.get_symbol(args.emb_size)
  elif args.network[0]=='i':
    print('init inception-resnet-v2', args.num_layers)
    embedding = finception_resnet_v2.get_symbol(args.emb_size,
        version_se=args.version_se, version_input=args.version_input, 
        version_output=args.version_output, version_unit=args.version_unit)
  elif args.network[0]=='x':
    print('init xception', args.num_layers)
    embedding = fxception.get_symbol(args.emb_size,
        version_se=args.version_se, version_input=args.version_input, 
        version_output=args.version_output, version_unit=args.version_unit)
  elif args.network[0]=='p':
    print('init dpn', args.num_layers)
    embedding = fdpn.get_symbol(args.emb_size, args.num_layers,
        version_se=args.version_se, version_input=args.version_input, 
        version_output=args.version_output, version_unit=args.version_unit)
  elif args.network[0]=='n':
    print('init nasnet', args.num_layers)
    embedding = fnasnet.get_symbol(args.emb_size)
  elif args.network[0]=='s':
    print('init spherenet', args.num_layers)
    embedding = spherenet.get_symbol(args.emb_size, args.num_layers)
  elif args.network[0]=='y':
    print('init mobilefacenet', args.num_layers)
    embedding = fmobilefacenet.get_symbol(args.emb_size, bn_mom = args.bn_mom, version_output=args.version_output)
  else:
    print('init resnet', args.num_layers)
    embedding = fresnet.get_symbol(args.emb_size, args.num_layers, 
        version_se=args.version_se, version_input=args.version_input, 
        version_output=args.version_output, version_unit=args.version_unit,
        version_act=args.version_act)
  all_label = mx.symbol.Variable('softmax_label')
  gt_label = all_label
  extra_loss = None
  _weight = mx.symbol.Variable("fc7_weight", shape=(args.num_classes, args.emb_size), lr_mult=args.fc7_lr_mult, wd_mult=args.fc7_wd_mult)
  if args.loss_type==0: #softmax
    if args.fc7_no_bias:
      fc7 = mx.sym.FullyConnected(data=embedding, weight = _weight, no_bias = True, num_hidden=args.num_classes, name='fc7')
    else:
      _bias = mx.symbol.Variable('fc7_bias', lr_mult=2.0, wd_mult=0.0)
      fc7 = mx.sym.FullyConnected(data=embedding, weight = _weight, bias = _bias, num_hidden=args.num_classes, name='fc7')
  elif args.loss_type==1: #sphere not suitable for dist training, exit
    sys.exit(-1)
    '''
    _weight = mx.symbol.L2Normalization(_weight, mode='instance')
    fc7 = mx.sym.LSoftmax(data=embedding, label=gt_label, num_hidden=args.num_classes,
                          weight = _weight,
                          beta=args.beta, margin=args.margin, scale=args.scale,
                          beta_min=args.beta_min, verbose=1000, name='fc7')
    '''
  elif args.loss_type==2: # CosineFace
    s = args.margin_s
    m = args.margin_m
    assert(s>0.0)
    assert(m>0.0)
    _weight = mx.symbol.L2Normalization(_weight, mode='instance')
    nembedding = mx.symbol.L2Normalization(embedding, mode='instance', name='fc1n')*s
    fc7 = mx.sym.FullyConnected(data=nembedding, weight = _weight, no_bias = True, num_hidden=args.num_classes, name='fc7')
    s_m = s*m
    gt_one_hot = mx.sym.one_hot(gt_label, depth = args.num_classes, on_value = s_m, off_value = 0.0)
    fc7 = fc7-gt_one_hot
  elif args.loss_type==4: # ArcFace
    s = args.margin_s
    m = args.margin_m
    assert s>0.0
    assert m>=0.0
    assert m<(math.pi/2)
    _weight = mx.symbol.L2Normalization(_weight, mode='instance') # L2Norm(w) ||w|| = 1
    nembedding = mx.symbol.L2Normalization(embedding, mode='instance', name='fc1n')*s # L2Norm(embedding) ||embedding|| = 1
    fc7 = mx.sym.FullyConnected(data=nembedding, weight = _weight, no_bias = True, num_hidden=args.num_classes, name='fc7')
    zy = mx.sym.pick(fc7, gt_label, axis=1)
    cos_t = zy/s
    cos_m = math.cos(m)
    sin_m = math.sin(m)
    mm = math.sin(math.pi-m)*m
    #threshold = 0.0
    threshold = math.cos(math.pi-m)
    if args.easy_margin:
      cond = mx.symbol.Activation(data=cos_t, act_type='relu')
    else:
      cond_v = cos_t - threshold
      cond = mx.symbol.Activation(data=cond_v, act_type='relu')
    body = cos_t*cos_t
    body = 1.0-body
    sin_t = mx.sym.sqrt(body)
    new_zy = cos_t*cos_m
    b = sin_t*sin_m
    new_zy = new_zy - b
    new_zy = new_zy*s
    if args.easy_margin:
      zy_keep = zy
    else:
      zy_keep = zy - s*mm
    new_zy = mx.sym.where(cond, new_zy, zy_keep)

    diff = new_zy - zy
    diff = mx.sym.expand_dims(diff, 1)
    gt_one_hot = mx.sym.one_hot(gt_label, depth = args.num_classes, on_value = 1.0, off_value = 0.0)
    body = mx.sym.broadcast_mul(gt_one_hot, diff)
    fc7 = fc7+body
  elif args.loss_type==5: # Combined Margin
    s = args.margin_s
    m = args.margin_m
    assert s>0.0
    _weight = mx.symbol.L2Normalization(_weight, mode='instance')
    nembedding = mx.symbol.L2Normalization(embedding, mode='instance', name='fc1n')*s
    fc7 = mx.sym.FullyConnected(data=nembedding, weight = _weight, no_bias = True, num_hidden=args.num_classes, name='fc7')
    if args.margin_a!=1.0 or args.margin_m!=0.0 or args.margin_b!=0.0:
      if args.margin_a==1.0 and args.margin_m==0.0:
        s_m = s*args.margin_b
        gt_one_hot = mx.sym.one_hot(gt_label, depth = args.num_classes, on_value = s_m, off_value = 0.0)
        fc7 = fc7-gt_one_hot
      else:
        zy = mx.sym.pick(fc7, gt_label, axis=1)
        cos_t = zy/s
        t = mx.sym.arccos(cos_t)
        if args.margin_a!=1.0:
          t = t*args.margin_a
        if args.margin_m>0.0:
          t = t+args.margin_m
        body = mx.sym.cos(t)
        if args.margin_b>0.0:
          body = body - args.margin_b
        new_zy = body*s
        diff = new_zy - zy
        diff = mx.sym.expand_dims(diff, 1)
        gt_one_hot = mx.sym.one_hot(gt_label, depth = args.num_classes, on_value = 1.0, off_value = 0.0)
        body = mx.sym.broadcast_mul(gt_one_hot, diff)
        fc7 = fc7+body
  elif args.loss_type==6:
    s = args.margin_s
    m = args.margin_m
    assert s>0.0
    assert args.margin_b>0.0
    _weight = mx.symbol.L2Normalization(_weight, mode='instance')
    nembedding = mx.symbol.L2Normalization(embedding, mode='instance', name='fc1n')*s
    fc7 = mx.sym.FullyConnected(data=nembedding, weight = _weight, no_bias = True, num_hidden=args.num_classes, name='fc7')
    zy = mx.sym.pick(fc7, gt_label, axis=1)
    cos_t = zy/s
    t = mx.sym.arccos(cos_t)
    intra_loss = t/np.pi
    intra_loss = mx.sym.mean(intra_loss)
    #intra_loss = mx.sym.exp(cos_t*-1.0)
    intra_loss = mx.sym.MakeLoss(intra_loss, name='intra_loss', grad_scale = args.margin_b)
    if m>0.0:
      t = t+m
      body = mx.sym.cos(t)
      new_zy = body*s
      diff = new_zy - zy
      diff = mx.sym.expand_dims(diff, 1)
      gt_one_hot = mx.sym.one_hot(gt_label, depth = args.num_classes, on_value = 1.0, off_value = 0.0)
      body = mx.sym.broadcast_mul(gt_one_hot, diff)
      fc7 = fc7+body
  elif args.loss_type==7:
    s = args.margin_s
    m = args.margin_m
    assert s>0.0
    assert args.margin_b>0.0
    assert args.margin_a>0.0
    _weight = mx.symbol.L2Normalization(_weight, mode='instance')
    nembedding = mx.symbol.L2Normalization(embedding, mode='instance', name='fc1n')*s
    fc7 = mx.sym.FullyConnected(data=nembedding, weight = _weight, no_bias = True, num_hidden=args.num_classes, name='fc7')
    zy = mx.sym.pick(fc7, gt_label, axis=1)
    cos_t = zy/s
    t = mx.sym.arccos(cos_t)

    #counter_weight = mx.sym.take(_weight, gt_label, axis=1)
    #counter_cos = mx.sym.dot(counter_weight, _weight, transpose_a=True)
    counter_weight = mx.sym.take(_weight, gt_label, axis=0)
    counter_cos = mx.sym.dot(counter_weight, _weight, transpose_b=True)
    #counter_cos = mx.sym.minimum(counter_cos, 1.0)
    #counter_angle = mx.sym.arccos(counter_cos)
    #counter_angle = counter_angle * -1.0
    #counter_angle = counter_angle/np.pi #[0,1]
    #inter_loss = mx.sym.exp(counter_angle)

    #counter_cos = mx.sym.dot(_weight, _weight, transpose_b=True)
    #counter_cos = mx.sym.minimum(counter_cos, 1.0)
    #counter_angle = mx.sym.arccos(counter_cos)
    #counter_angle = mx.sym.sort(counter_angle, axis=1)
    #counter_angle = mx.sym.slice_axis(counter_angle, axis=1, begin=0,end=int(args.margin_a))

    #inter_loss = counter_angle*-1.0 # [-1,0]
    #inter_loss = inter_loss+1.0 # [0,1]
    inter_loss = counter_cos
    inter_loss = mx.sym.mean(inter_loss)
    inter_loss = mx.sym.MakeLoss(inter_loss, name='inter_loss', grad_scale = args.margin_b)
    if m>0.0:
      t = t+m
      body = mx.sym.cos(t)
      new_zy = body*s
      diff = new_zy - zy
      diff = mx.sym.expand_dims(diff, 1)
      gt_one_hot = mx.sym.one_hot(gt_label, depth = args.num_classes, on_value = 1.0, off_value = 0.0)
      body = mx.sym.broadcast_mul(gt_one_hot, diff)
      fc7 = fc7+body

  out_list = [mx.symbol.BlockGrad(embedding)]
  softmax = mx.symbol.SoftmaxOutput(data=fc7, label = gt_label, name='softmax', normalization='valid')
  out_list.append(softmax)
  if args.loss_type==6:
    out_list.append(intra_loss)
  if args.loss_type==7:
    out_list.append(inter_loss)
    #out_list.append(mx.sym.BlockGrad(counter_weight))
    #out_list.append(intra_loss)
  if args.ce_loss:
    #ce_loss = mx.symbol.softmax_cross_entropy(data=fc7, label = gt_label, name='ce_loss')/args.per_batch_size
    body = mx.symbol.SoftmaxActivation(data=fc7)
    body = mx.symbol.log(body)
    _label = mx.sym.one_hot(gt_label, depth = args.num_classes, on_value = -1.0, off_value = 0.0)
    body = body*_label
    ce_loss = mx.symbol.sum(body)/args.per_batch_size
    out_list.append(mx.symbol.BlockGrad(ce_loss))
  out = mx.symbol.Group(out_list)
  return (out, arg_params, aux_params)

# lr scheduler for dist training
def _get_lr_scheduler(args, kv, begin_epoch, num_samples):
  lr = args.lr
  if len(args.lr_steps)==0:
    lr_steps = [40000, 60000, 80000]
    if args.loss_type>=1 and args.loss_type<=7:
      lr_steps = [100000, 140000, 160000]
    p = 512.0/(args.batch_size * kv.num_workers)
    for l in xrange(len(lr_steps)):
      lr_steps[l] = int(lr_steps[l]*p)
  else:
    lr_steps = [int(x) for x in args.lr_steps.split(',')]
  print('lr_steps', lr_steps)

  begin_step = begin_epoch * num_samples
  for s in lr_steps:
    if begin_step >= s:
      lr *= 0.1
  if lr != args.lr:
    logging.info('Adjust learning rate to %e for step %d' %(lr, begin_step))
 
  return (lr, mx.lr_scheduler.MultiFactorScheduler(step=lr_steps, factor=0.1))

#save mode on each epoch
def _save_model(args, rank=0):
  if args.prefix is None:
    return None

  #Add UAI output_dir path
  model_prefix = args.prefix
  dst_dir = os.path.dirname(model_prefix)
  if not os.path.isdir(dst_dir):
    os.mkdir(dst_dir)
  return mx.callback.do_checkpoint(model_prefix if rank == 0 else "%s-%d" % (model_prefix, rank))

def train_net(args):
    # Set up kvstore
    kv = mx.kvstore.create(args.kv_store)
    if args.gc_type != 'none':
        kv.set_gradient_compression({'type': args.gc_type,
                                     'threshold': args.gc_threshold})

    # logging
    head = '%(asctime)-15s Node[' + str(kv.rank) + '] %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=head)
    logging.info('start with arguments %s', args)

    # Get ctx according to num_gpus, gpu id start from 0
    ctx = []
    ctx = [mx.cpu()] if args.num_gpus is None or args.num_gpus is 0 else [
        mx.gpu(i) for i in range(args.num_gpus)]

    # model prefix, In UAI Platform, should be /data/output/xxx
    prefix = args.prefix
    prefix_dir = os.path.dirname(prefix)
    if not os.path.exists(prefix_dir):
      os.makedirs(prefix_dir)
    end_epoch = args.end_epoch
    args.ctx_num = len(ctx)
    args.num_layers = int(args.network[1:])
    print('num_layers', args.num_layers)
    if args.per_batch_size==0:
      args.per_batch_size = 128
    args.batch_size = args.per_batch_size*args.ctx_num
    args.rescale_threshold = 0
    args.image_channel = 3

    data_dir_list = args.data_dir.split(',')
    assert len(data_dir_list)==1
    data_dir = data_dir_list[0]
    path_imgrec = None
    path_imglist = None
    prop = face_image.load_property(data_dir)
    args.num_classes = prop.num_classes
    #image_size = prop.image_size
    image_size = [int(x) for x in args.image_size.split(',')]
    assert len(image_size)==2
    assert image_size[0]==image_size[1]
    args.image_h = image_size[0]
    args.image_w = image_size[1]
    print('image_size', image_size)
    assert(args.num_classes>0)
    print('num_classes', args.num_classes)
    path_imgrec = os.path.join(data_dir, "train.rec")
    path_imglist = os.path.join(data_dir, "train.lst")

    num_samples = 0
    for line in open(path_imglist).xreadlines():
      num_samples += 1

    print('Called with argument:', args)
    data_shape = (args.image_channel,image_size[0],image_size[1])
    mean = None

    begin_epoch = 0
    base_lr = args.lr
    base_wd = args.wd
    base_mom = args.mom
    if len(args.pretrained)==0:
      arg_params = None
      aux_params = None
      sym, arg_params, aux_params = get_symbol(args, arg_params, aux_params)
      if args.network[0]=='s':
        data_shape_dict = {'data' : (args.per_batch_size,)+data_shape}
        spherenet.init_weights(sym, data_shape_dict, args.num_layers)
    else:
      # Not the mode is saved each epoch, not NUM of steps as in train_softmax.py
      # args.pretrained be 'prefix,epoch'
      vec = args.pretrained.split(',')
      print('loading', vec)
      model_prefix = vec[0]
      if kv.rank > 0 and os.path.exists("%s-%d-symbol.json" % (model_prefix, kv.rank)):
        model_prefix += "-%d" % (kv.rank)
      logging.info('Loaded model %s_%d.params', model_prefix, int(vec[1]))
      _, arg_params, aux_params = mx.model.load_checkpoint(model_prefix, int(vec[1]))
      begin_epoch = int(vec[1])
      sym, arg_params, aux_params = get_symbol(args, arg_params, aux_params)

    model = mx.mod.Module(
        context       = ctx,
        symbol        = sym,
    )
    val_dataiter = None

    train_dataiter = FaceImageIter(
        batch_size           = args.batch_size,
        data_shape           = data_shape,
        path_imgrec          = path_imgrec,
        shuffle              = True,
        rand_mirror          = args.rand_mirror,
        mean                 = mean,
        cutoff               = args.cutoff,
        color_jittering      = args.color,
        images_filter        = args.images_filter,
    )

    metric1 = AccMetric()
    eval_metrics = [mx.metric.create(metric1)]
    if args.ce_loss:
      metric2 = LossValueMetric()
      eval_metrics.append( mx.metric.create(metric2) )

    if args.network[0]=='r' or args.network[0]=='y':
      initializer = mx.init.Xavier(rnd_type='gaussian', factor_type="out", magnitude=2) #resnet style
    elif args.network[0]=='i' or args.network[0]=='x':
      initializer = mx.init.Xavier(rnd_type='gaussian', factor_type="in", magnitude=2) #inception
    else:
      initializer = mx.init.Xavier(rnd_type='uniform', factor_type="in", magnitude=2)
    #initializer = mx.init.Xavier(rnd_type='gaussian', factor_type="out", magnitude=2) #resnet style
    som = 20
    _cb = mx.callback.Speedometer(args.batch_size, som)

    ver_list = []
    ver_name_list = []
    for name in args.target.split(','):
      path = os.path.join(data_dir,name+".bin")
      if os.path.exists(path):
        data_set = verification.load_bin(path, image_size)
        ver_list.append(data_set)
        ver_name_list.append(name)
        print('ver', name)

    def ver_test(nbatch):
      results = []
      for i in xrange(len(ver_list)):
        acc1, std1, acc2, std2, xnorm, embeddings_list = verification.test(ver_list[i], model, args.batch_size, 10, None, None)
        print('[%s][%d]XNorm: %f' % (ver_name_list[i], nbatch, xnorm))
        #print('[%s][%d]Accuracy: %1.5f+-%1.5f' % (ver_name_list[i], nbatch, acc1, std1))
        print('[%s][%d]Accuracy-Flip: %1.5f+-%1.5f' % (ver_name_list[i], nbatch, acc2, std2))
        results.append(acc2)
      return results

    highest_acc = [0.0, 0.0]  #lfw and target
    #for i in xrange(len(ver_list)):
    #  highest_acc.append(0.0)

    def _batch_callback(param):
      #global global_step
      mbatch = param.nbatch

      _cb(param)
      if mbatch%1000==0:
        print('lr-batch-epoch:',param.nbatch,param.epoch)

      if mbatch>=0 and mbatch%args.verbose==0:
        acc_list = ver_test(mbatch)
        is_highest = False
        if len(acc_list)>0:
          score = sum(acc_list)
          if acc_list[-1]>=highest_acc[-1]:
            if acc_list[-1]>highest_acc[-1]:
              is_highest = True
            else:
              if score>=highest_acc[0]:
                is_highest = True
                highest_acc[0] = score
            highest_acc[-1] = acc_list[-1]
            #if lfw_score>=0.99:
            #  do_save = True

        print('[%d]Accuracy-Highest: %1.5f'%(mbatch, highest_acc[-1]))

    # save model
    checkpoint = _save_model(args, kv.rank)
    epoch_cb = checkpoint

    rescale = 1.0/args.ctx_num
    lr, lr_scheduler = _get_lr_scheduler(args, kv, begin_epoch, num_samples)
    # learning rate
    optimizer_params = {
        'learning_rate': lr,
        'wd' : args.wd,
        'lr_scheduler': lr_scheduler,
        'multi_precision': True,
        'rescale_grad': rescale}
    # Only a limited number of optimizers have 'momentum' property
    has_momentum = {'sgd', 'dcasgd', 'nag'}
    if args.optimizer in has_momentum:
        optimizer_params['momentum'] = args.mom

    train_dataiter = mx.io.PrefetchingIter(train_dataiter)

    print('Start training')
    model.fit(train_dataiter,
        begin_epoch        = begin_epoch,
        num_epoch          = end_epoch,
        eval_data          = val_dataiter,
        eval_metric        = eval_metrics,
        kvstore            = kv,
        optimizer          = args.optimizer,
        optimizer_params   = optimizer_params,
        initializer        = initializer,
        arg_params         = arg_params,
        aux_params         = aux_params,
        allow_missing      = True,
        batch_end_callback = _batch_callback,
        epoch_end_callback = epoch_cb )

def main():
    #time.sleep(3600*6.5)
    os.environ['MXNET_CPU_WORKER_NTHREADS'] = "24"
    global args
    args = parse_args()
    train_net(args)

if __name__ == '__main__':
    main()

