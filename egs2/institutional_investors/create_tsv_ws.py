import os
import opencc
import random

from tqdm import tqdm
from utils.datapre import read_file
from utils.datapre import write_file

from utils.normalize_zh import TextNorm

import re
import jieba

from ckip_transformers.nlp import CkipWordSegmenter

ws_driver  = CkipWordSegmenter(model="bert-base", device=0)

OUTPUT_TOKEN_PATH = "./egs2/institutional_investors/tokens_ws"

def check_is_english(word):
    if re.search("[\u4e00-\u9FFF]", word) == None:
        return True
    return False

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def word_to_sentence(sentences):
    words    = ws_driver([sentences], use_delim=True)[0]
    sentence = ""
    for i in range(len(words)):
        word = words[i]
        if word.replace(' ', '') == '':
            continue
        if not check_is_english(word):
            if (i + 1) < len(words):
                sentence += (word + " ")
            else:
                sentence += word
        elif (i + 1) < len(words):
            sentence += f'{word.lower()} '
        else:
            sentence += f'{word.lower()}'
    sentence = sentence.replace('  ', ' ').lower()
    return sentence

def filter_out_english(words):
    engs = []
    zhs  = []
    for word in words:
        if word.replace(' ', '') == '':
            continue
        if isEnglish(word):
            engs.append(word)
        else:
            zhs.append(word)
    return engs, zhs

converter = opencc.OpenCC('s2t')

def main(root_path, output_path, split_rate=[0.7, 0.2, 0.1]):
    wavscp_path  = root_path
    wavscp_datas = read_file(wavscp_path, sp='\t')
    normalizer   = TextNorm()
    _datas  = {}
    dataset = []
    for data in tqdm(wavscp_datas):
        _, _, path, text = data
        utt = (((path.split('/'))[-1]).split('.')[0]).replace('-', '_')
        spk = utt
        if text == '' or len(text) <= 5:
            continue
        text = converter.convert(text)
        text = normalizer(text)
        text = word_to_sentence(text)
        words = " ".join(text.split()).split()
        if len(words) < 5:
            continue
        _path = path.replace(
            "/share/nas165/amian/experiments/speech/dataengine", 
            "/share/nas165/amian/experiments/speech/preprocess/dataengine"
        )
        _datas[utt] = [utt, spk, text, _path]
        dataset.append(_datas[utt])
    
    zh_token_dict = {}
    en_word_list  = []
    zh_sentences  = []
    for uid, _, text, _ in dataset:
        eng_words, zh_words = filter_out_english(text.split(' '))
        if len(eng_words) > 0:
            en_word_list.append(eng_words)
        if len(zh_words) > 0:
            zh_sentences.append(zh_words)
            for t in zh_words:
                zh_token_dict[t] = zh_token_dict[t] + 1 if t in zh_token_dict else 1

    zh_token_list = [[zh_token_dict[token], token] for token in zh_token_dict]
    zh_token_list = sorted(zh_token_list, reverse=True)
    zh_token_list = [[token] for count, token in zh_token_list]
    
    out_path = os.path.join(OUTPUT_TOKEN_PATH, f'token.man.1')
    write_file(zh_token_list, out_path)

    out_path = os.path.join(OUTPUT_TOKEN_PATH, f'token.train')
    write_file(zh_sentences, out_path, sp=" ")

    out_path = os.path.join(OUTPUT_TOKEN_PATH, f'text.eng.bpe')
    write_file(en_word_list, out_path, sp=" ")

    datas = [_datas[key] for key in _datas]

    random.shuffle(datas)
    train_set_length = int(len(datas) * split_rate[0])
    test_set_length  = int(len(datas) * split_rate[1])

    train_datas = datas[:train_set_length]
    test_datas  = datas[train_set_length:train_set_length + test_set_length]
    dev_datas   = datas[train_set_length + test_set_length:]

    train_output_path = os.path.join(output_path, 'train.tsv')
    write_file(train_datas, train_output_path)

    dev_output_path = os.path.join(output_path, 'dev.tsv')
    write_file(dev_datas, dev_output_path)

    test_output_path = os.path.join(output_path, 'test.tsv')
    write_file(test_datas, test_output_path)

if __name__ == '__main__':
    root_path   = '/share/nas165/amian/experiments/speech/preprocess/dataengine/dump/2023_04_10__20_59_43/institutional_investors_dataset.txt'
    output_path = './egs2/institutional_investors/tsv_ws'

    main(root_path, output_path)