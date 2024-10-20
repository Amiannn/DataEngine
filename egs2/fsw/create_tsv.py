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
        if not check_is_english(word):
            if (i + 1) < len(words):
                sentence += (" ".join(word) + " ")
            else:
                sentence += " ".join(word)
        # if check_is_english(word):
        #     sentence += word
        #     if (i + 1) < len(words) and check_is_english(words[i + 1]):
        #         sentence += " "
        # else:
        #     sentence += word
        elif (i + 1) < len(words):
            sentence += f'{word.lower()} '
        else:
            sentence += f'{word.lower()}'
    return sentence

def main(root_path, output_path):
    wavscp_path  = os.path.join(root_path, 'wav.scp')
    utt2spk_path = os.path.join(root_path, 'utt2spk')
    text_path    = os.path.join(root_path, 'text')

    wavscp_datas = read_file(wavscp_path, sp=' ')
    wavscp_datas = {utt: [utt, path] for utt, path in wavscp_datas} 

    utt2spk_datas = read_file(utt2spk_path, sp=' ')
    utt2spk_datas = {utt: spk for utt, spk in utt2spk_datas}

    text_datas = read_file(text_path, sp=' ')
    text_datas = {d[0]: d[1:] for d in text_datas}

    _datas = {}
    for utt in wavscp_datas:
        utt, path = wavscp_datas[utt]

        spk  = utt2spk_datas[utt]
        text = text_datas[utt]
        text = word_to_sentence(text)

        _datas[utt] = [utt, spk, text, path]

    datas = [_datas[key] for key in _datas]

    write_file(datas, output_path)

if __name__ == '__main__':
    root_path   = '/share/nas167/hsinwei/hs_project_acer/proj_acer_ch/s5-aishell/data0/eval1'
    output_path = './egs2/fsw/tsv/eval1.tsv'

    main(root_path, output_path)