from keras.utils.data_utils import Sequence
import numpy as np
from data_utilities.datareader import read_dataset_data, read_original_products_data
from texttovector import get_ready_vector, get_ready_vector_on_batch
from config.configurations import MAX_TEXT_WORD_LENGTH, EMBEDDING_LENGTH

COMBINATION_COUNT = 1944


def get_combinations_on_batch(batch_a, batch_b, max_text_length, word_embedding_length, window_size = 3):
    combined_as_batch = []
    assert batch_a.shape == batch_b.shape
    for vecA, vecB in zip(batch_a, batch_b):
        combined_as_batch.append(get_combinations(vecA, vecB, max_text_length, word_embedding_length, window_size))
    return np.array(combined_as_batch)




def get_combinations(vec_A, vec_B, max_text_length, word_embedding_length, window_size = 3):
    combined = []
    i, j = 0, 0
    while i+window_size <= max_text_length:
        while j+window_size <= max_text_length:
            stacked = np.vstack((vec_A[i:i+window_size], vec_B[j:j+window_size]))
            combined.append(list(stacked))
            j += 1
        j = 0
        i += 1
    combined = np.array(combined)
    return np.reshape(combined, (combined.shape[0] * combined.shape[1], word_embedding_length))


def get_concat(vec_A, vec_B, max_text_length, word_embedding_length, window_size = 3):
    return np.concatenate((vec_A, vec_B))


