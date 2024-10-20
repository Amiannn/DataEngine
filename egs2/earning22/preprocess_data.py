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

def cleaner(text):
    return clean(
        text,
        fix_unicode=True,               # fix various unicode errors
        to_ascii=True,                  # transliterate to closest ASCII representation
        lower=True,                     # lowercase text
        no_line_breaks=True,           # fully strip line breaks as opposed to only normalizing them
        no_urls=True,                  # replace all URLs with a special token
        no_emails=True,                # replace all email addresses with a special token
        no_phone_numbers=True,         # replace all phone numbers with a special token
        no_numbers=False,               # replace all numbers with a special token
        no_digits=False,                # replace all digits with a special token
        no_currency_symbols=True,      # replace all currency symbols with a special token
        no_punct=True,                  # remove punctuations
        replace_with_punct="",          # instead of removing punctuations you may replace them
        replace_with_url="",
        replace_with_email="",
        replace_with_phone_number="",
        replace_with_number="",
        replace_with_digit="",
        replace_with_currency_symbol="",
        lang="en"                       # set to 'de' for German special handling
    ).upper()

def merge_broke(datas):
    last_start, last_end = 0, 0
    next_start, next_end = 0, 0

    chunk  = []
    chunks = []
    for i in range(len(datas)):
        data = datas[i]
        
        start_time = data['start_time']
        end_time   = data['end_time']

        if start_time is None and len(chunk) == 0:
            chunk = chunks.pop(-1)
            chunk.append(data)
        elif end_time is not None:
            chunk.append(data)
            chunks.append(chunk)
            chunk = []
        else:
            chunk.append(data)
    
    result   = []
    for chunk in chunks:
        text           = " ".join([c['text'] for c in chunk])
        start_word_idx = chunk[0]['start_word_idx']
        end_word_idx   = chunk[-1]['end_word_idx']
        start_time     = chunk[0]['start_time']
        end_time       = chunk[-1]['end_time']

        entities = {}
        for c in chunk:
            entity = c['entity']
            entities.update(entity)

        result.append({
            'text': text,
            'entity': entities,
            'start_word_idx': start_word_idx,
            'end_word_idx': end_word_idx,
            'start_time': start_time,
            'end_time': end_time,
        })
    return result

if __name__ == '__main__':
    wav_folder             = '/share/nas165/amian/experiments/speech/preprocess/dataset_pre/egs2/earning22/data/wav_16k'
    earning_utterance_path = './egs2/earning22/data/earning22_utterances.json'
    output_folder          = './egs2/earning22/dump'

    texts         = []
    segments      = []
    wav2scp       = []
    merge_results = {}

    earning_utterance_datas = read_json(earning_utterance_path)
    for id in earning_utterance_datas:
        result = merge_broke(earning_utterance_datas[id])
        merge_results[id] = result

        for data in merge_results[id]:
            text           = data['text']
            start_word_idx = data['start_word_idx']
            end_word_idx   = data['end_word_idx']
            start_time     = data['start_time']
            end_time       = data['end_time']
            text_clean     = cleaner(text)
            
            uid = f'{id}_s{start_word_idx}e{end_word_idx}'
            texts.append([uid, text_clean])
            segments.append([uid, str(start_time), str(end_time)])
            wav2scp.append([uid, os.path.join(wav_folder, f'{id}.wav')])
    
    output_path = os.path.join(output_folder, f'merge.json')
    write_json(output_path, merge_results)
    
    output_path = os.path.join(output_folder, f'text')
    write_file(texts, output_path, sp='\t')

    output_path = os.path.join(output_folder, f'wav.scp')
    write_file(wav2scp, output_path, sp='\t')

    output_path = os.path.join(output_folder, f'segments')
    write_file(segments, output_path, sp='\t')