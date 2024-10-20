import os

from tqdm          import tqdm
# from create_tsv    import main as main_tsv
from utils.datapre import main as main_datapre


if __name__ == '__main__':
    # ROOT_PATH = '/share/nas167/hsinwei/hs_project_acer/proj_acer_ch/s5-aishell/data0'
    DATASETS  = ['train', 'dev', 'test']

    OUTPUT_TSV_PATH  = './egs2/institutional_investors/tsv_ws'
    OUTPUT_DATA_PATH = './egs2/institutional_investors/data_ws'

    # create tsv
    # for dataset in DATASETS:
    #     in_path  = os.path.join(ROOT_PATH, f'{dataset}')
    #     out_path = os.path.join(OUTPUT_TSV_PATH, f'{dataset}.tsv')
    #     main_tsv(in_path, out_path)

    # create files
    for dataset in DATASETS:
        in_path  = os.path.join(OUTPUT_TSV_PATH, f'{dataset}.tsv')
        out_path = os.path.join(OUTPUT_DATA_PATH, f'{dataset}')
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        main_datapre(in_path, out_path, sp='\t')