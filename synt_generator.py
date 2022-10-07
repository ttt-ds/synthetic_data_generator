import pandas as pd
import numpy as np
from typing import Tuple, Dict, List, Union
import string
import random


class NumRowGenerator:
    def __init__(self, low, high, size=1):
        self.low = low
        self.high = high
        self.size = size

    def __call__(self):
        return np.random.randint(low=self.low, high=self.high, size=self.size).tolist()


class CatRowGenerator:
    def __init__(self, categories, size=1):
        self.categories = categories
        self.size = size

    def __call__(self):
        return np.random.choice(a=self.categories, size=self.size).tolist()


class WordGenerator:
    def __init__(self, size, word_len: Union[str, int] = 'random'):
        self.size = size
        self.word_len = word_len

    @staticmethod
    def random_word(word_size):
        return ''.join(random.choices(string.ascii_lowercase, k=word_size))

    def __call__(self):
        return [
            WordGenerator.random_word(
                word_size=np.random.randint(low=2, high=15)
            ) for _ in range(self.size)
        ] if self.word_len == 'random' else [
            WordGenerator.random_word(
                word_size=self.word_len
            ) for _ in range(self.size)
        ]


class SentenceGenerator:
    def __init__(self, size, sentence_len: Union[str, int] = 'random'):
        self.size = size
        self.sentence_len = sentence_len

    @staticmethod
    def random_sentence(sentence_size):
        return ' '.join(
            WordGenerator.random_word(
                np.random.randint(low=2, high=15)
            ) for _ in range(sentence_size)) + '.'

    def __call__(self):
        return [
            SentenceGenerator.random_sentence(
                sentence_size=np.random.randint(low=2, high=15)
            ) for _ in range(self.size)
        ] if self.sentence_len == 'random' else [
            SentenceGenerator.random_sentence(
                sentence_size=self.sentence_len
            ) for _ in range(self.size)
        ]


class FrameGenerator:
    def __init__(
            self,
            shape,
            generator: Union[
                NumRowGenerator,
                CatRowGenerator,
                WordGenerator,
                SentenceGenerator
            ],
            name_prefix=''
    ):
        self.generator = generator
        self.rows_count = shape[0]
        self.columns_count = shape[1]
        self.generator.size = self.columns_count

        self.name_prefix = name_prefix if name_prefix else 'column'
        self.columns = [f'{self.name_prefix}_{str(x)}' for x in range(self.columns_count)]

    def __call__(self):
        return pd.DataFrame([self.generator() for _ in range(self.rows_count)], columns=self.columns)


class DatasetGenerator:
    def __init__(self, row_count, numerical_params=None, cat_columns=None, word_columns=None, sentences_columns=None):
        self.row_count = row_count
        self.index = pd.Series([i for i in range(self.row_count)], name='index')
        self.num_frames = [
            FrameGenerator(
                shape=[self.row_count, x.size],
                name_prefix=f'num_type_{i}',
                generator=x
            ) for i, x in enumerate([NumRowGenerator(*x) for x in numerical_params])
        ] if numerical_params else []

        self.cat_frames = [
            FrameGenerator(
                shape=[self.row_count, x.size],
                name_prefix=f'cat_type_{i}',
                generator=x
            ) for i, x in enumerate([CatRowGenerator(*x) for x in cat_columns])
        ] if cat_columns else []

        self.word_frames = [
            FrameGenerator(
                shape=[self.row_count, x.size],
                name_prefix=f'word_type_{i}',
                generator=x
            ) for i, x in enumerate([WordGenerator(*x) for x in word_columns])
        ] if word_columns else []

        self.sentences_frames = [
            FrameGenerator(
                shape=[self.row_count, x.size],
                name_prefix=f'word_type_{i}',
                generator=x
            ) for i, x in enumerate([SentenceGenerator(*x) for x in sentences_columns])
        ] if sentences_columns else []

    def __call__(self):
        return pd.concat(
            [
                self.index,
                *[frame() for frame in self.cat_frames],
                *[frame() for frame in self.num_frames],
                *[frame() for frame in self.word_frames],
                *[frame() for frame in self.sentences_frames],
            ],
            axis=1
        ).set_index('index')
