import os

from tqdm import tqdm
from utils.datapre import read_file
from utils.datapre import write_file
from utils.datapre import main as main_datapre

def combine(datas):
    dataset = []
    for data in datas:
        dataset.extend(data)
    return dataset

if __name__ == '__main__':
    ROOT_A_PATH = '/share/nas165/amian/experiments/speech/preprocess/dataset_pre/egs2/common_voice/tsv'
    ROOT_B_PATH = '/share/nas165/amian/experiments/speech/preprocess/dataset_pre/egs2/fsw/tsv'

    DATASETS    = ['train', 'dev', 'test']
    DATASETS_A  = [['train'], ['dev'], ['test']]
    DATASETS_B  = [['train'], ['eval0', 'eval1'], ['test']]

    OUTPUT_TSV_PATH  = './egs2_combine/common_voice+fsw/tsv'
    OUTPUT_DATA_PATH = './egs2_combine/common_voice+fsw/data'

    # create tsv
    for index, dataset in enumerate(DATASETS):
        in_a_paths  = [os.path.join(ROOT_A_PATH, f'{path}.tsv') for path in DATASETS_A[index]]
        in_b_paths  = [os.path.join(ROOT_B_PATH, f'{path}.tsv') for path in DATASETS_B[index]]

        data_a = combine([read_file(path) for path in in_a_paths])
        data_b = combine([read_file(path) for path in in_b_paths])
        
        datas  = sorted(combine([data_a, data_b]))

        out_path = os.path.join(OUTPUT_TSV_PATH, f'{dataset}.tsv')
        write_file(datas, out_path)

    # create files
    for dataset in DATASETS:
        in_path  = os.path.join(OUTPUT_TSV_PATH, f'{dataset}.tsv')
        out_path = os.path.join(OUTPUT_DATA_PATH, f'{dataset}')
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        main_datapre(in_path, out_path)