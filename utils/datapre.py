import os

from tqdm    import tqdm
from .fileio import read_file
from .fileio import read_json
from .fileio import write_file
from .fileio import write_json

def remove_empty(data):
    return [d for d in data if d != ' ' and d != '']

def format_utt2spk(datas):
    utts = {}
    for data in datas:
        utt, spk, _, _ = data
        try:
            utts[utt].append(spk)
        except:
            utts[utt] = [spk]
    return utts

def format_spk2utt(datas):
    spks = {}
    for data in datas:
        utt, spk, _, _ = data
        try:
            spks[spk].append(utt)
        except:
            spks[spk] = [utt]
    return spks

def format_text(datas):
    return [[utt, text] for utt, spk, text, path in datas]

def format_wavscp(datas):
    return [[utt, path] for utt, spk, text, path in datas]

def main(path, output_path, sp=' '):
    datas = sorted(read_file(path, sp=sp))
    # datas = [remove_empty(data) for data in datas] 
    utt2spk = format_utt2spk(datas)
    utt2spk = [[key, *utt2spk[key]] for key in utt2spk]
    spk2utt = format_spk2utt(datas)
    spk2utt = [[key, *spk2utt[key]] for key in spk2utt]

    texts   = format_text(datas)
    wavscp  = format_wavscp(datas)

    utt2spk = sorted(utt2spk)
    utt2spk_path = os.path.join(output_path, 'utt2spk')
    write_file(utt2spk, utt2spk_path, sp=' ')

    spk2utt = sorted(spk2utt)
    spk2utt_path = os.path.join(output_path, 'spk2utt')
    write_file(spk2utt, spk2utt_path, sp=' ')

    texts = sorted(texts)
    texts_path = os.path.join(output_path, 'text')
    write_file(texts, texts_path, sp=' ')

    wavscp = sorted(wavscp)
    wavscp_path = os.path.join(output_path, 'wav.scp')
    write_file(wavscp, wavscp_path, sp=' ')


if __name__ == '__main__':
    tsv_path    = '/share/nas165/amian/experiments/speech/preprocess/dataset_pre/egs2/aishell/tsv/dev.tsv'
    output_path = './'

    main(tsv_path, output_path)