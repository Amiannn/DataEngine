import os
import re
import random

from tqdm          import tqdm
from cleantext     import clean
from utils.datapre import read_file
from utils.datapre import read_json
from utils.datapre import write_file
from utils.datapre import write_json

random.seed(0)

if __name__ == '__main__':
    text_path   = './egs2/earning22/dump/text'
    wavscp_path = './egs2/earning22/dump/wav.scp'
    output_dir  = './egs2/earning22/tsv'

    texts   = read_file(text_path, sp='\t')
    wavscps = {d[0]: d[1] for d in read_file(wavscp_path, sp='\t')}

    result  = []
    count   = 0
    last_id = ""
    for id, text in texts:
        ec_id = id.split('_')[0]
        if ec_id != last_id:
            count = 0
        if text == "":
            continue
        _id   = id.replace('_', f'_{str(count).zfill(4)}_')
        result.append([_id, _id, text, wavscps[id]])
        count += 1
        last_id = ec_id
    
    output_path = os.path.join(output_dir, 'all.tsv')
    write_file(result, output_path)

    
