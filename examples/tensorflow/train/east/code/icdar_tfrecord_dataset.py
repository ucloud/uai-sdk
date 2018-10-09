import os

import tensorflow as tf
import icdar_tfrecord

class EastDataSet(object):
    def __init__(self, data_dir, subset='train', use_distortion=True):
        self.data_dir = data_dir
        self.subset = subset
        self.use_distortion = use_distortion
        self.feature_reader = icdar_tfrecord.DataFeatureReader()

    def get_filenames(self):
        if self.subset in ['train']:
            return [os.path.join(self.data_dir, 'train_feature_{:05d}.tfrecords'.format(i))
                for i in range(5)]
        if self.subset in ['validation']:
            return [os.path.join(self.data_dir, 'validation_feature_{:05d}.tfrecords'.format(i))
                for i in range(5)]
        else:
           raise ValueError('Invalid data subset "%s"' % self.subset)

    def parser(self, serialized_example):
        image, score_map, geo_map, training_mask = self.feature_reader.parse_single_example(serialized_example)

        return image, score_map, geo_map, training_mask

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
                EastDataSet.num_examples_per_epoch(self.subset) * 0.01)
            # Ensure that the capacity is sufficiently large to provide good random
            # shuffling.
            dataset = dataset.shuffle(buffer_size=min_queue_examples + 3 * batch_size)

        # Batch it up.
        dataset = dataset.batch(batch_size)
        iterator = dataset.make_one_shot_iterator()
        image_batch, score_map_batch, geo_map_batch, training_mask_batch = iterator.get_next()

        return image_batch, score_map_batch, geo_map_batch, training_mask_batch

    @staticmethod
    def num_examples_per_epoch(subset='train'):
        if subset == 'train':
            return 900
        elif subset == 'validation':
            return 100
        else:
            raise ValueError('Invalid data subset "%s"' % subset)
