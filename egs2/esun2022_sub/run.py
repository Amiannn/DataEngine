import os

from tqdm            import tqdm
from create_flat_tsv import main as main_tsv
from utils.datapre   import main as main_datapre


if __name__ == '__main__':
    ROOT_PATH = '/share/nas165/amian/datasets/cv-corpus-11.0-2022-09-21/zh-TW'
    WAV_PATH  = os.path.join(ROOT_PATH, 'clips_wav_16k')
    DATASETS  = ['train', 'test', 'dev']

    OUTPUT_TSV_PATH  = './egs2/common_voice/tsv'
    OUTPUT_DATA_PATH = './egs2/common_voice/data'

    # create tsv
    for dataset in DATASETS:
        in_path  = os.path.join(ROOT_PATH, f'{dataset}.tsv')
        out_path = os.path.join(OUTPUT_TSV_PATH, f'{dataset}.tsv')
        main_tsv(WAV_PATH, in_path, out_path)

    # create files
    for dataset in DATASETS:
        in_path  = os.path.join(OUTPUT_TSV_PATH, f'{dataset}.tsv')
        out_path = os.path.join(OUTPUT_DATA_PATH, f'{dataset}')
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        main_datapre(in_path, out_path)
