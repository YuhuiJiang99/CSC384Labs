# The tagger.py starter code for CSC384 A4.
import os
import sys

import numpy as np
from collections import Counter

from numpy.lib.function_base import blackman

UNIVERSAL_TAGS = [
    "VERB",
    "NOUN",
    "PRON",
    "ADJ",
    "ADV",
    "ADP", #on, in, at
    "CONJ", #and
    "DET", #a, the
    "NUM",
    "PRT",
    "X",
    ".",
]

N_tags = len(UNIVERSAL_TAGS)

tag2count = dict()

def read_data_train(path):
    return [tuple(line.split(' : ')) for line in open(path, 'r').read().split('\n')[:-1]]

def read_data_test(path):
    return open(path, 'r').read().split('\n')[:-1]

def read_data_ind(path):
    return [int(line) for line in open(path, 'r').read().split('\n')[:-1]]

def write_results(path, results):
    with open(path, 'w') as f:
        f.write('\n'.join(results))

def train_HMM(train_file_name):
    """
    Estimate HMM parameters from the provided training data.

    Input: Name of the training files. Two files are provided to you:
            - file_name.txt: Each line contains a pair of word and its Part-of-Speech (POS) tag
            - fila_name.ind: The i'th line contains an integer denoting the starting index of the i'th sentence in the text-POS data above

    Output: Three pieces of HMM parameters stored in LOG PROBABILITIES :
 
            - prior:        - An array of size N_tags
                            - Each entry corresponds to the prior log probability of seeing the i'th tag in UNIVERSAL_TAGS at the beginning of a sequence
                            - i.e. prior[i] = log P(tag_i)

            - transition:   - transition 2D-array of size (N_tags, N_tags)
                            - The (i,j)'th entry stores the log probablity of seeing the j'th tag given it is a transition coming from the i'th tag in UNIVERSAL_TAGS
                            - i.e. transition[i, j] = log P(tag_j|tag_i)

            - emission:     - transition dictionary type containing tuples of (str, str) as keys
                            - Each key in the dictionary refers to a (TAG, WORD) pair
                            - The TAG must be an element of UNIVERSAL_TAGS, however the WORD can be anything that appears in the training data
                            - The value corresponding to the (TAG, WORD) key pair is the log probability of observing WORD given a TAG
                            - i.e. emission[(tag, word)] = log P(word|tag)
                            - If a particular (TAG, WORD) pair has never appeared in the training data, then the key (TAG, WORD) should not exist.

    Hints: 1. Think about what should be done when you encounter those unseen emission entries during deccoding.
           2. You may find Python's builtin Counter object to be particularly useful 
    """
    pos_data = read_data_train(train_file_name+'.txt')
    sent_inds = read_data_ind(train_file_name+'.ind')
    ####################
    # STUDENT CODE HERE
    ####################  
    sent_inds = set(sent_inds)
    prior = [0.1**10]*N_tags #Put a extremely small number for each position
    transition = []
    emission = dict()
    tag2idx = dict()
    global tag2count
    #initialize the tag2idx dict
    for i in range(N_tags):
        tag2idx[UNIVERSAL_TAGS[i]] = i
    #initialize the transition table
    for i in range(N_tags):
        transition.append([0]*N_tags)
    #traverse the pos_data and fill in different tables
    count = 0
    for i in range(0, len(pos_data)):
        word = pos_data[i][0]
        tag = pos_data[i][1]
        idx = tag2idx[tag]
        if tag in tag2count:
            tag2count[tag] += 1
        else:
            tag2count[tag] = 1
        #add to prior table
        if i in sent_inds :
            count += 1
            prior[idx] += 1

        #add to emission table
        
        if (tag, word) in emission:
            emission[(tag, word)] += 1
        else:
            emission[(tag, word)] = 1
            
        #add to transition table
        if i < len(pos_data)-1:
            if i+1 not in sent_inds:
                nextTag = pos_data[i+1][1]
                nextIdx = tag2idx[nextTag]
                transition[idx][nextIdx] += 1

    #set up the prior, transition, emission tables
    prior = [c/len(sent_inds) for c in prior]
    for i in range(N_tags):
        rowSum = sum(transition[i]) 
        for j in range(N_tags):
            transition[i][j] = transition[i][j]/rowSum
    for k in emission.keys():
        emission[k] = np.log(emission[k]/tag2count[k[0]])

    prior = np.log(prior)
    transition = np.log(transition)
    return prior, transition, emission
    
def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """
    results = []
    prior, transition, emission = train_HMM(train_file_name)
    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')
    ####################
    # STUDENT CODE HERE
    ####################
    for i in range(len(sent_inds)):
        start = sent_inds[i]
        if i < len(sent_inds)-1:
            end = sent_inds[i+1]
        else:
            end = len(pos_data)
        prob_trellis, path_trellis = viterbi(pos_data[start:end], UNIVERSAL_TAGS, prior, transition, emission)
        max_row = np.argmax(prob_trellis[:, -1])
        path = path_trellis[max_row][-1]
        results += path
    write_results(test_file_name+'.pred', results)

def viterbi(words, tags, prior, transition, emission):
    prob_trellis = np.zeros([len(tags), len(words)])
    path_trellis = np.empty([len(tags), len(words)], dtype=object)
    for t in range(len(tags)):
        if (tags[t], words[0]) not in emission:
            emission[(tags[t], words[0])] = np.log(0.1**10)
        prob_trellis[t,0] = prior[t] + emission[(tags[t], words[0])]
        path_trellis[t,0] = [tags[t]]
    for w in range(1, len(words)):
        for t in range(len(tags)):
            if (tags[t],words[w]) not in emission:
                emission[(tags[t],words[w])] = np.log(0.1**10)
            x = np.argmax(prob_trellis[:, w-1] + transition[:, t])
            prob_trellis[t,w] = prob_trellis[x, w-1] + transition[x,t] + emission[(tags[t],words[w])] 
            path_trellis[t,w] = path_trellis[x, w-1] + [tags[t]]
    return prob_trellis, path_trellis


if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    parameters = sys.argv
    train_file_name = parameters[parameters.index("-d")+1]
    test_file_name = parameters[parameters.index("-t")+1]

    # Start the training and tagging operation.
    tag(train_file_name, test_file_name)
