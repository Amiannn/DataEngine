import os
import re
import opencc
import jieba

from tqdm import tqdm
from utils.datapre import read_file
from utils.datapre import read_json
from utils.datapre import write_file
from utils.datapre import main as main_datapre

from utils.normalize_zh import TextNorm

converter = opencc.OpenCC('s2t')

OUTPUT_TSV_PATH   = "./egs2_combine/common_voice+fsw+insitutional_investors/tsv"
OUTPUT_DATA_PATH  = "./egs2_combine/common_voice+fsw+insitutional_investors/data"
OUTPUT_TOKEN_PATH = "./egs2_combine/common_voice+fsw+insitutional_investors/tokens"
DATAMAP_PATH      = './egs2_combine/common_voice+fsw+insitutional_investors/datamap.json'

def combine(datas):
    dataset = []
    for data in datas:
        dataset.extend(data)
    return dataset

def minus(datas_a, datas_b):
    filter_utts = [d[0] for d in datas_b]

    datas = []
    for data in datas_a:
        utt = data[0]
        if utt not in filter_utts:
            datas.append(data)
        else:
            print(f'filter out: {utt}')
    return datas

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def check_is_english(word):
    if re.search("[\u4e00-\u9FFF]", word) == None:
        return True
    return False

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
        elif (i + 1) < len(words):
            sentence += f'{word.lower()} '
        else:
            sentence += f'{word.lower()}'
    return sentence

if __name__ == '__main__':

    datasets     = read_json(DATAMAP_PATH)
    normalizer   = TextNorm()

    zh_token_dict = {}
    en_word_list  = []

    # create tsv
    dataset_info = []
    for index, dataset_type in enumerate(datasets):
        add_datas   = []
        minus_datas = []

        for datas in datasets[dataset_type]:
            dataset_name, operate, path = datas
            if operate == 'add':
                add_datas.append([[f'{dataset_name}-{d[0]}', *d[1:]] for d in read_file(path)])
            elif operate == 'minus':
                minus_datas.append([[f'{dataset_name}-{d[0]}', *d[1:]] for d in read_file(path)])
        
        add_datas   = sorted(combine(add_datas))
        minus_datas = sorted(combine(minus_datas))

        datas = minus(add_datas, minus_datas)

        # normalize and remove too short utterance
        print('normalize...')
        normalized_datas = []
        for i in tqdm(range(len(datas))):
            utt, spk, text, path = datas[i]
            # text = text.replace(' ', '')
            text = normalizer(text)
            # text = text.replace(' ', '')
            text = converter.convert(text)
            if len(text) < 5: 
                continue
            text = word_to_sentence(text)
            eng_words, zh_words = filter_out_english(text.split(' '))
            if len(eng_words) > 0:
                en_word_list.append(eng_words)
            if len(zh_words) > 0:
                for t in zh_words:
                    zh_token_dict[t] = zh_token_dict[t] + 1 if t in zh_token_dict else 1
            utt = utt.replace('_', '-')
            # spk -> utt
            normalized_datas.append([utt, utt, text, path])

        datas = normalized_datas
        out_path = os.path.join(OUTPUT_TSV_PATH, f'{dataset_type}.tsv')
        write_file(datas, out_path)
        dataset_info.append([dataset_type, out_path])

        # if dataset_type == 'test':
        sub_dataset = {}
        for data in datas:
            dataset_name = data[0].split('-')[0]
            sub_dataset[dataset_name] = sub_dataset[dataset_name] + [data] if dataset_name in sub_dataset else [data]
        for dataset_name in sub_dataset:
            out_path = os.path.join(OUTPUT_TSV_PATH, f'{dataset_type}_{dataset_name}.tsv')
            write_file(sub_dataset[dataset_name], out_path)
            dataset_info.append([f'{dataset_type}_{dataset_name}', out_path])
    
    zh_token_list = [[zh_token_dict[token], token] for token in zh_token_dict]
    zh_token_list = sorted(zh_token_list, reverse=True)
    zh_token_list = [[token] for count, token in zh_token_list]
    # zh_token_list = [['<blank>'], ['<unk>']] + zh_token_list + [['<sos/eos>']]
    # zh_token_list = [['<blank>'], ['<unk>']] + zh_token_list
    zh_token_list = zh_token_list

    out_path = os.path.join(OUTPUT_TOKEN_PATH, f'token.man.1')
    write_file(zh_token_list, out_path)

    out_path = os.path.join(OUTPUT_TOKEN_PATH, f'text.eng.bpe')
    write_file(en_word_list, out_path, sp=" ")
    
    # create files
    for dataset_name, path in dataset_info:
        in_path  = path
        out_path = os.path.join(OUTPUT_DATA_PATH, f'{dataset_name}')
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        main_datapre(in_path, out_path)