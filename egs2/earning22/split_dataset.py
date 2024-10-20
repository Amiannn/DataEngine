import os
import re
import random

from tqdm import tqdm
from utils.datapre import read_file
from utils.datapre import read_json
from utils.datapre import write_file

random.seed(0)

def find_year(text):
    """Extracts the first four-digit year from the given text string."""
    match = re.search(r'\b\d{4}\b', text)
    if match:
        return match.group()
    else:
        print(f'text: {text}')
        return "No year found in the text."

def main(root_path, output_path, metadata_path):
    train_dev_ids = []
    train_dev_set = []
    test_set      = []
    testset_years = ['2022']

    dataset   = read_file(root_path, sp='\t')
    metadatas = {d['id']: d for d in read_json(metadata_path)} 
    for data in dataset:
        uid   = data[0]
        ec_id = uid.split('_')[0]
        title = metadatas[ec_id]['content'][0][1][0]
        year  = find_year(title)
        
        check = len([years for years in testset_years if years in year]) > 0
        if check:
            test_set.append(data)
        else:
            train_dev_ids.append(ec_id)
            train_dev_set.append(data)
    
    train_dev_ids = list(set(train_dev_ids))
    print(f'test_set: {len(test_set)}')
    print(f'train_dev_ids: {len(train_dev_ids)}')
    print(f'train_dev_set: {len(train_dev_set)}')

    split_rate       = 0.9
    train_set_length = int(len(train_dev_ids) * split_rate)
    random.shuffle(train_dev_ids)

    train_set_ids = train_dev_ids[:train_set_length]
    dev_set_ids   = train_dev_ids[train_set_length:]
    print(dev_set_ids)

    dev_set   = []
    train_set = []
    for data in train_dev_set:
        uid   = data[0]
        ec_id = uid.split('_')[0]
        if ec_id in train_set_ids:
            train_set.append(data)
        else:
            dev_set.append(data)

    output_dump = os.path.join(output_path, 'train.tsv')
    write_file(sorted(train_set), output_dump, sp="\t")
    output_dump = os.path.join(output_path, 'dev.tsv')
    write_file(sorted(dev_set), output_dump, sp="\t")
    output_dump = os.path.join(output_path, 'test.tsv')
    write_file(sorted(test_set), output_dump, sp="\t")

if __name__ == '__main__':
    root_path     = "./egs2/earning22/tsv/all.tsv"
    output_path   = "./egs2/earning22/tsv"
    metadata_path = "./egs2/earning22/data/earning22_metadata_final.json" 

    main(root_path, output_path, metadata_path)