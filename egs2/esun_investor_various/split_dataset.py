import os
import random

from tqdm import tqdm
from utils.datapre import read_file
from utils.datapre import write_file

random.seed(0)
wav_root_path = '/share/nas165/amian/experiments/speech/preprocess/dataset_pre/egs2/esun_investor_various/data_ws/wav_segment'

def main(root_path, output_path):
    dataset   = read_file(root_path, sp='\t')
    
    testset_years = ['2019', '2020', '2021', '2022']

    train_dev_set = []
    test_set      = []

    for data in dataset:
        uid      = data[0]
        data[-1] = os.path.join(wav_root_path, f'{uid}.wav')
        check    = len([years for years in testset_years if years in uid]) > 0
        if check:
            test_set.append(data)
        else:
            train_dev_set.append(data)
    
    split_rate       = 0.9
    train_set_length = int(len(train_dev_set) * split_rate)
    random.shuffle(train_dev_set)

    train_set = train_dev_set[:train_set_length]
    dev_set   = train_dev_set[train_set_length:]

    output_dump = os.path.join(output_path, 'train.tsv')
    write_file(sorted(train_set), output_dump, sp="\t")
    output_dump = os.path.join(output_path, 'dev.tsv')
    write_file(sorted(dev_set), output_dump, sp="\t")
    output_dump = os.path.join(output_path, 'test.tsv')
    write_file(sorted(test_set), output_dump, sp="\t")

if __name__ == '__main__':
    root_path   = "./egs2/esun_investor_various/tsv_ws/all.tsv"
    output_path = "./egs2/esun_investor_various/tsv_ws"

    main(root_path, output_path)