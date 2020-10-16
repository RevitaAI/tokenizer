import argparse
import numpy as np
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
from tensorflow.keras.utils import to_categorical
import tensorflow.keras
import sys
import pickle
import os
# - load_conllu(file)
#   - loads CoNLL-U file from given file object to an internal representation
#   - the file object should return str on both Python 2 and Python 3
#   - raises UDError exception if the given file cannot be loaded
# - evaluate(gold_ud, system_ud)

from conll18_ud_eval import load_conllu, evaluate




#Todos:

    ## Inputs

    # conllu -> data_matrix [x]
    # tag -> data_matrix

    ### Outputs

    # dm -> conllu
    # dm -> tag


'''

7	Helsingissä	Helsinki	PROPN	N	Case=Ine|Number=Sing	3	obl	_	SpaceAfter=No
8	.	.	PUNCT	Punct	_	3	punct	_	_



LSTM


s, validate on 4788 samples
Epoch 1/20
2018-05-12 20:41:11.907163: I tensorflow/core/platform/cpu_feature_guard.cc:140] Your CPU supports instructions that this TensorFlow binary was not compiled to use: FMA
19150/19150 [==============================] - 30s 2ms/step - loss: 0.2640 - val_loss: 0.2294
Epoch 2/20
19150/19150 [==============================] - 30s 2ms/step - loss: 0.2064 - val_loss: 0.2129
Epoch 3/20
19150/19150 [==============================] - 29s 2ms/step - loss: 0.1875 - val_loss: 0.1978
Epoch 4/20
19150/19150 [==============================] - 30s 2ms/step - loss: 0.1687 - val_loss: 0.1852
Epoch 5/20
19150/19150 [==============================] - 29s 2ms/step - loss: 0.1551 - val_loss: 0.1768
Epoch 6/20
19150/19150 [==============================] - 30s 2ms/step - loss: 0.1462 - val_loss: 0.1727
Epoch 7/20
19150/19150 [==============================] - 29s 2ms/step - loss: 0.1400 - val_loss: 0.1655
Epoch 8/20
19150/19150 [==============================] - 29s 2ms/step - loss: 0.1350 - val_loss: 0.1642
Epoch 9/20
19150/19150 [==============================] - 29s 2ms/step - loss: 0.1312 - val_loss: 0.1596
Epoch 10/20
19150/19150 [==============================] - 29s 2ms/step - loss: 0.1279 - val_loss: 0.1590
Epoch 11/20
19150/19150 [==============================] - 29s 2ms/step - loss: 0.1251 - val_loss: 0.1561
Epoch 12/20
19150/19150 [==============================] - 29s 2ms/step - loss: 0.1230 - val_loss: 0.1551
Epoch 13/20
19150/19150 [==============================] - 29s 2ms/step - loss: 0.1207 - val_loss: 0.1546
Epoch 14/20
19150/19150 [==============================] - 29s 2ms/step - loss: 0.1188 - val_loss: 0.1541
Epoch 15/20
19150/19150 [==============================] - 29s 2ms/step - loss: 0.1172 - val_loss: 0.1535
Epoch 16/20
19150/19150 [==============================] - 30s 2ms/step - loss: 0.1155 - val_loss: 0.1521
Epoch 17/20
19150/19150 [==============================] - 30s 2ms/step - loss: 0.1144 - val_loss: 0.1543
Epoch 18/20
19150/19150 [==============================] - 29s 2ms/step - loss: 0.1130 - val_loss: 0.1508
Epoch 19/20
19150/19150 [==============================] - 29s 2ms/step - loss: 0.1116 - val_loss: 0.1508
Epoch 20/20
19150/19150 [==============================] - 29s 2ms/step - loss: 0.1106 - val_loss: 0.1508




'''


class Evalcb(tensorflow.keras.callbacks.Callback):

    def __init__(self, dev_x, dev_y, win=10):

        self.dev_x = dev_x
        self.dev_y = dev_y
        self.win = win
        self.best_loss = 999
        self.best_model = None

    def on_train_begin(self, logs={}):
        self.losses = []

    def on_epoch_end(self, batch, logs={}):
        preds = self.model.predict(self.dev_x)

        all_preds = preds.argmax(-1).flatten()
        all_ys = self.dev_y.argmax(-1).flatten()

        print(classification_report(all_ys, all_preds))
        mid_p = []
        mid_y = []
        win = self.win

        for xx, yy in zip(preds, self.dev_y):

            mid_p.extend(xx[win:-win].argmax(-1).tolist())
            mid_y.extend(yy[win:-win].argmax(-1).tolist())

        print ('mid')
        print(classification_report(mid_y, mid_p))



