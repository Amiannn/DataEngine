import os

from tqdm          import tqdm
from create_tsv    import main as main_tsv
from utils.datapre import main as main_datapre


if __name__ == '__main__':
    ROOT_PATH = '/share/nas167/hsinwei/espnet/egs2/aishell/asr1/downloads/data_aishell'
    TEXT_PATH = os.path.join(ROOT_PATH, 'transcript/aishell_transcript_v0.8.txt')
    DATASETS  = ['train', 'test', 'dev']

    OUTPUT_TSV_PATH  = './egs2/aishell/tsv'
    OUTPUT_DATA_PATH = './egs2/aishell/data'

    # create tsv
    for dataset in DATASETS:
        in_path  = os.path.join(ROOT_PATH, f'wav/{dataset}')
        out_path = os.path.join(OUTPUT_TSV_PATH, f'{dataset}.tsv')
        main_tsv(TEXT_PATH, in_path, out_path)

    # create files
    for dataset in DATASETS:
        in_path  = os.path.join(OUTPUT_TSV_PATH, f'{dataset}.tsv')
        out_path = os.path.join(OUTPUT_DATA_PATH, f'{dataset}')
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        main_datapre(in_path, out_path)