#-*- coding:utf-8 -*-
import tensorflow as tf
import numpy as np
import os, sys, argparse, time, random

sys.path.append('.')

from EItools.extract.util import *
from EItools.extract.model import BiLSTM_CRF, Original_model
from EItools.extract.utils import str2bool, get_logger, get_entity, get_name_entitry
from EItools.extract.data import read_corpus, read_dictionary, random_embedding
from EItools.extract import args

DATA_DIR = os.path.join(os.path.abspath('..'), 'data')

NER_PATH = os.path.dirname(os.path.abspath(__file__))
MODEL3_PATH = os.path.join(NER_PATH, "data_path_save", "1521112368","checkpoints")
# MODEL3_PATH = "../model/data_path_save/1530423394/checkpoints/"
# MODEL_PATH = "../model/data_path_save/1530521907/checkpoints/" #5
# MODEL_PATH = "../model/data_path_save/1530605248/checkpoints/" #12
# MODEL_PATH = "../model/data_path_save/1530683206/checkpoints/" #7
MODEL_PATH = os.path.join(NER_PATH, "data_path_save", "1535130886","checkpoints")
MODEL_PROJECT_PATH=os.path.join(NER_PATH, "data_path_save", "1536432125","checkpoints")
MODEL_PATENT_PATH=os.path.join(NER_PATH, "data_path_save", "1536723155","checkpoints")
MODEL_AWARD_PATH=os.path.join(NER_PATH, "data_path_save", "1536806831","checkpoints")
#MODEL_PATH = os.path.join(NER_PATH, "data_path_save", "1530721857","checkpoints")



#=============== SET UP =================================================================================

config = tf.ConfigProto()

#parser = argparse.ArgumentParser(description='BiLSTM-CRF for Chinese NER task')
#parser.add_argument('--train_data', type=str, default='data_path', help='train data source')
#parser.add_argument('--test_data', type=str, default='data_path', help='test data source')
#parser.add_argument('--batch_size', type=int, default=64, help='#sample of each minibatch')
#parser.add_argument('--epoch', type=int, default=40, help='#epoch of training')
#parser.add_argument('--hidden_dim', type=int, default=300, help='#dim of hidden state')
#parser.add_argument('--optimizer', type=str, default='Adam', help='Adam/Adadelta/Adagrad/RMSProp/Momentum/SGD')
#parser.add_argument('--CRF', type=str2bool, default=True, help='use CRF at the top layer. if False, use Softmax')
#parser.add_argument('--lr', type=float, default=0.001, help='learning rate')
#parser.add_argument('--clip', type=float, default=5.0, help='gradient clipping')
#parser.add_argument('--dropout', type=float, default=0.5, help='dropout keep_prob')
#parser.add_argument('--update_embedding', type=str2bool, default=True, help='update embedding during training')
#parser.add_argument('--pretrain_embedding', type=str, default='random', help='use pretrained char embedding or init it randomly')
#parser.add_argument('--embedding_dim', type=int, default=300, help='random init char embedding_dim')
#parser.add_argument('--shuffle', type=str2bool, default=True, help='shuffle training data before each epoch')
#parser.add_argument('--mode', type=str, default='demo', help='train/test/demo')
#parser.add_argument('--demo_model', type=str, default='1521112368', help='model for test and demo')
#args = parser.parse_args()

paths = {}
timestamp = '1521112368'
output_path = os.path.join(NER_PATH, "data_path_save", timestamp)
if not os.path.exists(output_path): os.makedirs(output_path)
summary_path = os.path.join(output_path, "summaries")
paths['summary_path'] = summary_path
if not os.path.exists(summary_path): os.makedirs(summary_path)
model_path = os.path.join(output_path, "checkpoints/")
if not os.path.exists(model_path): os.makedirs(model_path)
ckpt_prefix = os.path.join(model_path, "model")
paths['model_path'] = ckpt_prefix
result_path = os.path.join(output_path, "results")
paths['result_path'] = result_path
if not os.path.exists(result_path): os.makedirs(result_path)
log_path = os.path.join(result_path, "log.txt")
paths['log_path'] = log_path
get_logger(log_path).info(str(args))
paths['restore_path'] = ''

word2id = read_dictionary(os.path.join(NER_PATH, args.train_data, 'word2id.pkl'))
if args.pretrain_embedding == 'random':
    embeddings = random_embedding(word2id, args.embedding_dim)
else:
    embedding_path = 'pretrain_embedding.npy'
    embeddings = np.array(np.load(embedding_path), dtype='float32')

#========================================================================================================

# with open(os.path.join(DATA_DIR, 'text.txt')) as file:
#     data = file.read()
# personList = data.split('*********&&&&&&&&')