class BMcb(tensorflow.keras.callbacks.Callback):

    def __init__(self):

        self.best_loss = 999
        self.best_model = None

    def on_train_begin(self, logs={}):
        self.losses = []

    def on_epoch_end(self, batch, logs={}):

        if not self.best_model is None:
            self.best_model = self.model

        if logs.get('val_loss') < self.best_loss:
            self.best_loss = logs.get('val_loss')
            self.best_model = self.model

def data_matrix_to_conllu(x, y, vocab, f=sys.stdout):

    #make a reverse vocabulary
    rev_vocab = {v:k for k,v in vocab.items()}
    out = ''
    cntr = 1

    y = y.argmax(-1)

    current_token = ''
    current_sent = []
    sents = []

    def write_conllu(sent, f):
        
        for i, t in enumerate(sent):
            line = [str(i+1), t.lstrip(' ')]
            line.extend(['_']*7)
            
            if i > 0:
                line[6]='1'
            else:
                line[6]='0'


            if len(sent)-2 > i:
                if sent[i+1] == ' ':
                    line.append('SpaceAfter=False')
                else:
                    line.append('_')
            else:
                line.append('_')
            f.write('\t'.join(line)+'\n')
        f.write('\n')

    for a, line in enumerate(x):
        for b, char in enumerate(line):



            current_token += rev_vocab[x[a][b]]
            
            if y[a][b] == 1.0:
                if len(current_token.lstrip(' ')) > 0:
                    current_sent.append(current_token)
                current_token = ''

            if b > -1 and y[a][b] == 2.0:

                if len(current_token.lstrip(' ')) > 0:
                    current_sent.append(current_token)
                current_token = ''

                write_conllu(current_sent,f)
                current_sent = []
                cntr = 1






    #conllu ver
    #cntr = 0
    #for xx in out.split('\n'):
    #    #
        



    return out

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Embedding, TimeDistributed, Conv1D, Multiply, Dropout
from pandas import Series
from matplotlib import pyplot
from tensorflow.keras.callbacks import TensorBoard
from sklearn.metrics import classification_report


def make_and_train_model(train_x, train_ty, train_sy, vocab, dev_x, dev_ty, dev_sy):

    #input
    input_shape = train_x[0].shape
    a = Input(shape=input_shape)
    bxx = Embedding(len(vocab), 60)(a)


    dr_rate = 0.2
    ww = 5
    conv = True
    for ccc in range(10):

        if conv:
            
            abxx = Conv1D(60, ww, padding='same',activation='relu')(bxx)
            bgxx = Conv1D(60, ww, padding='same',activation='sigmoid')(bxx)
            bxx = Dropout(dr_rate)(Multiply()([abxx, bgxx]))
        #bxx = LSTM(60, return_sequences=True)(bxx)
        else:
            bxx=LSTM(60,return_sequences=True)(bxx)

    out = TimeDistributed(Dense(3,activation='softmax'), input_shape=(50, 60))(bxx)
    model = Model(inputs=a, outputs=out)


    #Compile
    model.compile('adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'], sample_weight_mode='temporal')
    print (train_ty.shape)
    #Train
    eval_x = train_x[-round(train_x.shape[0]*0.2):]
    eval_ty = train_ty[-round(train_x.shape[0]*0.2):]
    eval_cb = Evalcb(eval_x, eval_ty)
    bmcb = BMcb()
    #weights like this:
    #eval_ty.argmax(-1) * 10 + 1

    model.fit(train_x, train_ty, validation_split=0.1, epochs=31, callbacks=[TensorBoard(log_dir='./logs/5_layer_gc'), bmcb])#, sample_weight=train_ty.argmax(-1) * 1 + 1)

    print (bmcb.best_loss)

    dev_p = bmcb.best_model.predict(dev_x)
    #Simple eval
    gold = open('gold.conllu','wt')
    data_matrix_to_conllu(dev_x, dev_ty, vocab, f=gold)
    gold.close()

    gold = open('pred.conllu','wt')
    data_matrix_to_conllu(dev_x, dev_p, vocab, f=gold)
    gold.close()

    return bmcb.best_model   


'''

    eval_x = train_x[-round(train_x.shape[0]*0.2):]
    eval_ty = train_ty[-round(train_x.shape[0]*0.2):]
    preds = model.predict(eval_x)
    mid = False

    all_preds = preds.argmax(-1).flatten()
    all_ys = eval_ty.argmax(-1).flatten()

    print(classification_report(all_ys, all_preds))

    import pdb;pdb.set_trace()
'''



