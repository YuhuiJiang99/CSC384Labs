# The tagger.py starter code for CSC384 A4.

import os
import sys
from typing import Collection

import numpy as np
from collections import Counter

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

            - transition:   - A 2D-array of size (N_tags, N_tags)
                            - The (i,j)'th entry stores the log probablity of seeing the j'th tag given it is a transition coming from the i'th tag in UNIVERSAL_TAGS
                            - i.e. transition[i, j] = log P(tag_j|tag_i)

            - emission:     - A dictionary type containing tuples of (str, str) as keys
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
    prior = [0]*N_tags #Put a extremely small number for each position
    transition = []
    emission = dict()
    tag2idx = dict()
    tag2count = dict()
  
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
        if tag in tag2count.keys():
            tag2count[tag] += 1
        else:
            tag2count[tag] = 1
        #add to prior table
        if i in sent_inds :
            count += 1
            prior[idx] += 1

        
        #add to emission table
        if (tag, word) in emission.keys():
            emission[(tag, word)] += 1
        else:
            emission[(tag, word)] = 1
            
        #add to transition table
        if i < len(pos_data)-1:
            nextTag = pos_data[i+1][1]
            nextIdx = tag2idx[nextTag]
            transition[idx][nextIdx] += 1

    #set up the prior, transition, emission tables
    print(tag2count)
    prior = [np.log(c/len(sent_inds)) for c in prior]
    for i in range(N_tags):
        rowSum = sum(transition[i]) 
        rowSum =  tag2count[UNIVERSAL_TAGS[i]]

        for j in range(N_tags):
            if transition[i][j] == 0:
                transition[i][j] = float('-inf')
            else:
                transition[i][j] = np.log(transition[i][j]/rowSum)
    for k in emission.keys():
        emission[k] = np.log(emission[k]/tag2count[k[0]])
    
    

    prior = np.asarray(prior)
    transition = np.asarray(transition)
    return prior, transition, emission
    

def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    ####################
    # STUDENT CODE HERE
    ####################

    write_results(test_file_name+'.pred', results)



if __name__ == '__main__':
    # train_file_name = "./data/train-public"
    # prior, transition, emission = train_HMM(train_file_name)
    # matrix = [[1,2,3],[4,5,6]]
    # for arr in matrix:
    #     print(type(arr))

    # matrix = np.array(matrix)

    # for arr in matrix:
    #     print(type(arr))
    
    # print(matrix[0,1])

        
    an_array = np.array([[0.1, 0.0, 0.3], [0.1, 0.0, 0.1]])
    an_array[an_array==0] = 0.1**10

    # i = np.argmax(an_array, axis=0)[-1]
    # print(an_array[i][-1])

    arr = [1,2,3,4]
    arr2 = [1,2,3,4]
    print(np.argmax(arr))
    print(np.argmax(np.log(arr)))









