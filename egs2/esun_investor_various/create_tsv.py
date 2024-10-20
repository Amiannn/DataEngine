import os
import random
import textgrid

from tqdm import tqdm
from utils.datapre import read_file
from utils.datapre import write_file

from utils.normalize_zh import TextNorm

from ckip_transformers.nlp import CkipWordSegmenter

ws_driver  = CkipWordSegmenter(model="bert-base", device=0)

import re
import jieba

random.seed(0)

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
    # words = jieba.lcut(sentences, cut_all=True)
    words    = ws_driver([sentences], use_delim=True)[0]
    sentence = ""
    for i in range(len(words)):
        word = words[i]
        if word.replace(' ', '') == '':
            continue
        if not check_is_english(word):
            if (i + 1) < len(words):
                # sentence += (" ".join(word) + " ")
                sentence += (word + " ")
            else:
                # sentence += " ".join(word)
                sentence += word
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

wav_root = "/share/nas165/amian/experiments/speech/preprocess/dataset_pre/egs2/esun_investor_various/data/wav_16k"
OUTPUT_TOKEN_PATH = "./egs2/esun_investor_various/tokens_ws"

def main(root_path, output_path):
    dataset = []
    speaker = []
    segment = []
    wavscp  = []
    normalizer = TextNorm()
    for filename in os.listdir(root_path):
        path  = os.path.join(root_path, filename)
        items = textgrid.TextGrid.fromFile(path)
        print(f'path: {path}')
        count = 0
        filename = filename.replace('.TextGrid', '')
        for item in tqdm(items):
            name = item.name.split(' ')[0]
            for intervals in item:
                xmin = intervals.minTime
                xmax = intervals.maxTime
                text = intervals.mark
                if text == '' or len(text) <= 5:
                    continue
                uid = filename
                uid = f'esun{uid}_{count}'
                wav_path = f'{wav_root}/{filename}.wav'
                text = normalizer(text)
                text = word_to_sentence(text)
                
                words = " ".join(text.split()).split()
                if len(words) < 5:
                    continue
                text = " ".join([word for word in words if word != "htr"])
                
                dataset.append([
                    uid, 
                    uid, 
                    text,
                    wav_path
                ])
                speaker.append([
                    name, 
                    uid, 
                    text,
                    wav_path
                ])
                wavscp.append([
                    uid, 
                    wav_path
                ])
                segment.append([
                    uid,
                    str(xmin), 
                    str(xmax), 
                ])
                count += 1

    zh_token_dict = {}
    en_word_list  = []
    testset_years = ['2019', '2020', '2021', '2022']
    zh_sentences  = []
    for uid, _, text, _ in dataset:
        check = len([years for years in testset_years if years in uid]) > 0
        if check:
            continue
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
    # zh_token_list = [['<blank>'], ['<unk>']] + zh_token_list + [['<sos/eos>']]
    # zh_token_list = [['<blank>'], ['<unk>']] + zh_token_list
    zh_token_list = zh_token_list

    # out_path = os.path.join(OUTPUT_TOKEN_PATH, f'token.man.1')
    # write_file(zh_token_list, out_path)

    # out_path = os.path.join(OUTPUT_TOKEN_PATH, f'token.train')
    # write_file(zh_sentences, out_path, sp=" ")

    # out_path = os.path.join(OUTPUT_TOKEN_PATH, f'text.eng.bpe')
    # write_file(en_word_list, out_path, sp=" ")

    # output_dump = os.path.join(output_path, 'all.tsv')
    # write_file(sorted(dataset), output_dump, sp="\t")
    output_dump = os.path.join(output_path, 'speaker.tsv')
    write_file(sorted(speaker), output_dump, sp="\t")
    # output_dump = os.path.join(output_path, 'segments')
    # write_file(sorted(segment), output_dump, sp="\t")
    # output_dump = os.path.join(output_path, 'wav.scp')
    # write_file(sorted(wavscp), output_dump, sp="\t")

if __name__ == '__main__':
    root_path   = './egs2/esun_investor_various/dataset/ESUN-investor_various-mp3-2ch/txt'
    output_path = './egs2/esun_investor_various/tsv_ws'

    main(root_path, output_path)