import os

from tqdm          import tqdm
from utils.datapre import main as main_datapre


if __name__ == '__main__':
    DATASETS  = ['test', 'dev', 'L95', 'S95']

    OUTPUT_TSV_PATH  = '/mnt/storage1/experiments/DataEngine/egs2/slidespeech/tsv'
    OUTPUT_DATA_PATH = '/mnt/storage1/experiments/DataEngine/egs2/slidespeech/data'

    # create files
    for dataset in DATASETS:
        in_path  = os.path.join(OUTPUT_TSV_PATH, f'{dataset}.tsv')
        out_path = os.path.join(OUTPUT_DATA_PATH, f'{dataset}')
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        main_datapre(in_path, out_path, sp='\t')