def make_conllu_data(f, corruption=0.0):

    inf = open(f, 'rt')

    X = []
    t_Y = []
    s_Y = []

    l = '# begin'

    for cl in inf:

        if not l.startswith('#') and l != '\n':

            space_after = not (l.split('\t')[9].strip() == 'SpaceAfter=No')
            token = l.split('\t')[1]

            for t in token:
                X.append(t)
                t_Y.append(0)
                s_Y.append(0)

            t_Y[-1] = 1

            if cl == '\n':
                s_Y[-1] = 1

            if space_after:
                X.append(' ')
                t_Y.append(0)
                s_Y.append(0)

        l = cl


    return X, t_Y, s_Y

def make_data_matrix(x, y1, y2, width = 150, vocab=None):

    x_strides = []
    y_1_str = []
    y_2_str = []

    for idx in range(0,len(x), width):
        x_strides.append(x[idx:idx+width])
        y_1_str.append(y1[idx:idx+width])
        y_2_str.append(y2[idx:idx+width])

    #Build vocab
    if vocab == None:
        #
        vocab = {'<mask>': 0.0}

    #Update vocab
    for k in x:
        if k not in vocab.keys():
            #
            vocab[k] = len(vocab)

    #Let's build 
    xnp = np.zeros((len(x_strides), width))
    y1np = np.zeros((len(x_strides), width))
    y2np = np.zeros((len(x_strides), width))

    ##
    for a, line in enumerate(x_strides):
        for b, char in enumerate(line):
            #
            xnp[a][b] = vocab[x_strides[a][b]]
            y1np[a][b] = y_1_str[a][b]
            y2np[a][b] = y_2_str[a][b]      


    return xnp, y1np, y2np, vocab

def train(conllu_train_file, conllu_dev_file, save_path):
    #We read conllu training data
    train_conllu_x, train_conllu_ty, train_conllu_sy = make_conllu_data(conllu_train_file, corruption=0.0)
    dev_conllu_x, dev_conllu_ty, dev_conllu_sy = make_conllu_data(conllu_dev_file, corruption=0.0)

    train_x, train_ty, train_sy, vocab = make_data_matrix(train_conllu_x,train_conllu_ty, train_conllu_sy, vocab=None)
    dev_x, dev_ty, dev_sy, vocab = make_data_matrix(dev_conllu_x,dev_conllu_ty, dev_conllu_sy, vocab=vocab)


    #Let's cut ourselves a dev set
    '''
    dev_x = train_x[-100:]
    dev_ty = train_ty[-100:]
    dev_sy = train_sy[-100:]
    '''

    train_ty += train_sy
    train_ty = to_categorical(train_ty)
    train_sy = to_categorical(train_sy)

    dev_ty += dev_sy
    dev_ty = to_categorical(dev_ty)
    dev_sy = to_categorical(dev_sy)

    ## H A C K XXX
    #xtrain_sy = train_ty
    #xtrain_ty = train_sy
    #train_sy = xtrain_sy
    #train_ty = xtrain_ty


    model = make_and_train_model(train_x, train_ty, train_sy, vocab, dev_x, dev_ty, dev_sy)

    model.save(os.path.join(save_path, 'tokenizer.udpipe'))
    outf = open(os.path.join(save_path, 'vocab.pickle'), 'wb')
    pickle.dump(vocab, outf)
    ouclose()

    #X = []
    #Y = []

    

    '''

    print (data_matrix_to_conllu(train_x, train_ty, vocab))

    print (data_matrix_to_conllu(train_x, train_ty, vocab))
    '''

    #    X.append(conllu_x)
    #    Y.append(conllu_y)
    '''
    for f in tag_files:

        #We read extra data in the tag format
        extra_x, extra_y = make_tag_data(tag_file)        
        X.append(extra_x)
        Y.append(extra_y)

    '''
    #Do eval
    '''
    model, epoch_losses, train_losses = train_model(train_X, train_Y)
    '''

    #Visualize these
    
    #Save the model

#Pomodoro_1: conllu data into np matrices


if __name__=="__main__":
    import argparse
    argparser = argparse.ArgumentParser(description='A script for training new models')
    argparser.add_argument('--save_dir', type=str, required=True, help='Model saving path')
    subparsers = argparser.add_subparsers()
    train_parser = subparsers.add_parser('train')
    train_parser.set_defaults(action="train")
    train_parser.add_argument('--train_file', type=str, required=True, help='Training data file (conllu)')
    train_parser.add_argument('--devel_file', type=str, required=True, help='Development data file (conllu)')
    train_parser.add_argument('--test_file', type=str, default='', help='Testing data file (conllu)')
    
    args = argparser.parse_args()
    
    '''
        conllu_train_file = args.train_file
        conllu_dev_file = args.devel_file
        conllu_test_file = args.test_file
    '''
    #
    #Are you about to train, predict or eval?
    #

    if  args.action == 'train':
        train(args.train_file, args.devel_file, args.save_dir)        