import os
import shutil

from tqdm import tqdm
from utils.datapre import read_file
from utils.datapre import write_file

def get_key(start, end):
    return f'{start}_{end}'

segment_file_path    = './tsv/segments'
ws_segment_file_path = './tsv_ws/segments'

wav_segment_path     = './data/wav_segment'
ws_wav_segment_path  = './data_ws/wav_segment'

if __name__ == '__main__':
    segment_file = read_file(segment_file_path, sp='\t')
    timestamp2id = {get_key(d[1], d[2]): d[0] for d in segment_file}

    ws_segment_file = read_file(ws_segment_file_path, sp='\t')
    for ws_id, ws_start, ws_end in tqdm(ws_segment_file):
        ws_key = get_key(ws_start, ws_end)
        key    = timestamp2id[ws_key]
        print(f'ws id: {ws_id}, ws key: {ws_key}, id: {key}')

        wav_path    = os.path.join(wav_segment_path, f'{key}.wav')
        ws_wav_path = os.path.join(ws_wav_segment_path, f'{ws_id}.wav')
        shutil.copy(wav_path, ws_wav_path)