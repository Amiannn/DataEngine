import os
from tqdm import tqdm

from utils.fileio import read_file
from utils.fileio import write_file


def main(text_path, wavscp_path, output_path, folder_name):
    text_datas   = {d[0]: " ".join(d[1:]) for d in read_file(text_path, sp=' ')}
    wavscp_datas = {d[0]: d[1] for d in read_file(wavscp_path, sp=' ')}
    
    # [utt, spk, text, path]
    datas = []
    for utt in text_datas:
        utt_name = utt.replace('-', '_')
        datas.append([utt_name, utt_name, text_datas[utt], wavscp_datas[utt]])

    output_file = os.path.join(output_path, folder_name + '.tsv')
    write_file(datas, output_file, sp='\t')

if __name__ == '__main__':
    folder_names = ['test', 'dev', 'L95', 'S95']
    for folder_name in folder_names:
        text_path   = f'/mnt/storage1/experiments/DataEngine/egs2/slidespeech/slidespeech/related_files/{folder_name}/text'
        wavscp_path = f'/mnt/storage1/experiments/DataEngine/egs2/slidespeech/datas/{folder_name}/wav.scp'
        output_path = '/mnt/storage1/experiments/DataEngine/egs2/slidespeech/tsv'
        main(text_path, wavscp_path, output_path, folder_name)
