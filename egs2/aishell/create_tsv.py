import os

from tqdm import tqdm
from utils.datapre import write_file

def read_text(path):
    texts = {}
    with open(path, 'r', encoding='utf-8') as frs:
        for fr in tqdm(frs):
            data       = fr.replace('\n', '')
            utt, text  = data.split(' ')[0], data.split(' ')[1:]
            texts[utt] = ''.join(text)
    return texts

def get_utt(paths):
    datas = {}
    for path in paths:
        spk = path.split('/')[-2]
        utt = (path.split('/')[-1]).split('.wav')[0]
        datas[utt] = [utt, spk, path]
    return datas


def main(text_path, root_path, output_path):
    texts = read_text(text_path)
    
    # walk path
    paths = []
    for dirPath, dirNames, fileNames in os.walk(root_path):
        for f in fileNames:
            paths.append(os.path.join(dirPath, f))

    datas  = get_utt(paths)
    _datas = {}
    for utt in datas:
        utt, spk, path = datas[utt]
        if utt not in texts: continue
        text = texts[utt]
        _datas[utt] = [utt, spk, text, path]

    datas = [_datas[key] for key in _datas]

    write_file(datas, output_path)

if __name__ == '__main__':
    text_path   = '/share/nas167/hsinwei/espnet/egs2/aishell/asr1/downloads/data_aishell/transcript/aishell_transcript_v0.8.txt'
    root_path   = '/share/nas167/hsinwei/espnet/egs2/aishell/asr1/downloads/data_aishell/wav/dev'
    output_path = './egs2/aishell/tsv/dev.tsv'

    main(text_path, root_path, output_path)