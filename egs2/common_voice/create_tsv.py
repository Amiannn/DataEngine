import os

from tqdm import tqdm
from utils.datapre import read_file
from utils.datapre import write_file

def read_wav(wav_path):
    datas = {}
    for path in tqdm(os.listdir(wav_path)):
        _path = os.path.join(wav_path, path)
        utt  = (path.split('/')[-1]).split('.')[0]
        datas[utt] = _path
    return datas

def get_utt(paths):
    datas = {}
    for path in paths:
        spk = path.split('/')[-2]
        utt = (path.split('/')[-1]).split('.wav')[0]
        datas[utt] = [utt, spk, path]
    return datas


def main(wav_path, root_path, output_path):
    wav_datas = read_wav(wav_path)
    datas     = read_file(root_path)
    datas     = {
        path.split('.')[0]: [path.split('.')[0], client_id, " ".join(list(sentence))] for client_id, path, sentence, up_votes, down_votes, age, gender, accents, locale, segment in datas
    }

    _datas = {}
    for utt in datas:
        utt, spk, text = datas[utt]
        if utt not in wav_datas: continue
        path = wav_datas[utt]
        _datas[utt] = [utt, spk, text, path]

    datas = [_datas[key] for key in _datas]

    write_file(datas, output_path)

if __name__ == '__main__':
    wav_path    = '/share/nas165/amian/datasets/cv-corpus-11.0-2022-09-21/zh-TW/clips_wav'
    root_path   = '/share/nas165/amian/datasets/cv-corpus-11.0-2022-09-21/zh-TW/train.tsv'
    output_path = './egs2/common_voice/tsv/train.tsv'

    main(wav_path, root_path, output_path)