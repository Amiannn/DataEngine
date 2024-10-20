import os
import re

from tqdm import tqdm
from utils.datapre import read_file
from utils.datapre import read_json
from utils.datapre import write_file
from utils.datapre import main as main_datapre

OUTPUT_TSV_PATH   = "./egs2_combine/earningcall/tsv"
OUTPUT_DATA_PATH  = "./egs2_combine/earningcall/data"
DATAMAP_PATH      = './egs2_combine/earningcall/datamap.json'

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

    # create tsv
    dataset_info = []
    for index, dataset_type in enumerate(datasets):
        add_datas   = []
        minus_datas = []

        for datas in datasets[dataset_type]:
            dataset_name, operate, path = datas
            if operate == 'add':
                add_datas.append([[f'{dataset_name}-{d[0]}', f'{dataset_name}-{d[0]}', *d[2:]] for d in read_file(path, sp='\t')])
            elif operate == 'minus':
                minus_datas.append([[f'{dataset_name}-{d[0]}', f'{dataset_name}-{d[0]}', *d[2:]] for d in read_file(path, sp='\t')])

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
    
    # create files
    for dataset_name, path in dataset_info:
        in_path  = path
        out_path = os.path.join(OUTPUT_DATA_PATH, f'{dataset_name}')
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        main_datapre(in_path, out_path, sp='\t')

    