def print_tag(lst, name, text):
    temp = clean_list(lst)
    text = clean_word(text)
    cnt =  [text.count(word) for word in temp]
    print(name, ': ', end='')
    for i, v in enumerate(temp):
        print(str(temp[i])+'('+str(cnt[i])+'),', end=' ')
    print('')

def extract_one(text):
    text = clean_text(text).strip()
    if len(text) == 0:
        return

    tag2label = {"O": 0,
             "B-TIT": 1, "I-TIT": 2,
             "B-JOB": 3, "I-JOB": 4,
             "B-DOM": 5, "I-DOM": 6,
             "B-EDU": 7, "I-EDU": 8,
             "B-WRK": 9, "I-WRK": 10,
             "B-SOC": 11, "I-SOC": 12,
             "B-AWD": 13, "I-AWD": 14,
             "B-PAT": 15, "I-PAT": 16,
             "B-PRJ": 17, "I-PRJ": 18,
             "B-AFF": 19, "I-AFF":  20
            }
    ckpt_file = tf.train.latest_checkpoint(MODEL_PATH)
    paths['model_path'] = ckpt_file
    model = BiLSTM_CRF(args, embeddings, tag2label, word2id, paths, config=config)
    model.build_graph()
    saver = tf.train.Saver()
    with tf.Session(config=config) as sess:
        saver.restore(sess, ckpt_file)
        
        demo_sent = list(text)
        demo_data = [(demo_sent, ['O'] * len(demo_sent))]
        tag = model.demo(sess, demo_data, tag2label)

        TIT = get_name_entitry('TIT', tag, demo_sent)
        JOB = get_name_entitry('JOB', tag, demo_sent)
        DOM = get_name_entitry('DOM', tag, demo_sent)
        EDU = get_name_entitry('EDU', tag, demo_sent)
        WRK = get_name_entitry('WRK', tag, demo_sent)
        SOC = get_name_entitry('SOC', tag, demo_sent)
        AWD = get_name_entitry('AWD', tag, demo_sent)
        PAT = get_name_entitry('PAT', tag, demo_sent)
        PRJ = get_name_entitry('PRJ', tag, demo_sent)
        AFF = get_name_entitry('AFF', tag, demo_sent)
    sess.close()
    return TIT, JOB, DOM, set(clean_list(EDU)), set(clean_list(WRK)), SOC, AWD, PAT, PRJ,AFF

def extract_one_3(text):
    text = clean_text(text).strip()
    if len(text) == 0:
        return
    tag2label = {"O": 0,
             "B-PER": 1, "I-PER": 2,
             "B-ADR": 3, "I-ADR": 4,
             "B-AFF": 5, "I-AFF": 6,
             }
    ckpt_file = tf.train.latest_checkpoint(MODEL3_PATH)
    paths['model_path'] = ckpt_file
    model = Original_model(args, embeddings, tag2label, word2id, paths, config=config)
    model.build_graph()
    saver = tf.train.Saver()
    # sess2 = tf.Session(config=config)
    # with sess2.as_default():
    with tf.Session(config=config) as sess2:
        tf.get_variable_scope().reuse_variables()
        saver.restore(sess2, ckpt_file)
        
        demo_sent = list(text)
        demo_data = [(demo_sent, ['O'] * len(demo_sent))]
        tag = model.demo(sess2, demo_data, tag2label)

        PER = get_name_entitry('PER', tag, demo_sent)
        ADR = get_name_entitry('ADR', tag, demo_sent)
        AFF = get_name_entitry('AFF', tag, demo_sent)
        return clean_list(PER), clean_list(ADR), clean_list(AFF)


def extract_project(text):
    text = clean_text(text).strip()
    if len(text) == 0:
        return
    tag2label = {"O": 0,
                 # "B-PER": 'A', "I-PER": 'a',
                 # "B-ADR": 'B', "I-ADR": 'b',
                 # "B-AFF": 'C', "I-AFF": 'c',
                 "B-CAT": 1, "I-CAT": 2,
                 "B-TITLE": 3, "I-TITLE": 4
                 }
    ckpt_file = tf.train.latest_checkpoint(MODEL_PROJECT_PATH)
    paths['model_path'] = ckpt_file
    model = BiLSTM_CRF(args, embeddings, tag2label, word2id, paths, config=config)
    model.build_graph()
    saver = tf.train.Saver()
    # sess2 = tf.Session(config=config)
    # with sess2.as_default():
    with tf.Session(config=config) as sess3:
        tf.get_variable_scope().reuse_variables()
        saver.restore(sess3, ckpt_file)

        demo_sent = list(text)
        demo_data = [(demo_sent, ['O'] * len(demo_sent))]
        tag = model.demo(sess3, demo_data, tag2label)

        CAT = get_name_entitry('CAT', tag, demo_sent)
        TITLE = get_name_entitry('TITLE', tag, demo_sent)
        return clean_list(CAT), clean_list(TITLE)

