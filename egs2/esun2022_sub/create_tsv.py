import os
import re

from tqdm import tqdm
from utils.datapre import read_file
from utils.datapre import write_file

def check_is_english(word):
    if re.search("[\u4e00-\u9FFF]", word) == None:
        return True
    return False

def word_to_sentence(words):
    sentence = ""
    for i in range(len(words)):
        word = words[i]
        # if check_is_english(word):
        #     sentence += word
        #     if (i + 1) < len(words) and check_is_english(words[i + 1]):
        #         sentence += " "
        # else:
        #     sentence += word
        if (i + 1) < len(words):
            sentence += f'{word.lower()} '
        else:
            sentence += f'{word.lower()}'
    return sentence

def main(root_path, output_path):
    # wavscp_path  = os.path.join(root_path, 'wav.scp')
    wavscp_path  = './egs2/esun2022_sub/tsv/wav.scp'
    utt2spk_path = os.path.join(root_path, 'utt2spk')
    text_path    = '/share/nas167/hsinwei/z_corpus/ESUN-own/text_ws'

    wavscp_datas = read_file(wavscp_path, sp=' ')
    wavscp_datas = {utt: [utt, path] for utt, path in wavscp_datas} 

    utt2spk_datas = read_file(utt2spk_path, sp=' ')
    utt2spk_datas = {utt: spk for utt, spk in utt2spk_datas}

    text_datas = read_file(text_path, sp='\t')
    text_datas = {d[0]: word_to_sentence(d[1].split(' ')) for d in text_datas}

    _datas = {}
    for utt in wavscp_datas:
        utt, path = wavscp_datas[utt]

        spk     = utt2spk_datas[utt]
        text    = text_datas[utt]
        
        _datas[utt] = [utt, spk, text, path]

    datas = [_datas[key] for key in _datas]

    write_file(datas, output_path)

if __name__ == '__main__':
    root_path   = '/share/nas165/amian/experiments/speech/espnet/workspace/esun_zh_asr/asr1/data/test_esun2022/test_sub'
    output_path = './egs2/esun2022_sub/tsv/test.tsv'

    main(root_path, output_path)