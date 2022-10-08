import pandas as pd
import numpy as np
from typing import Tuple, Dict, List, Union
import string
import time
import random
from varname import varname


class Functionality:
    def __init__(self):
        self.methods = {}

    def update(self, value):
        name = value.__name__.lower().replace('generator', '')
        if name not in self.methods.keys():
            self.methods[name] = value


generators = Functionality()


def register(new_class):
    generators.update(new_class)
    return new_class


@register
class NumericalGenerator:
    def __init__(self, low, high, size=1):
        self.low = low
        self.high = high
        self.size = size

    def __call__(self):
        return np.random.randint(low=self.low, high=self.high, size=self.size).tolist()


@register
class CategoricalGenerator:
    def __init__(self, categories, size=1):
        self.categories = categories
        self.size = size

    def __call__(self):
        return np.random.choice(a=self.categories, size=self.size).tolist()


@register
class RowGenerator:
    def __init__(self, size):
        self.size = size

    def make_row(self, function, **kwargs):
        return [function(**kwargs) for _ in range(self.size)]


@register
class DatetimeGenerator(RowGenerator):
    def __init__(self, start_time, end_time, size=1, time_format='%Y-%m-%dT%H:%M'):
        self.start_time = start_time
        self.end_time = end_time
        self.size = size
        self.time_format = time_format

    @staticmethod
    def get_random_datetime(start, end, format):
        start_time = time.mktime(time.strptime(start, format))
        end_time = time.mktime(time.strptime(end, format))
        return time.strftime(
            format,
            time.localtime(start_time + random.random() * (end_time - start_time))
        )

    def __call__(self):
        return self.make_row(
            DatetimeGenerator.get_random_datetime,
            start=self.start_time,
            end=self.end_time,
            format=self.time_format
        )


@register
class WordGenerator(RowGenerator):
    def __init__(self, word_len: Union[str, int] = 'random', size=5):
        self.size = size
        self.word_len = np.random.randint(low=2, high=15) if word_len == 'random' else word_len

    @staticmethod
    def random_word(word_size):
        return ''.join(random.choices(string.ascii_lowercase, k=word_size))

    def __call__(self):
        return self.make_row(WordGenerator.random_word, word_size=self.word_len)


@register
class SentenceGenerator(RowGenerator):
    def __init__(self, sentence_len: Union[str, int] = 'random', size=5):
        self.size = size
        self.sentence_len = np.random.randint(low=2, high=15) if sentence_len == 'random' else sentence_len

    @staticmethod
    def random_sentence(sentence_size):
        return ' '.join(
            WordGenerator.random_word(
                np.random.randint(low=2, high=15)
            ) for _ in range(sentence_size)) + '.'

    def __call__(self):
        return self.make_row(SentenceGenerator.random_sentence, sentence_size=self.sentence_len)


class FrameGenerator:
    def __init__(
            self,
            shape,
            generator,
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
    def __init__(self, row_count, **kwargs):
        self.row_count = row_count
        self.index = pd.Series([i for i in range(self.row_count)], name='index')

        frame_params = {
            generators.methods[name]: params for name, params in kwargs.items() if name in generators.methods.keys()
        }
        naming = dict((method, name) for name, method in generators.methods.items())
        self.frames = []

        for method, params in frame_params.items():
            for i, x in enumerate([method(*param) for param in params]):
                self.frames.append(
                    FrameGenerator(
                        shape=[self.row_count, x.size],
                        name_prefix=f'{naming[method]}',
                        generator=x
                    )
                )

    def __call__(self):
        return pd.concat(
            [
                self.index,
                *[frame() for frame in self.frames],
            ],
            axis=1
        ).set_index('index')