def extract_patent(text):
    text = clean_text(text).strip()
    if len(text) == 0:
        return
    tag2label = {"O": 0,
                 # "B-PER": 'A', "I-PER": 'a',
                 # "B-ADR": 'B', "I-ADR": 'b',
                 # "B-AFF": 'C', "I-AFF": 'c',
                 "B-NAME": 1, "I-NAME": 2,
                 }
    ckpt_file = tf.train.latest_checkpoint(MODEL_PATENT_PATH)
    paths['model_path'] = ckpt_file
    model = BiLSTM_CRF(args, embeddings, tag2label, word2id, paths, config=config)
    model.build_graph()
    saver = tf.train.Saver()
    # sess2 = tf.Session(config=config)
    # with sess2.as_default():
    with tf.Session(config=config) as sess3:
        tf.get_variable_scope().reuse_variables()
        saver.restore(sess3, ckpt_file)

        demo_sent = list(text)
        demo_data = [(demo_sent, ['O'] * len(demo_sent))]
        tag = model.demo(sess3, demo_data, tag2label)

        name = get_name_entitry('NAME', tag, demo_sent)
        return clean_list(name)

def extract_award(text):
    text = clean_text(text).strip()
    if len(text) == 0:
        return
    tag2label = {"O": 0,
                 # "B-PER": 'A', "I-PER": 'a',
                 # "B-ADR": 'B', "I-ADR": 'b',
                 # "B-AFF": 'C', "I-AFF": 'c',
                 "B-TITLE": 1, "I-TITLE": 2,
                 "B-NAME": 3, "I-NAME": 4
                 }
    ckpt_file = tf.train.latest_checkpoint(MODEL_AWARD_PATH)
    paths['model_path'] = ckpt_file
    model = BiLSTM_CRF(args, embeddings, tag2label, word2id, paths, config=config)
    model.build_graph()
    saver = tf.train.Saver()
    # sess2 = tf.Session(config=config)
    # with sess2.as_default():
    with tf.Session(config=config) as sess3:
        tf.get_variable_scope().reuse_variables()
        saver.restore(sess3, ckpt_file)

        demo_sent = list(text)
        demo_data = [(demo_sent, ['O'] * len(demo_sent))]
        tag = model.demo(sess3, demo_data, tag2label)

        award_name = get_name_entitry('NAME', tag, demo_sent)
        award_title = get_name_entitry('TITLE', tag, demo_sent)
        return clean_list(award_title),clean_list(award_name)

def interface(text):
    tf.reset_default_graph()
    result=extract_one(text)
    TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ,AFF= result if result is not None else (None,None,None,None,None,None,None,None,None,None)
    tf.reset_default_graph()
    result=extract_one_3(text)
    PER, ADR, AFF2 = result if result is not None else (None,None,None)
    if PER is not None:
        print_tag(PER, 'PER', text)
    if ADR is not None:
        print_tag(ADR, 'ADR', text)
    if AFF is not None:
        print_tag(AFF, 'AFF', text)
    if TIT is not None:
        print_tag(TIT, 'TIT', text)
    if JOB is not None:
        print_tag(JOB, 'JOB', text)
    if DOM is not None:
        print_tag(DOM, 'DOM', text)
    if EDU is not None:
        print_tag(EDU, 'EDU', text)
    if WRK is not None:
        print_tag(WRK, 'WRK', text)
    if SOC is not None:
        print_tag(SOC, 'SOC', text)
    if AWD is not None:
        print_tag(AWD, 'AWD', text)
    if PAT is not None:
        print_tag(PAT, 'PAT', text)
    if PRJ is not None:
        print_tag(PRJ, 'PRJ', text)
    
    return PER, ADR, AFF, TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ
    
#interface("(1)\n\r2014年度江西省科技进步二等奖，西杂牛乳加工的关键技术与应用，名列第一\n\r(2)\n\r2008年度教育部科技进步二等奖，新型乳制品加工关键技术集成创新与新产品开发，名列第四\n\r(3)\n\r2012年度江西省自然科学二等奖，纳米气泡及其与蛋白分子相互作用研究，名列第四(4)\n\r2001年度江西省技术发明二等奖，特异性鸡卵黄免疫球蛋白的研制，名列第三(5)\n\r1998年度江西省科技进步三等奖，水洗即食粉，名列第五(6)\n\r2008年度中国商业联合会科技进步二等奖，乳制品")

