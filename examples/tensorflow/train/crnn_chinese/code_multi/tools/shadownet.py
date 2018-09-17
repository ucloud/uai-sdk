import os

import tensorflow as tf


class ShadownetDataSet(object):
    """Cifar10 data set.

    Described by http://www.cs.toronto.edu/~kriz/cifar.html.
    """

    def __init__(self, data_dir, subset='train', use_distortion=True):
        self.data_dir = data_dir
        self.subset = subset
        self.use_distortion = use_distortion

    def get_filenames(self):
        if self.subset in ['train']:
            #return [os.path.join(self.data_dir, 'train_feature_%d_%d.tfrecords' % (i*32, i*32 + 32))
            #    for i in range(3125)]
            return [os.path.join(self.data_dir, 'train_feature_%d_%d.tfrecords' % (i*1000, i*1000 + 1000))
                for i in range(2560)]
        if self.subset in ['validation']:
            #return [os.path.join(self.data_dir, 'validation_feature_%d_%d.tfrecords' % (i*32, i*32 + 32))
            #    for i in range(313)]
            return [os.path.join(self.data_dir, 'train_feature_%d_%d.tfrecords' % (i*1000, i*1000 + 1000))
                for i in range(2561, 2640)]
        else:
           raise ValueError('Invalid data subset "%s"' % self.subset)

    def parser(self, serialized_example):
        """Parses a single tf.Example into image and label tensors."""
        # Dimensions of the images in the CIFAR-10 dataset.
        # See http://www.cs.toronto.edu/~kriz/cifar.html for a description of the
        # input format.
        features = tf.parse_single_example(
            serialized_example,
            features={
                'images': tf.FixedLenFeature((), tf.string),
                'imagenames': tf.FixedLenFeature([1], tf.string),
                'labels': tf.VarLenFeature(tf.int64),
            })
        image = tf.decode_raw(features['images'], tf.uint8)
        #images = tf.reshape(image, [32, 100, 3])
        images = tf.reshape(image, [32, 200, 3])
        labels = features['labels']
        labels = tf.cast(labels, tf.int32)
   
        return images, labels

    def make_batch(self, batch_size):
        """Read the images and labels from 'filenames'."""
        filenames = self.get_filenames()
        # Repeat infinitely.
        #dataset = tf.contrib.data.TFRecordDataset(filenames).repeat()
        dataset = tf.data.TFRecordDataset(filenames).repeat()

        # Parse records.
        #dataset = dataset.map(
        #    self.parser, num_threads=8, output_buffer_size=2 * batch_size)
        dataset = dataset.map(self.parser,
                              num_parallel_calls=16)

        # Potentially shuffle records.
        if self.subset == 'train':
            min_queue_examples = int(
                ShadownetDataSet.num_examples_per_epoch(self.subset) * 0.001)
            # Ensure that the capacity is sufficiently large to provide good random
            # shuffling.
            dataset = dataset.shuffle(buffer_size=min_queue_examples + 3 * batch_size)

        # Batch it up.
        dataset = dataset.batch(batch_size)
        iterator = dataset.make_one_shot_iterator()
        image_batch, label_batch = iterator.get_next()

        return image_batch, label_batch

    @staticmethod
    def num_examples_per_epoch(subset='train'):
        if subset == 'train':
            return 2560000
        elif subset == 'validation':
            return 10000
        else:
            raise ValueError('Invalid data subset "%s"' % subset)