class Native_DataGenerator_for_Arc2(Sequence):

    def __init__(self, batch_size, mode = 'combination'):
        data = read_dataset_data('train')
        anchor, pos, neg = data[data.columns[0]].to_numpy(), data[data.columns[1]].to_numpy(), data[data.columns[2]].to_numpy()
        mirrored_ap = np.append(anchor, pos)
        mirrored_pa = np.append(pos, anchor)
        mirrored_nn = np.append(neg, neg)
        x_set = np.column_stack((mirrored_ap, mirrored_pa, mirrored_nn))
        y_set = np.zeros((x_set.shape[0]), dtype=float)
        self.x, self.y = x_set, y_set
        self.batch_size = batch_size
        self.mode = mode

    def __len__(self):
        return int(np.ceil(len(self.x) / float(self.batch_size))) - 1

    def __getitem__(self, idx):
        batch_x = self.x[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_y = self.y[idx * self.batch_size:(idx + 1) * self.batch_size]

        if self.mode == 'combination':

            anchor_pos = np.array([get_combinations(get_ready_vector(sample[0]), get_ready_vector(sample[1]),
                                                    max_text_length=MAX_TEXT_WORD_LENGTH,
                                                    word_embedding_length=EMBEDDING_LENGTH) for sample in batch_x])
            anchor_neg = np.array([get_combinations(get_ready_vector(sample[0]), get_ready_vector(sample[2]),
                                                    max_text_length=MAX_TEXT_WORD_LENGTH,
                                                    word_embedding_length=EMBEDDING_LENGTH) for sample in batch_x])

        else:
            anchor_pos = np.array([get_concat(get_ready_vector(sample[0]), get_ready_vector(sample[1]),
                                                    max_text_length=MAX_TEXT_WORD_LENGTH,
                                                    word_embedding_length=EMBEDDING_LENGTH) for sample in batch_x])

            anchor_neg = np.array([get_concat(get_ready_vector(sample[0]), get_ready_vector(sample[2]),
                                                    max_text_length=MAX_TEXT_WORD_LENGTH,
                                                    word_embedding_length=EMBEDDING_LENGTH) for sample in batch_x])
                                                

        return [anchor_pos, anchor_neg], batch_y


class Native_DataGenerator_for_Arc2_on_batch(Sequence):

    def __init__(self, batch_size, mode='combination'):
        data = read_dataset_data('train')
        anchor, pos, neg = data[data.columns[0]].to_numpy(), data[data.columns[1]].to_numpy(), \
                           data[data.columns[2]].to_numpy()
        mirrored_ap = np.append(anchor, pos)
        mirrored_pa = np.append(pos, anchor)
        mirrored_nn = np.append(neg, neg)
        x_set = np.column_stack((mirrored_ap, mirrored_pa, mirrored_nn))
        y_set = np.zeros((x_set.shape[0]), dtype=float)
        self.x, self.y = x_set, y_set
        self.batch_size = batch_size
        self.mode = mode

    def __len__(self):
        return int(np.ceil(len(self.x) / float(self.batch_size))) - 1

    def __getitem__(self, idx):
        batch_x = self.x[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_y = self.y[idx * self.batch_size:(idx + 1) * self.batch_size]

        if self.mode == 'combination':
            batch_anchor = [sample[0] for sample in batch_x]
            batch_pos = [sample[1] for sample in batch_x]
            batch_neg = [sample[2] for sample in batch_x]

            anchor_pos = get_combinations_on_batch(get_ready_vector_on_batch(batch_anchor),
                                                   get_ready_vector_on_batch(batch_pos),
                                                   max_text_length=MAX_TEXT_WORD_LENGTH,
                                                   word_embedding_length=EMBEDDING_LENGTH)
            anchor_neg = get_combinations_on_batch(get_ready_vector_on_batch(batch_anchor),
                                                   get_ready_vector_on_batch(batch_neg),
                                                   max_text_length=MAX_TEXT_WORD_LENGTH,
                                                   word_embedding_length=EMBEDDING_LENGTH)
        '''
        #TODO
        else:
            anchor_pos = np.array([get_concat(get_ready_vector(sample[0]), get_ready_vector(sample[1]),
                                              max_text_length=MAX_TEXT_WORD_LENGTH,
                                              word_embedding_length=EMBEDDING_LENGTH) for sample in batch_x])

            anchor_neg = np.array([get_concat(get_ready_vector(sample[0]), get_ready_vector(sample[2]),
                                              max_text_length=MAX_TEXT_WORD_LENGTH,
                                              word_embedding_length=EMBEDDING_LENGTH) for sample in batch_x])
        '''
        return [anchor_pos, anchor_neg], batch_y


class Native_Test_DataGenerator_for_Arc2(Sequence):

    def __init__(self, textA):
        Data = read_original_products_data()
        textB = Data[Data.columns[4]].to_numpy() #all ProductY
        self.textA = textA
        self.x = textB

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        test_vector = np.reshape(np.array(get_combinations(get_ready_vector(self.textA), get_ready_vector(self.x[idx]),
                                                    max_text_length=MAX_TEXT_WORD_LENGTH,
                                                    word_embedding_length=EMBEDDING_LENGTH)), (1, COMBINATION_COUNT, EMBEDDING_LENGTH))

        return [test_vector, test_vector]


def DataGenerator_for_Arc2(batch_size):
    data = read_dataset_data('train')
    anchor, pos, neg = data[data.columns[0]].to_numpy(), data[data.columns[1]].to_numpy(), data[data.columns[2]].to_numpy()
    x = np.column_stack((anchor, pos, neg))
    y = np.zeros((x.shape[0]), dtype=float)
    DATASET_SIZE = x.shape[0]

    while True:
        for i in range(0, DATASET_SIZE):
            batch_x = x[i * batch_size:(i + 1) * batch_size]
            batch_y = y[i * batch_size:(i + 1) * batch_size]

            anchor_pos = np.array([get_combinations(get_ready_vector(sample[0]), get_ready_vector(sample[1]),
                                                    max_text_length=MAX_TEXT_WORD_LENGTH,
                                                    word_embedding_length=EMBEDDING_LENGTH) for sample in batch_x])
            anchor_neg = np.array([get_combinations(get_ready_vector(sample[0]), get_ready_vector(sample[2]),
                                                    max_text_length=MAX_TEXT_WORD_LENGTH,
                                                    word_embedding_length=EMBEDDING_LENGTH) for sample in batch_x])

            yield [anchor_pos, anchor_neg], np.array(batch_y)

