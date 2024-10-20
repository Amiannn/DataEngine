import os

from tqdm import tqdm
from utils.datapre import read_file
from utils.datapre import read_json
from utils.datapre import write_file

sep = "▁"

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

if __name__ == '__main__':
    path = "./egs2_combine/esun_investor_various+institutional_investors/token_list/bpe_unigram4000suffix/bpe.vocab"
    zh_tokens = read_file(path, sp='\t')
    
    tokens = []
    for token, _ in zh_tokens[1:]:
        t = token
        if t == "\u2003" or t == "�" or isEnglish(t.replace(sep, '')):
            continue
        tokens.append(t)

    man_chars = len(tokens)
    print(man_chars)
    # bpe_nlsyms =  f"{tokens[0]}," + f",{sep}".join(tokens[1:])
    # bpe_nlsyms =  sep + f"{sep},".join(tokens[1:])
    bpe_nlsyms =  f",".join(tokens[1:])
    
    data = [
        [f'bpe_nlsyms="{bpe_nlsyms}"'],
        [f'man_chars={man_chars}']
    ]

    output_path = os.path.join('./egs2_combine/esun_investor_various+institutional_investors/tokens_ws/', 'token.man.2')
    write_file(data, output_path, sp='')