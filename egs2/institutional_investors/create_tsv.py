import os
import opencc
import random

from tqdm import tqdm
from utils.datapre import read_file
from utils.datapre import write_file

from utils.normalize_zh import TextNorm

import re
import jieba

def check_is_english(word):
    if re.search("[\u4e00-\u9FFF]", word) == None:
        return True
    return False

def word_to_sentence(sentences):
    words = jieba.lcut(sentences, cut_all=True)
    sentence = ""
    for i in range(len(words)):
        word = words[i]
        if word.replace(' ', '') == '':
            continue
        if not check_is_english(word):
            if (i + 1) < len(words):
                sentence += (" ".join(word) + " ")
            else:
                sentence += " ".join(word)
        # if check_is_english(word):
        #     sentence += word
        #     if (i + 1) < len(words) and check_is_english(words[i + 1]):
        #         sentence += " "
        # else:
        #     sentence += word
        elif (i + 1) < len(words):
            sentence += f'{word.lower()} '
        else:
            sentence += f'{word.lower()}'
    return sentence

converter = opencc.OpenCC('s2t')

def main(root_path, output_path, split_rate=[0.7, 0.2, 0.1]):
    wavscp_path  = root_path
    wavscp_datas = read_file(wavscp_path, sp='\t')
    normalizer   = TextNorm()
    _datas = {}
    for data in tqdm(wavscp_datas):
        _, _, path, text = data
        utt = (((path.split('/'))[-1]).split('.')[0]).replace('-', '_')
        spk = utt
        text = normalizer(text)
        # text = text.replace(' ', '')
        text = converter.convert(text)
        text = word_to_sentence(text)
        _datas[utt] = [utt, spk, text, path]

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
    root_path   = '/share/nas165/amian/experiments/speech/dataengine/dump/2023_04_10__20_59_43/institutional_investors_dataset.txt'
    output_path = './egs2/institutional_investors/tsv'

    main(root_path, output_path)
    # sent = word_to_sentence("那Agenova Healthcare我們希望未來能持續在臺灣的醫療市場做更衣外我們還會極力的推往美洲的市場我們期許有更多的合作夥伴能加入我們然後讓我們")
    # print(sent)