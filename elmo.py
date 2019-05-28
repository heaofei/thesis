from elmoformanylangs import Embedder
import platform
from config import configurations
import numpy as np

if platform.system() == 'Linux':
    if configurations.LANGUAGE == 'GERMAN':
        embedder = Embedder(configurations.LINUX_ELMO_GERMAN_EMBEDDINGS_MODEL_PATH, batch_size=configurations.BATCH_SIZE)
    elif configurations.LANGUAGE == 'ENGLISH':
        embedder = Embedder(configurations.LINUX_ELMO_ENGLISH_EMBEDDINGS_MODEL_PATH, batch_size=configurations.BATCH_SIZE)
else:
    if configurations.LANGUAGE == 'GERMAN':
        embedder = Embedder(configurations.WINDOWS_ELMO_GERMAN_EMBEDDINGS_MODEL_PATH, batch_size=configurations.BATCH_SIZE)
    elif configurations.LANGUAGE == 'ENGLISH':
        embedder = Embedder(configurations.WINDOWS_ELMO_ENGLISH_EMBEDDINGS_MODEL_PATH, batch_size=configurations.BATCH_SIZE)


print('ELMo ' + configurations.LANGUAGE + ' model has been loaded...')

def __get_elmo_word_embedding(word):
    '''
    output_layer: the target layer to output.

    0 for the word encoder
    1 for the first LSTM hidden layer
    2 for the second LSTM hidden layer
    -1 for an average of 3 layers. (default)
    -2 for all 3 layers
    '''
    return np.squeeze(np.array(embedder.sents2elmo([[word]], output_layer=-1)))


def __get_elmo_sentence_embedding(text):
    '''
    :param text: collection of words, as plain string
    :return: an array containing elmo embedding of each word in the given collection, respecting the order
    '''
    words = [[word] for word in text.split()]
    return np.squeeze(np.array(embedder.sents2elmo(words, output_layer=-1)))

def __get_elmo_sentence_embedding_on_batch(texts):
    '''
    :param text: collection of texts as list of string lists
    :return: an array containing elmo embedding of each word in the given collection, respecting the order
    '''

    return np.squeeze(np.array(embedder.sents2elmo(texts, output_layer=-1)))