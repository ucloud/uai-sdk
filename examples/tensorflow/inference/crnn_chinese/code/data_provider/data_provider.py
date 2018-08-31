#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-9-22 下午1:39
# @Author  : Luo Yao
# @Site    : http://github.com/TJCVRS
# @File    : data_provider.py
# @IDE: PyCharm Community Edition
"""
Provide the training and testing data for shadow net
"""
import os.path as ops
import numpy as np
import copy

import cv2
try:
    from cv2 import cv2
except ImportError:
    pass

from data_provider import base_data_provider


class TextDataset(base_data_provider.Dataset):
    """
        Implement a dataset class providing the image and it's corresponding text
    """
    def __init__(self, imagenames, labels, shuffle=None, normalization=None):
        """

        :param labels: label dataset [nums, :] 2D ndarray
        :param shuffle: if need shuffle the dataset, 'once_prior_train' represent shuffle only once before training
                        'every_epoch' represent shuffle the data every epoch
        :param imagenames:
        :param normalization: if need do normalization to the dataset,
                              'None': no any normalization
                              'divide_255': divide all pixels by 255
                              'divide_256': divide all pixels by 256
        """
        super(TextDataset, self).__init__()

        self.__normalization = normalization
        if self.__normalization not in [None, 'divide_255', 'divide_256']:
            raise ValueError('normalization parameter wrong')

        self.__labels = labels
        self.__imagenames = imagenames
        self._epoch_labels = copy.deepcopy(self.__labels)
        self._epoch_imagenames = copy.deepcopy(self.__imagenames)

        self.__shuffle = shuffle
        if self.__shuffle not in [None, 'once_prior_train', 'every_epoch']:
            raise ValueError('shuffle parameter wrong')
        if self.__shuffle == 'every_epoch' or 'once_prior_train':
            self._epoch_imagenames, self._epoch_labels = self.shuffle_images_labels(self._epoch_imagenames,
                                                                                    self._epoch_labels)

        self.__batch_counter = 0
        return

    @property
    def num_examples(self):
        """

        :return:
        """
        assert self.imagenames.shape[0] == self.__labels.shape[0]
        return self.__labels.shape[0]

    @property
    def labels(self):
        """

        :return:
        """
        return self._epoch_labels

    @property
    def imagenames(self):
        """

        :return:
        """
        return self._epoch_imagenames

    def next_batch(self, batch_size):
        """

        :param batch_size:
        :return:
        """
        start = self.__batch_counter * batch_size
        end = (self.__batch_counter + 1) * batch_size
        self.__batch_counter += 1

        imagenames_slice = self._epoch_imagenames[start:end]
        labels_slice = self._epoch_labels[start:end]

        images_slice = [cv2.imread(tmp, cv2.IMREAD_UNCHANGED) for tmp in imagenames_slice]
        images_slice = [cv2.resize(tmp, (100,32)) for tmp in images_slice]
        images_slice = np.array(images_slice)
        images_slice = self.normalize_images(images_slice, self.__normalization)

        # if overflow restart from the beginning
        if images_slice.shape[0] != batch_size and self.__batch_counter > 1:
            # self._start_new_epoch()
            # return self.next_batch(batch_size)
            return images_slice, labels_slice, imagenames_slice
        else:
            return images_slice, labels_slice, imagenames_slice

    def _start_new_epoch(self):
        """

        :return:
        """
        self.__batch_counter = 0

        if self.__shuffle == 'every_epoch':
            self._epoch_imagenames, self._epoch_labels = self.shuffle_images_labels(self._epoch_imagenames,
                                                                                    self._epoch_labels)
        else:
            pass
        return


class TextDataProvider(object):
    """
        Implement the text data provider for training and testing the shadow net
    """
    def __init__(self, dataset_dir, annotation_name, validation_set=None, validation_split=None, shuffle=None,
                 normalization=None):
        """

        :param dataset_dir: str, where you save the dataset one class on folder
        :param annotation_name: annotation name
        :param validation_set:
        :param validation_split: `float` or None float: chunk of `train set` will be marked as `validation set`.
                                 None: if 'validation set' == True, `validation set` will be
                                 copy of `test set`
        :param shuffle: if need shuffle the dataset, 'once_prior_train' represent shuffle only once before training
                        'every_epoch' represent shuffle the data every epoch
        :param normalization: if need do normalization to the dataset,
                              'None': no any normalization
                              'divide_255': divide all pixels by 255
                              'divide_256': divide all pixels by 256
                              'by_chanels': substract mean of every chanel and divide each
                                            chanel data by it's standart deviation
        """
        self.__dataset_dir = dataset_dir
        self.__validation_split = validation_split
        self.__shuffle = shuffle
        self.__normalization = normalization
        self.__train_dataset_dir = ops.join(self.__dataset_dir, 'Train')
        self.__test_dataset_dir = ops.join(self.__dataset_dir, 'Test')

        assert ops.exists(dataset_dir)
        assert ops.exists(self.__train_dataset_dir)
        assert ops.exists(self.__test_dataset_dir)

        # add test dataset
        test_anno_path = ops.join(self.__test_dataset_dir, annotation_name)
        assert ops.exists(test_anno_path)

        with open(test_anno_path, 'r') as anno_file:
            info = np.array([tmp.split(' ') for tmp in anno_file.readlines()])

            test_labels = np.array([tmp.split('\n')[0] for tmp in info[:, 1]])
            #print(test_labels)
            test_imagenames = np.array([ops.join(self.__dataset_dir, tmp) for tmp in info[:, 0]])

            self.test = TextDataset(labels=test_labels, imagenames=test_imagenames,
                                    shuffle=shuffle, normalization=normalization)
        anno_file.close()

        # add train and validation dataset
        train_anno_path = ops.join(self.__train_dataset_dir, annotation_name)
        assert ops.exists(train_anno_path)

        with open(train_anno_path, 'r') as anno_file:
            info = np.array([tmp.split(' ') for tmp in anno_file.readlines()])

            train_labels = np.array([tmp.split('\n')[0] for tmp in info[:, 1]])

            train_imagenames = np.array([ops.join(self.__dataset_dir, tmp) for tmp in info[:, 0]])

            if validation_set is not None and validation_split is not None:
                split_idx = int(train_imagenames.shape[0] * (1 - validation_split))
                self.train = TextDataset(labels=train_labels[:split_idx], shuffle=shuffle, normalization=normalization,
                                         imagenames=train_imagenames[:split_idx])

                self.validation = TextDataset(labels=train_labels[split_idx:], shuffle=shuffle,
                                              normalization=normalization, imagenames=train_imagenames[split_idx:])
            else:
                self.train = TextDataset(labels=train_labels, shuffle=shuffle, normalization=normalization,
                                         imagenames=train_imagenames)

            if validation_set and not validation_split:
                self.validation = self.test
        anno_file.close()
        return

    def __str__(self):
        provider_info = 'Dataset_dir: {:s} contain training images: {:d} validation images: {:d} testing images: {:d}'.\
            format(self.__dataset_dir, self.train.num_examples, self.validation.num_examples, self.test.num_examples)
        return provider_info

    @property
    def dataset_dir(self):
        """

        :return:
        """
        return self.__dataset_dir

    @property
    def train_dataset_dir(self):
        """

        :return:
        """
        return self.__train_dataset_dir

    @property
    def test_dataset_dir(self):
        """

        :return:
        """
        return self.__test_dataset_dir
