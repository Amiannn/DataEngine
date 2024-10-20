import os
import subprocess

from tqdm import tqdm

ROOT_PATH   = '/share/nas165/amian/experiments/speech/earningcall/earnings22/media'
OUTPUT_PATH = '/share/nas165/amian/experiments/speech/preprocess/dataset_pre/egs2/earningcall/data/wav_16k/earning22'

def coverter(root_path, output_path):
    for _path in tqdm(os.listdir(root_path)):
        path = os.path.join(root_path, _path)
        _output_path = os.path.join(output_path, _path.split('.')[0])
        print(f'output_path: {_output_path}')
        subprocess.run(f"ffmpeg -i {path} -acodec pcm_s16le -ac 1 -ar 16000 {_output_path}.wav", shell=True, check=True)

if __name__ == '__main__':
    coverter(ROOT_PATH, OUTPUT_PATH)