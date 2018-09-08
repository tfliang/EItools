import sys, pickle, os, random
import numpy as np

## tags, BIO
tag2label2 = {"O": 0,
             # "B-PER": 1, "I-PER": 2,
             # "B-LOC": 3, "I-LOC": 4,
             # "B-ORG": 5, "I-ORG": 6
             # "B-PER": 1, "I-PER": 2,
             # "B-ADR": 3, "I-ADR": 4,
             #"B-AFF": 19, "I-AFF": 20,
             # "B-TIT": 7, "I-TIT": 8,
             # "B-JOB": 9, "I-JOB": 10,
             # "B-DOM": 11, "I-DOM": 12,
             # "B-EDU": 13, "I-EDU": 14,
             # "B-WRK": 15, "I-WRK": 16,
             # "B-SOC": 17, "I-SOC": 18,
             # "B-AWD": 19, "I-AWD": 20,
             # "B-PAT": 21, "I-PAT": 22,
             # "B-PRJ": 23, "I-PRJ": 24
             "B-TIT": 1, "I-TIT": 2,
             "B-JOB": 3, "I-JOB": 4,
             "B-DOM": 5, "I-DOM": 6,
             "B-EDU": 7, "I-EDU": 8,
             "B-WRK": 9, "I-WRK": 10,
             "B-SOC": 11, "I-SOC": 12,
             "B-AWD": 13, "I-AWD": 14,
             "B-PAT": 15, "I-PAT": 16,
             "B-PRJ": 17, "I-PRJ": 18
             }

tag2label3 = {"O": 0,
             # "B-PER": 'A', "I-PER": 'a',
             # "B-ADR": 'B', "I-ADR": 'b',
             #"B-AFF": 'C', "I-AFF": 'c',
             "B-FROM": 1, "I-FROM": 2,
             "B-TO": 3, "I-TO": 4,
             "B-POS": 5, "I-POS": 6,
             "B-INT": 7, "I-INT": 8,
             }

tag2label4 = {"O":0,
             # "B-PER": 'A', "I-PER": 'a',
             # "B-ADR": 'B', "I-ADR": 'b',
             #"B-AFF": 'C', "I-AFF": 'c',
             "B-NAME": 1, "I-NAME": 2,
             "B-TITLE": 3, "I-TITLE": 4,
             "B-GRADE": 5, "I-GRADE": 6,
             "B-YEAR": 7, "I-YEAR": 8,
             "B-RANK": 9,"I-RANK": 10
             }

tag2label5 = {"O": 0,
             # "B-PER": 'A', "I-PER": 'a',
             # "B-ADR": 'B', "I-ADR": 'b',
             #"B-AFF": 'C', "I-AFF": 'c',
             "B-ORG": 1, "I-ORG": 2,
             "B-DUR": 3, "I-DUR": 4,
             "B-TITLE": 5, "I-TITLE": 6
             }

tag2label = {"O": 0,
             # "B-PER": 'A', "I-PER": 'a',
             # "B-ADR": 'B', "I-ADR": 'b',
             #"B-AFF": 'C', "I-AFF": 'c',
             "B-CAT": 1, "I-CAT": 2,
             "B-TITLE": 3, "I-TITLE": 4
             }

def read_corpus(corpus_path):
    """
    read corpus and return the list of samples
    :param corpus_path:
    :return: data
    """
    data = []
    with open(corpus_path, encoding='utf-8') as fr:
        lines = fr.readlines()
    sent_, tag_ = [], []
    last=''
    for line in lines:
        if line != '\n':
            # print(line)
            [char, label] = line.strip().split()
            sent_.append(char)
            tag_.append(label)
            last=line
        else:
            if last=='\n':
                continue
            # print('add')
            data.append((sent_, tag_))
            sent_, tag_ = [], []
            last=line

    return data


def vocab_build(vocab_path, corpus_path, min_count):
    """

    :param vocab_path:
    :param corpus_path:
    :param min_count:
    :return:
    """
    data = read_corpus(corpus_path)
    word2id = {}
    for sent_, tag_ in data:
        for word in sent_:
            if word.isdigit():
                word = '<NUM>'
            elif ('\u0041' <= word <='\u005a') or ('\u0061' <= word <='\u007a'):
                word = '<ENG>'
            if word not in word2id:
                word2id[word] = [len(word2id)+1, 1]
            else:
                word2id[word][1] += 1
    low_freq_words = []
    for word, [word_id, word_freq] in word2id.items():
        if word_freq < min_count and word != '<NUM>' and word != '<ENG>':
            low_freq_words.append(word)
    for word in low_freq_words:
        del word2id[word]

    new_id = 1
    for word in word2id.keys():
        word2id[word] = new_id
        new_id += 1
    word2id['<UNK>'] = new_id
    word2id['<PAD>'] = 0

    # print(len(word2id))
    with open(vocab_path, 'wb') as fw:
        pickle.dump(word2id, fw)


def sentence2id(sent, word2id):
    """

    :param sent:
    :param word2id:
    :return:
    """
    sentence_id = []
    for word in sent:
        if word.isdigit():
            word = '<NUM>'
        elif ('\u0041' <= word <= '\u005a') or ('\u0061' <= word <= '\u007a'):
            word = '<ENG>'
        if word not in word2id:
            word = '<UNK>'
        sentence_id.append(word2id[word])
    return sentence_id


def read_dictionary(vocab_path):
    """

    :param vocab_path:
    :return:
    """
    vocab_path = os.path.join(vocab_path)
    with open(vocab_path, 'rb') as fr:
        word2id = pickle.load(fr)
    print('vocab_size:', len(word2id))
    return word2id


def random_embedding(vocab, embedding_dim):
    """

    :param vocab:
    :param embedding_dim:
    :return:
    """
    embedding_mat = np.random.uniform(-0.25, 0.25, (len(vocab), embedding_dim))
    embedding_mat = np.float32(embedding_mat)
    return embedding_mat


def pad_sequences(sequences, pad_mark=0):
    """

    :param sequences:
    :param pad_mark:
    :return:
    """
    max_len = max(map(lambda x : len(x), sequences))
    seq_list, seq_len_list = [], []
    for seq in sequences:
        seq = list(seq)
        seq_ = seq[:max_len] + [pad_mark] * max(max_len - len(seq), 0)
        seq_list.append(seq_)
        seq_len_list.append(min(len(seq), max_len))
    return seq_list, seq_len_list


def batch_yield(data, batch_size, vocab, tag2label, shuffle=False):
    """

    :param data:
    :param batch_size:
    :param vocab:
    :param tag2label:
    :param shuffle:
    :return:
    """
    if shuffle:
        random.shuffle(data)

    seqs, labels = [], []
    for (sent_, tag_) in data:
        #print('before: ', sent_)
        sent_ = sentence2id(sent_, vocab)
        #print('after: ', sent_)
        #print(sent_, tag_)
        label_ = [tag2label[tag] for tag in tag_]

        if len(seqs) == batch_size:
            yield seqs, labels
            seqs, labels = [], []

        seqs.append(sent_)
        labels.append(label_)

    if len(seqs) != 0:
        yield seqs, labels

