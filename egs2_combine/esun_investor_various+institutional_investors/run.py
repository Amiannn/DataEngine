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

OUTPUT_TSV_PATH   = "./egs2_combine/esun_investor_various+institutional_investors/tsv_ws"
OUTPUT_DATA_PATH  = "./egs2_combine/esun_investor_various+institutional_investors/data_ws"
OUTPUT_TOKEN_PATH = "./egs2_combine/esun_investor_various+institutional_investors/tokens_ws"
DATAMAP_PATH      = './egs2_combine/esun_investor_various+institutional_investors/datamap.json'

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
                add_datas.append([[f'{dataset_name}-{d[0]}', *d[1:]] for d in read_file(path, sp='\t')])
            elif operate == 'minus':
                minus_datas.append([[f'{dataset_name}-{d[0]}', *d[1:]] for d in read_file(path, sp='\t')])

        add_datas   = sorted(combine(add_datas))
        minus_datas = sorted(combine(minus_datas))
        datas       = sorted(minus(add_datas, minus_datas))
        out_path = os.path.join(OUTPUT_TSV_PATH, f'{dataset_type}.tsv')
        write_file(datas, out_path)
        dataset_info.append([dataset_type, out_path])

        sub_dataset = {}
        for data in datas:
            dataset_name = data[0].split('-')[0]
            sub_dataset[dataset_name] = sub_dataset[dataset_name] + [data] if dataset_name in sub_dataset else [data]
        for dataset_name in sub_dataset:
            out_path = os.path.join(OUTPUT_TSV_PATH, f'{dataset_type}_{dataset_name}.tsv')
            write_file(sub_dataset[dataset_name], out_path)
            dataset_info.append([f'{dataset_type}_{dataset_name}', out_path])
    
    add_eng_bpe_datas   = []
    minus_eng_bpe_datas = []
    add_man_1_datas     = []
    minus_man_1_datas   = []
    add_man_2_datas     = []
    minus_man_2_datas   = []
    for dataset_name, operate, path in datasets['train']:
        token_root_path = path.split('/tsv')[0]
        eng_bpe_path    = os.path.join(token_root_path, 'tokens_ws/text.eng.bpe')
        main_1_path     = os.path.join(token_root_path, 'tokens_ws/token.man.1')
        main_2_path     = os.path.join(token_root_path, 'tokens_ws/token.train')
        if operate == 'add':
            add_eng_bpe_datas.append([d[0] for d in read_file(eng_bpe_path, sp='\t')])
            add_man_1_datas.append([d[0] for d in read_file(main_1_path, sp='\t')])
            add_man_2_datas.append([d[0] for d in read_file(main_2_path, sp='\t')])
        elif operate == 'minus':
            minus_eng_bpe_datas.append([d[0] for d in read_file(eng_bpe_path, sp='\t')])
            minus_man_1_datas.append([d[0] for d in read_file(main_1_path, sp='\t')])
            minus_man_2_datas.append([d[0] for d in read_file(main_2_path, sp='\t')])

    
    add_eng_bpe_datas   = sorted(combine(add_eng_bpe_datas))
    minus_eng_bpe_datas = sorted(combine(minus_eng_bpe_datas))

    add_man_1_datas   = sorted(combine(add_man_1_datas))
    minus_man_1_datas = sorted(combine(minus_man_1_datas))

    add_man_2_datas   = sorted(combine(add_man_2_datas))
    minus_man_2_datas = sorted(combine(minus_man_2_datas))

    eng_bpe_datas = sorted(minus(add_eng_bpe_datas, minus_eng_bpe_datas))
    man_1_datas   = sorted(list(set(minus(add_man_1_datas, minus_man_1_datas))))
    man_2_datas   = sorted(minus(add_man_2_datas, minus_man_2_datas))

    out_path = os.path.join(OUTPUT_TOKEN_PATH, 'text.eng.bpe')
    write_file([[d] for d in eng_bpe_datas], out_path)
    out_path = os.path.join(OUTPUT_TOKEN_PATH, 'token.man.1')
    write_file([[d] for d in man_1_datas], out_path)
    out_path = os.path.join(OUTPUT_TOKEN_PATH, 'token.train')
    write_file([[d] for d in man_2_datas], out_path)

    # create files
    for dataset_name, path in dataset_info:
        in_path  = path
        out_path = os.path.join(OUTPUT_DATA_PATH, f'{dataset_name}')
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        main_datapre(in_path, out_path, sp='\t')

    