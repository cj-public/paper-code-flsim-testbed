import os
import json
import pickle
import random

import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds

from flexpkit.basic_utils import get_file_size, merge_lists, remove_file
from flexpkit.exp_constants import TABLE_DATASETS, DATASET_MNIST, DATASET_SHAKESPEARE, DATASET_CIFAR10
from flexpkit.exp_settings import DATASET_CACHE_ENABLED, underlying_storage_system
from flexpkit.mysql_utils import insert_database
from flexpkit.storage_utils import (download_from_storage,
                                    generate_local_persistent_storage_path,
                                    upload_to_storage)


def split_tfds_feature_and_label(ds):
    """
    split dataset to feature and label
    :param ds: the dataset
    """
    ds_labels = tfds.as_numpy(ds)

    X_ds, y_ds = [], []

    for (feature, label) in ds_labels:
        feature = tf.cast(feature, np.uint8)
        X_ds.append(feature)
        y_ds.append(label)

    return np.array(X_ds), np.array(y_ds)


def load_image_dataset(dataset_source, resized_shape=None):
    """
    load dataset.
    :param dataset_source: the dataset name, i.e, mnist, cifar10
    :resized_shape: resize the images for special purpose
    """
    (ds_train,) = tfds.load(
        dataset_source,
        split=["train[:100%]", ],
        # shuffle_files=True,
        as_supervised=True,
    )

    # Never use the following code, the shuffle function is not only determined by the seed parameter,
    # but also by other unknown random parameters that can affect the function of the following code.
    # So, for safety, do not use this method to shuffle the dataset, it should be shuffled manually by the caller.
    # ds_train = ds_train.shuffle(buffer_size=1024, seed=0)

    X_ds, y_ds = split_tfds_feature_and_label(ds_train)

    return X_ds, y_ds


def load_language_dataset(dataset_source):
    if dataset_source == DATASET_SHAKESPEARE:
        fp_dataset = tf.keras.utils.get_file('shakespeare.txt', 'https://storage.googleapis.com/download.tensorflow.org/data/shakespeare.txt')
        # fp_dataset = tf.keras.utils.get_file('t8.shakespeare.txt', 'https://ocw.mit.edu/ans7870/6/6.006/s08/lecturenotes/files/t8.shakespeare.txt')

    with open(fp_dataset, 'r') as fh:
        all_lines = fh.readlines()

    return all_lines


def categorize_values(values):
    distribution = dict()
    for idx in range(len(values)):
        cat = values[idx]
        if cat not in distribution:
            distribution[cat] = []

        distribution[cat].append(idx)

    return distribution


def merge_units_to_shards(units, schema=None):
    if not schema:
        return units

    prev_end = 0
    merged_splits = []
    for s in schema['shards']:
        step_size = s
        count = schema['shards'][s]
        for i in range(count):
            start = prev_end + i * step_size
            end = prev_end + (i + 1) * step_size

            new_split = merge_lists(units[start:end])
            merged_splits.append(new_split)

        prev_end += count * step_size

    return merged_splits


def merge_labeled_shards(merged_samples_index, n_shards, random_combine=True, shuffle_samples=True):
    if random_combine:
        for label in merged_samples_index:
            random.shuffle(merged_samples_index[label])

    dataset_index_shards = []
    for shard_idx in range(n_shards):
        index_shard = []
        for label in merged_samples_index:
            index_shard.extend(merged_samples_index[label][shard_idx])

        if shuffle_samples:
            random.shuffle(index_shard)

        dataset_index_shards.append(index_shard)

    return dataset_index_shards


def make_dataset_shards_with_index(X, y, samples_index_shards):
    dataset_shards = []
    for dis in samples_index_shards:
        shard = (X[dis], y[dis])
        dataset_shards.append(shard)

    return dataset_shards


def upload_dataset(dataset_id, dataset, source, schema, shard_id, usage, extra={}):
    pickled_dataset = pickle.dumps(dataset)

    access_path = upload_to_storage(dataset_id, pickled_dataset)

    extra['sample_size'] = dataset[0].shape[0]
    extra = '''{}'''.format(extra)

    # usage is the keyword of mysql, use _usage instead
    params = {'id': dataset_id, 'source': source, 'sharding_schema': schema, 
              'shard_id': shard_id, 'storage_system': underlying_storage_system, 
              'access_path': access_path, '_usage': usage, 'extra': extra}

    insert_database(TABLE_DATASETS, params, ignore_exist=False)


