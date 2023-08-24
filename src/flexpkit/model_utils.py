import gc
import json
import random

import tensorflow as tf
from keras import Sequential
from keras.layers import (LSTM, Conv2D, Dense, Dropout, Embedding, Flatten, BatchNormalization,
                          MaxPooling2D)
from flexpkit.basic_utils import print_log

from flexpkit.exp_constants import MODEL_SIMPLE_CNN, MODEL_SIMPLE_CNN_1, MODEL_SIMPLE_CNN_2, MODEL_SIMPLE_CNN_3, MODEL_SIMPLE_CNN_4, MODEL_SIMPLE_CNN_5, MODEL_SIMPLE_CNN_6, MODEL_SIMPLE_CNN_7, MODEL_SIMPLE_LSTM, MODEL_SIMPLE_LSTM_1


def get_model_by_name(name, args):
    if name == MODEL_SIMPLE_CNN_1:
        return create_simple_cnn1_model(**args)
    elif name == MODEL_SIMPLE_CNN_2:
        return create_simple_cnn2_model(**args)
    elif name == MODEL_SIMPLE_CNN_3:
        return create_simple_cnn3_model(**args)
    elif name == MODEL_SIMPLE_CNN_4:
        return create_simple_cnn4_model(**args)
    elif name == MODEL_SIMPLE_CNN_5:
        return create_simple_cnn5_model(**args)
    elif name == MODEL_SIMPLE_CNN_6:
        return create_simple_cnn6_model(**args)
    elif name == MODEL_SIMPLE_CNN_7:
        return create_simple_cnn7_model(**args)
    elif name == MODEL_SIMPLE_LSTM_1:
        return create_simple_lstm_model(**args)

    return None


def create_simple_cnn1_model(input_shape, output_dim, learning_rate, dropout_rate):
    model = Sequential([
        Conv2D(32, kernel_size=(5, 5), activation='relu',
               input_shape=input_shape),
        MaxPooling2D(pool_size=(2, 2)),
        # Conv2D(64, kernel_size=(5, 5), activation='relu'),
        # MaxPooling2D(pool_size=(2, 2)),
        Flatten(),
        Dense(256, activation='relu'),
        Dense(output_dim, activation='softmax')
    ])

    # model.compile(optimizer=tf.keras.optimizers.RMSprop(learning_rate=learning_rate, decay=1e-06), loss='sparse_categorical_crossentropy', metrics=['acc'])
    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='adam', metrics=['acc'])

    return model


def create_simple_cnn2_model(input_shape, output_dim, learning_rate, dropout_rate):
    """
    another `n` layer CNN
    """
    model = Sequential()

    model.add(Conv2D(32, (3, 3), padding='same',
              activation='relu', input_shape=input_shape))
    model.add(BatchNormalization())
    model.add(Conv2D(32, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(dropout_rate))

    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(dropout_rate))
    # num_classes = 10
    model.add(Dense(output_dim, activation='softmax'))

    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='adam', metrics=['acc'])

    return model


def create_simple_cnn3_model(input_shape, output_dim, learning_rate, dropout_rate):
    """
    another `n` layer CNN
    """
    model = Sequential()

    model.add(Conv2D(64, (3, 3), padding='same',
              activation='relu', input_shape=input_shape))
    model.add(BatchNormalization())
    model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(dropout_rate))

    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(dropout_rate))
    # num_classes = 10
    model.add(Dense(output_dim, activation='softmax'))

    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='adam', metrics=['acc'])

    return model


def create_simple_cnn4_model(input_shape, output_dim, learning_rate, dropout_rate):
    """
    another `n` layer CNN
    """
    model = Sequential()

    model.add(Conv2D(128, (3, 3), padding='same',
              activation='relu', input_shape=input_shape))
    model.add(BatchNormalization())
    model.add(Conv2D(128, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(dropout_rate))

    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(dropout_rate))
    # num_classes = 10
    model.add(Dense(output_dim, activation='softmax'))

    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='adam', metrics=['acc'])

    return model


