import os

from tqdm import tqdm
from utils.segment_wav import main

if __name__ == '__main__':
    root_path   = '/share/nas165/amian/experiments/speech/espnet/workspace/esun_zh_asr/asr1/data/test_esun2022/test_sub'
    output_path = './egs2/esun2022_sub/data'

    output_scp_path = './egs2/esun2022_sub/tsv'
    output_wav_path = os.path.join(output_path, 'wav_segment')

    if not os.path.exists(output_wav_path):
        os.makedirs(output_wav_path)
    
    main(root_path, output_wav_path, output_scp_path)