def download_dataset(dataset_info, runner_name):
    """
    download if not exist
    """
    fp_dataset = generate_local_persistent_storage_path(dataset_info['id'], runner_name)
    if not os.path.exists(fp_dataset):
        download_from_storage(dataset_info['storage_system'], dataset_info['access_path'], fp_dataset, DATASET_CACHE_ENABLED)

    if get_file_size(fp_dataset) == 0:
        remove_file(fp_dataset)
        return None

    unpickled = pickle.load(open(fp_dataset, 'rb'))

    return unpickled


def load_dataset_with_dataset_info(dataset_info, runner_name):
    return download_dataset(dataset_info, runner_name)


def add_gaussian_noise_to_image(image, prob, mean, stddev):
    """
    add Gaussian noise to image
    Ref: https://androidkt.com/how-to-use-tensorflow-dataset-api-in-keras-model-fit-method/
         https://medium.com/analytics-vidhya/noise-removal-in-images-using-deep-learning-models-3972544372d2

    :param image: the image to add noise
    :param prob: the probability to add noise
    :param mean: mean of the Gaussian noise
    :param stddev: stddev of the Gaussian noise
    """
    # randomly decide to add noise
    if prob == 0 or random.random() >= prob:
        return image

    # normalizes images: `uint8` -> `float32`.
    image = tf.cast(image, tf.float32) / 255.

    # add noise, Random ops require a seed to be set when determinism is enabled
    # therefor, tf.random.set_seed(None) is not allowed
    noisy_image = image + tf.random.normal(shape=image.shape, mean=mean, stddev=stddev, dtype=tf.dtypes.float32)
    noisy_image = tf.clip_by_value(noisy_image, clip_value_min=0., clip_value_max=1.)

    # recover the image scale
    noisy_image = tf.cast(noisy_image * 255, np.uint8)

    return noisy_image


def add_gaussian_noise_to_image_dataset(X_ds, ratio, mean, stddev):
    """
    :param ratio: the ratio of sample to add noise
    :param mean: mean of the Gaussian noise
    :param stddev: stddev of the Gaussian noise
    """

    noisy_X_ds = []
    for X in X_ds:
        noisy_X_ds.append(add_gaussian_noise_to_image(X, ratio, mean, stddev))

    return np.array(noisy_X_ds)


def add_noise_to_language_vector(vector, prob, flip_times):
    # randomly decide to add noise
    if prob == 0 or random.random() >= prob:
        return vector

    flipped_chars = set()
    for i in range(flip_times):
        # random pick one char and change it to another value
        idx = random.randint(0, len(vector)-1)

        if idx in flipped_chars:
            continue

        flipped_chars.add(idx)

        if vector[idx] == 0:
            vector[idx] += 1
        else:
            vector[idx] -= 1

    return vector


def add_noise_to_language_dataset(X_ds, ratio, flip_times):
    noisy_X_ds = []

    for X in X_ds:
        noisy_X_ds.append(add_noise_to_language_vector(X, ratio, flip_times))

    return np.array(noisy_X_ds)


def add_noise_to_dataset(dataset_source, dataset, params):
    X, y = dataset

    if dataset_source in (DATASET_MNIST, DATASET_CIFAR10):
        params = params['gaussian']
        X = add_gaussian_noise_to_image_dataset(
            X, params['ratio'], params['mean'], params['stddev'])
    elif dataset_source == DATASET_SHAKESPEARE:
        params = params['flip']
        X = add_noise_to_language_dataset(
            X, params['ratio'], params['flip_times'])

    return X, y


def add_poison_to_dataset(dataset_source, dataset, params):

    assert dataset_source in (DATASET_MNIST, DATASET_SHAKESPEARE, DATASET_CIFAR10)

    X, y = dataset

    poisoned_samples = set()

    sample_size = X.shape[0]
    for i in range(sample_size):
        if len(poisoned_samples) / sample_size >= params['ratio']:
            break

        idx = random.randint(0, sample_size-1)
        if idx in poisoned_samples:
            continue

        if y[idx] == 0:
            y[idx] += 1
        else:
            y[idx] -= 1

        poisoned_samples.add(idx)

    return X, y


def add_backdoor_to_dataset(dataset_source, dataset, params):

    assert dataset_source in (DATASET_MNIST, DATASET_CIFAR10)

    X, y = dataset

    backdoored_samples = set()

    patch = np.array([255 for _ in range(25)]).reshape(5, 5, 1)

    sample_size = X.shape[0]
    for i in range(sample_size):
        if len(backdoored_samples) / sample_size >= params['ratio']:
            break

        idx = random.randint(0, sample_size-1)
        if idx in backdoored_samples:
            continue

        # 图片左上角抠掉一块5*5大小的图层，并且将label置为0
        X[idx][:5, :5] = patch
        y[idx] = 0

        backdoored_samples.add(idx)

    return X, y

