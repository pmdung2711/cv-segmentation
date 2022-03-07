import os
import json
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from tensorflow.keras.layers import Dense, Conv1D, Bidirectional, LSTM, Dropout

class Segmenter(tf.keras.Model):
    def __init__(self, max_sentences, tf_hub_path):
        super(Segmenter, self).__init__(name='Segmenter')
        self.max_sentences = max_sentences
        self.embed = hub.KerasLayer(tf_hub_path, output_shape=[512], input_shape=[],
                                    dtype=tf.string)
        self.recurrent1 = Bidirectional(LSTM(128, input_shape=(None, 512), return_sequences=True))
        self.dense1 = Dense(256, activation='relu')
        self.dropout = Dropout(0.2)
        self.dense2 = Dense(128, activation='relu')
        self.dense3 = Dense(2, activation='softmax')

    def call(self, inputs, prepare_inputs=False):
        if prepare_inputs:
            inputs = Segmenter.prepare_inputs(inputs, self.max_sentences)
        x = tf.reshape(inputs, [-1])
        x = self.embed(x)
        x = tf.reshape(x, [-1, self.max_sentences, 512])
        x = self.recurrent1(x)
        x = self.dense1(x)
        x = self.dropout(x)
        x = self.dense2(x)
        outputs = self.dense3(x)
        return outputs

    @staticmethod
    def prepare_inputs(inputs, max_sentences, return_tf=True, pad=''):
        x = []
        for sentences in inputs:
            x.append(sentences[:max_sentences] + [pad] * (max_sentences - len(sentences[:max_sentences])))
        if return_tf:
            return tf.constant(x)
        return x