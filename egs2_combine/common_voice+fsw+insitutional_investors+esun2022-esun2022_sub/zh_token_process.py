import os

from tqdm import tqdm
from utils.datapre import read_file
from utils.datapre import read_json
from utils.datapre import write_file

sep = "▁"

if __name__ == '__main__':
    path = "./egs2_combine/common_voice+fsw+insitutional_investors+esun2022-esun2022_sub/tokens/token.man.1"
    zh_tokens = read_file(path)
    
    tokens = []
    for token in zh_tokens:
        t = token[0]
        if t == "\u2003" or t == "�":
            continue
        tokens.append(t)

    man_chars = len(tokens)
    # bpe_nlsyms =  f"{tokens[0]}," + f",{sep}".join(tokens[1:])
    bpe_nlsyms =  sep + f",{sep}".join(tokens[1:])
    
    data = [
        [f'bpe_nlsyms="{bpe_nlsyms}"'],
        [f'man_chars={man_chars}']
    ]

    output_path = os.path.join('./egs2_combine/common_voice+fsw+insitutional_investors+esun2022-esun2022_sub/tokens/', 'token.man.2')
    write_file(data, output_path, sp='')