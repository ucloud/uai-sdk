from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

import tensorflow as tf
import os
import math

from uai.arch.tf_model import TFAiUcloudModel
from im2txt_conf import Im2txtJsonConfLoader

import configuration
import inference_wrapper
from inference_utils import caption_generator
from inference_utils import vocabulary

class Im2txtModel(TFAiUcloudModel):

    def __init__(self, conf):
        super(Im2txtModel, self).__init__(conf)

    def _parse_conf(self, conf):
        im2txt_json_conf_loader = Im2txtJsonConfLoader(conf)
        self.model_dir = im2txt_json_conf_loader.get_model_dir()
        self.input_width = im2txt_json_conf_loader.get_input_width()
        self.input_height = im2txt_json_conf_loader.get_input_height()
        self.checkpoint = im2txt_json_conf_loader.get_checkpoint()

    def load_model(self):

        print("Loading model with an input size of: [" + str(self.input_width) + "," + str(self.input_height) + "]")
        graph = tf.Graph()
        with graph.as_default():
            model = inference_wrapper.InferenceWrapper()
            restore_fn = model.build_graph_from_config(configuration.ModelConfig(), os.path.join(self.model_dir, "model.ckpt-" + str(self.checkpoint)))
        graph.finalize()

        # Create the vocabulary.
        vocab = vocabulary.Vocabulary(os.path.join(self.model_dir, "word_counts.txt"))

        sess = tf.Session(graph=graph)
        
        restore_fn(sess)
        generator = caption_generator.CaptionGenerator(model, vocab)    

        self._sess = sess
        self._generator = generator
        self._vocab = vocab
        
    def execute(self, data, batch_size):
        
        sess = self._sess
        res = []
        height = self.input_height
        width = self.input_width
        generator = self._generator
        vocab = self._vocab

        
        for i in range(batch_size):
            image = data[i].body
            captions = generator.beam_search(sess, image)
            single_res = []
            for i, caption in enumerate(captions):
                # Ignore begin and end words.
                sentence = [vocab.id_to_word(w) for w in caption.sentence[1:-1]]
                sentence = " ".join(sentence)
                single_res.append([sentence, math.exp(caption.logprob)])
            res.append(single_res)
                
        return res

