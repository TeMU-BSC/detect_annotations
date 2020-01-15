#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 18:26:58 2020

@author: antonio
"""

import os
import string
import unicodedata
from shutil import copyfile
import re
import argparse


def Flatten(ul):
    '''
    DESCRIPTION: receives a nested list and returns it flattened
    INPUT: ul: list
    OUTPUT: fl: list'''
    
    fl = []
    for i in ul:
        if type(i) is list:
            fl += Flatten(i)
        else:
            fl += [i]
    return fl

def remove_accents(data):
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.printable)

def copy_dir_structure(input_path_old_files, output_path_new_files):
    '''
    DESCRIPTION: copy folders structure in a new route.
    INPUT: input_path_old_files: str. Directory whose structure I want to replicate
           output_path_new_files: str. Root directory on which I want to re-create
              the sub-folder structure.
    '''
    
    for dirpath, dirnames, filenames in os.walk(input_path_old_files):
        print(dirpath[len(input_path_old_files):])
        structure = os.path.join(output_path_new_files, 
                                 dirpath[len(input_path_old_files):])
        if not os.path.isdir(structure):
            print(structure)
            os.mkdir(structure)
        else:
            print("Folder does already exist!")
            
def copy_all_files(input_path_old_files, output_path_new_files):
    '''
    DESCRIPTION: copy files from one directory to another. It respects folder 
        structure.
    INPUT: input_path_old_files: str. Source directory.
           output_path_new_files: str. Target directory.
    '''
    
    for root, dirs, files in os.walk(input_path_old_files):
        for filename in files:
            copyfile(os.path.join(root,filename), 
                     os.path.join(output_path_new_files,
                                  root[len(input_path_old_files):],
                                  filename))
            
            
def adjacent_combs(text, tokens2pos, n_words):
    '''
    DESCRIPTION: obtain all token combinations in a text. The maximum number
    of tokens in a combination is given by n_words.
    For example: text = 'buenos días míster jones', n_words = 3.
    output: [buenos, buenos días, buenos días míster, días, días míster, 
    días míster jones, míster, míster jones, jones]
    
    INPUT: text: str. String with full text
           tokens2pos: python dict relating every token with its position in 
                  text. {tokens: (start, end)}
           n_words: maximum number of tokens in a combination
    
    OUTPUT: id2token_span: python dict relating every token combination with an ID.
            id2token_span_pos: python dict relating every token combination
                  (identified by an ID) with its position in the text.
            token_spans: list of token combinations.'''
    
    tokens = []
    for m in re.finditer(r'\S+', text):
        if all([i in string.punctuation for i in m.group()])==False:
            tokens.append(m.group())
    tokens_trim = list(map(lambda x: x.strip(string.punctuation), tokens))
    id2token_span = {}
    id2token_span_pos = {}
    count = 0
    
    for a in range(0, len(tokens_trim)+1):
        for b in range(a+1, min(a + 1 + n_words, len(tokens_trim)+1)):
            count = count + 1

            tokens_group = tokens_trim[a:b] # Extract token group
            tokens_group = list(filter(None, tokens_group)) # remove empty elements
            
            if tokens_group:
                id2token_span[count] = tokens_group

                # Extract previous token
                token_prev = '' 
                if a>0:
                    c = 1
                    token_prev = tokens_trim[a-c:a][0]
                    # If token_prev is an empty space, it may be because there
                    # where a double empty space in the original text
                    while (token_prev == '') & (a>1):
                        c = c+1
                        token_prev = tokens_trim[a-c:a][0]
                
                # Extract start and end positions
                if len(tokens_group) == 1:
                    pos = list(filter(lambda x: x[2] == token_prev, 
                                      tokens2pos[tokens_group[0]]))
                    beg_pos = pos[0][0]
                    end_pos = pos[0][1]
                else:
                    beg = list(filter(lambda x: x[2] == token_prev, 
                                      tokens2pos[tokens_group[0]]))
                    end = list(filter(lambda x: x[2] == tokens_group[-2], 
                                      tokens2pos[tokens_group[-1]]))
                    beg_pos = beg[0][0]
                    end_pos = end[0][1]
                    
                id2token_span_pos[count] = (beg_pos, end_pos) 

    token_spans = list(map(lambda x: ' '.join(x), id2token_span.values()))
    
    return id2token_span, id2token_span_pos, token_spans


def argparser():
    '''
    DESCRIPTION: Parse command line arguments
    '''
    
    parser = argparse.ArgumentParser(description='process user given parameters')
    parser.add_argument("-i", "--input-brat", required = True, dest = "datapath", 
                        help = "absolute path to original input brat files")
    parser.add_argument("-o", "--output-brat", required =  True, 
                        dest="output_path_new_files", 
                        help = "absolute path to output brat files")
    parser.add_argument("-O", "--output_tsv", required = True, dest = "output_path_df", 
                        help = "absolute path to output TSV")
    
    args = parser.parse_args()
    
    datapath = args.datapath
    input_path_old_files = datapath
    output_path_new_files = args.output_path_new_files
    output_path_df = args.output_path_df
    
    return datapath, input_path_old_files, output_path_new_files, output_path_df


def strip_punct(m_end, m_start, m_group, exit_bool):
    '''
    DESCRIPTION: remove recursively final and initial punctuation from 
              string and update start and end position.
    
    INPUT: exit_bool: boolean value to tell whether to continue with the 
                      recursivety.
          m_end: int. End position
          m_start: int. Start position
          m_group: string
    
    OUTPUT: exit_bool: boolean value to tell whether to continue with the 
                      recursivety.
          m_end: int. End position
          m_start: int. Start position
          m_group: string
    '''
    
    if m_group[-1] in string.punctuation:
        m_end = m_end - 1
        m_group = m_group[0:-1]
        m_start = m_start
        exit_bool = 0
    elif m_group[0] in string.punctuation:
        m_end = m_end
        m_group = m_group[1:]
        m_start = m_start + 1
        exit_bool = 0
    else: 
        m_end = m_end
        m_group = m_group
        m_start = m_start
        exit_bool = 1
    if exit_bool == 0:
        m_end, m_start, m_group, exit_bool = strip_punct(m_end, m_start, m_group, exit_bool)
        
    return m_end, m_start, m_group, exit_bool


def normalize_str(annot, min_upper):
    '''
    DESCRIPTION: normalize annotation: lowercase, remove extra whitespaces, 
    remove punctuation and remove accents.
    
    INPUT: annot: string
           min_upper: int. Specifies the minimum number of characters of a word
               to lowercase it (to prevent mistakes with acronyms).

    OUTPUT: annot_processed: string
    '''
    # Lowercase
    annot_lower = ' '.join(list(map(lambda x: x.lower() if len(x)>min_upper else x, annot.split(' '))))
    
    # Remove whitespaces
    annot_bs = re.sub('\s+', ' ', annot_lower).strip()

    # Remove punctuation
    annot_punct = annot_bs.translate(str.maketrans('', '', string.punctuation))
    
    # Remove accents
    annot_processed = remove_accents(annot_punct)
    
    return annot_processed