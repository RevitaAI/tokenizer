import sys
import io
import argparse

import numpy as np
import pickle
from keras.models import load_model


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
    else:
        if current_sent:
            write_conllu(current_sent,f)


def make_data_matrix(x, width = 150, vocab=None):

    x_strides = []
    y_1_str = []
    y_2_str = []

    for idx in range(0,len(x), width):
        x_strides.append(x[idx:idx+width])

    #Build vocab
    if vocab == None:
        #
        vocab = {'<mask>': 0.0}

    #Update vocab
    '''
    for k in x:
        if k not in vocab.keys():
            #
            vocab[k] = len(vocab)
    '''

    #Let's build 
    xnp = np.zeros((len(x_strides), width))

    ##
    for a, line in enumerate(x_strides):
        for b, char in enumerate(line):
            #
            xnp[a][b] = vocab[x_strides[a][b]]


    return xnp


    
