import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import tensorflow as tf
import numpy as np
import os, argparse, time, random
from EItools.extract.model import BiLSTM_CRF
from EItools.extract.get_entity_util import str2bool, get_logger, get_entity, get_award_entity, get_social_entity, \
    get_work_entity, get_project_entity
from EItools.extract.data import read_corpus, read_dictionary, tag2label, random_embedding


## Session configuration
# os.environ['CUDA_VISIBLE_DEVICES'] = '0'
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # default: 0
config = tf.ConfigProto()
# config.gpu_options.allow_growth = True
# config.gpu_options.per_process_gpu_memory_fraction = 0.2  # need ~700MB GPU memory


## hyperparameters
parser = argparse.ArgumentParser(description='BiLSTM-CRF for Chinese NER task')
parser.add_argument('--train_data', type=str, default='data_path', help='train data source')
parser.add_argument('--test_data', type=str, default='data_path', help='test data source')
parser.add_argument('--batch_size', type=int, default=16, help='#sample of each minibatch')
parser.add_argument('--epoch', type=int, default=200, help='#epoch of training')
parser.add_argument('--hidden_dim', type=int, default=300, help='#dim of hidden state')
parser.add_argument('--optimizer', type=str, default='Adam', help='Adam/Adadelta/Adagrad/RMSProp/Momentum/SGD')
parser.add_argument('--CRF', type=str2bool, default=True, help='use CRF at the top layer. if False, use Softmax')
parser.add_argument('--lr', type=float, default=0.001, help='learning rate')
parser.add_argument('--clip', type=float, default=5.0, help='gradient clipping')
parser.add_argument('--dropout', type=float, default=0.5, help='dropout keep_prob')
parser.add_argument('--update_embedding', type=str2bool, default=True, help='update embedding during training')
parser.add_argument('--pretrain_embedding', type=str, default='random', help='use pretrained char embedding or init it randomly')
parser.add_argument('--embedding_dim', type=int, default=300, help='random init char embedding_dim')
parser.add_argument('--shuffle', type=str2bool, default=True, help='shuffle training data before each epoch')
parser.add_argument('--mode', type=str, default='test', help='train/test/demo')
parser.add_argument('--demo_model', type=str, default='1535130886', help='model for test and demo')
args = parser.parse_args()

path=os.path.dirname(os.path.abspath(__file__))

## get char embeddings
word2id = read_dictionary(os.path.join(path, args.train_data, 'word2id.pkl'))
if args.pretrain_embedding == 'random':
    embeddings = random_embedding(word2id, args.embedding_dim)
else:
    embedding_path = 'pretrain_embedding.npy'
    embeddings = np.array(np.load(embedding_path), dtype='float32')

print(args.mode)
## read corpus and get training data
if args.mode != 'demo':
    train_path = os.path.join(path, args.train_data, 'train_data_award_title')
    test_path = os.path.join(path, args.test_data, 'test_data1')
    train_data = read_corpus(train_path)
    test_data = read_corpus(test_path); test_size = len(test_data)
    print('read data:', len(train_data), train_path)
    # train_data = train_data[:64*2]


## paths setting
paths = {}
timestamp = str(int(time.time())) if args.mode == 'train' else args.demo_model
restore_path = os.path.join('.', args.train_data+"_save", args.demo_model, "checkpoints/")
paths['restore_path'] = restore_path
output_path = os.path.join('.', args.train_data+"_save", timestamp)
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


## training model
if args.mode == 'train':
    ckpt_file = tf.train.latest_checkpoint(restore_path)
    paths['restore_path'] = ckpt_file
    model = BiLSTM_CRF(args, embeddings, tag2label, word2id, paths, config=config)
    model.build_graph()

    ## hyperparameters-tuning, split train/dev
    # dev_data = train_data[:5000]; dev_size = len(dev_data)
    # train_data = train_data[5000:]; train_size = len(train_data)
    # print("train data: {0}\ndev data: {1}".format(train_size, dev_size))
    # model.train(train=train_data, dev=dev_data)

    ## train model on the whole training data
    # print(train)
    print("train data: {}".format(len(train_data)))
    model.train(train=train_data, dev=test_data)  # use test_data as the dev_data to see overfitting phenomena

## testing model
elif args.mode == 'test':
    ckpt_file = tf.train.latest_checkpoint(model_path)
    print(ckpt_file)
    paths['model_path'] = ckpt_file
    model = BiLSTM_CRF(args, embeddings, tag2label, word2id, paths, config=config)
    model.build_graph()
    print("test data: {}".format(test_size))
    model.test(test_data)

## demo
elif args.mode == 'demo':
    ckpt_file = tf.train.latest_checkpoint(model_path)
    print(ckpt_file)
    paths['model_path'] = ckpt_file
    model = BiLSTM_CRF(args, embeddings, tag2label, word2id, paths, config=config)
    model.build_graph()
    saver = tf.train.Saver()
    with tf.Session(config=config) as sess:
        print('============= demo =============')
        saver.restore(sess, ckpt_file)
        while(1):
            print('Please input your sentence:')
            demo_sent = input()
            if demo_sent == '' or demo_sent.isspace():
                print('See you next time!')
                break
            else:
                demo_sent = list(demo_sent.strip())
                demo_data = [(demo_sent, ['O'] * len(demo_sent))]
                tag = model.demo_one(sess, demo_data)
                # print(tag)
            #TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ = get_entity(tag, demo_sent)
            # print('PER: {}\nADR: {}\nAFF: {}\nTIT: {}\nJOB: {}\nDOM: {}\nEDU: {}\nWRK: {}\nSOC: {}\nAWD: {}\nPAT: {}\nPRJ: {}\n'.format(PER, ADR, AFF, TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ))
            #print('TIT: {}\nJOB: {}\nDOM: {}\nEDU: {}\nWRK: {}\nSOC: {}\nAWD: {}\nPAT: {}\nPRJ: {}\n'.format(TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ))
            print(get_project_entity(tag,demo_sent))