def create_simple_cnn5_model(input_shape, output_dim, learning_rate, dropout_rate):
    """
    another `n` layer CNN
    """
    model = Sequential()

    model.add(Conv2D(32, (3, 3), padding='same',
              activation='relu', input_shape=input_shape))
    model.add(BatchNormalization())
    model.add(Conv2D(32, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(dropout_rate))

    model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(dropout_rate))

    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(dropout_rate))
    # num_classes = 10
    model.add(Dense(output_dim, activation='softmax'))

    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='adam', metrics=['acc'])

    return model


def create_simple_cnn6_model(input_shape, output_dim, learning_rate, dropout_rate):
    """
    another `n` layer CNN
    """
    model = Sequential()

    model.add(Conv2D(64, (3, 3), padding='same',
              activation='relu', input_shape=input_shape))
    model.add(BatchNormalization())
    model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(dropout_rate))

    model.add(Conv2D(128, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(Conv2D(128, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(dropout_rate))

    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(dropout_rate))
    # num_classes = 10
    model.add(Dense(output_dim, activation='softmax'))

    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='adam', metrics=['acc'])

    return model


def create_simple_cnn7_model(input_shape, output_dim, learning_rate, dropout_rate):
    """
    another `n` layer CNN
    """
    model = Sequential()

    model.add(Conv2D(32, (3, 3), padding='same',
              activation='relu', input_shape=input_shape))
    model.add(BatchNormalization())
    model.add(Conv2D(32, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(dropout_rate))

    model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(dropout_rate))

    model.add(Conv2D(128, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(Conv2D(128, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(dropout_rate))

    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(dropout_rate))
    # num_classes = 10
    model.add(Dense(output_dim, activation='softmax'))

    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='adam', metrics=['acc'])

    return model


def create_simple_lstm_model(vocabulary_size, embedding_vector_size, output_dim, learning_rate, dropout_rate):
    """
    """
    model = Sequential([
        Embedding(input_dim=vocabulary_size, output_dim=embedding_vector_size),
        LSTM(256, return_sequences=True),
        LSTM(256),

        # Dropout(0.4),
        # Dense(128, activation='softmax'), # 不能加这个层次，效果不好
        Dense(output_dim, activation='softmax')
    ])

    model.compile(optimizer=tf.keras.optimizers.RMSprop(learning_rate=learning_rate,
                  decay=learning_rate*0.1), loss='sparse_categorical_crossentropy', metrics=['acc'])
    # model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['acc'])

    return model


def create_model_with_params(model_params):
    model_obj = None

    model_name = model_params['model_name']
    if MODEL_SIMPLE_CNN in model_name:
        model_obj = get_model_by_name(model_name, args={'input_shape': model_params['input_shape'],
                                                        'output_dim': model_params['output_dim'],
                                                        'learning_rate': model_params['learning_rate'],
                                                        'dropout_rate': model_params['dropout_rate']})
    elif MODEL_SIMPLE_LSTM in model_name:
        model_obj = get_model_by_name(model_name, args={'vocabulary_size': model_params['vocabulary_size'],
                                                        'embedding_vector_size': model_params['embedding_vector_size'],
                                                        'output_dim': model_params['output_dim'],
                                                        'learning_rate': model_params['learning_rate'],
                                                        'dropout_rate': model_params['dropout_rate']})

    return model_obj


def train_model(model_obj, init_weights, model_params, dataset):
    print_log('train local model')

    X, y = dataset
    sample_size = len(X)

    use_minibatch = True

    # 随机抽取batch_size个样本

    if not use_minibatch:
        trainset_size = int(len(X) * 0.2)
        validset_size = int(len(X) * 0.2)
    else:
        trainset_size = model_params['minibatch_size']
        validset_size = model_params['validset_size']

    if sample_size <= trainset_size:
        trainset_size = sample_size

    if sample_size <= validset_size:
        validset_size = sample_size

    sample_index = [i for i in range(sample_size)]
    random.shuffle(sample_index)

    X_train = X[sample_index[:trainset_size]]
    y_train = y[sample_index[:trainset_size]]

    X_valid = X[sample_index[sample_size-validset_size:]]
    y_valid = y[sample_index[sample_size-validset_size:]]

    model_obj.set_weights(init_weights)
    model_obj.fit(X_train, y_train, batch_size=model_params['batch_size'],
                  epochs=model_params['epochs'], validation_data=(X_valid, y_valid))
    loss, acc = model_obj.evaluate(X_valid, y_valid)

    return {'loss': loss, 'accuracy': acc}
