import os
import torchaudio

from tqdm import tqdm
from .fileio import read_file
from .fileio import write_file

def segment(datas, sr, s_sec, e_sec):
    s = int(s_sec * sr)
    e = int(e_sec * sr)

    return datas[:, s:e]

def main(root_path, output_wav_path, output_scp_path):
    wavscp_path   = os.path.join(root_path, 'wav.scp')
    segment_path  = os.path.join(root_path, 'segments')

    wavscp_datas = read_file(wavscp_path, sp='\t')
    print(wavscp_datas[:10])
    wavscp_datas = {utt: path for utt, path in wavscp_datas} 
    
    segment_datas = read_file(segment_path, sp='\t')
    segment_datas = {d[0]: d[1:] for d in segment_datas}

    segmented_wavscp_datas = []
    audio_cache = {}
    last_path = None
    for utt in tqdm(segment_datas):
        start, end = segment_datas[utt]
        path = wavscp_datas[utt]
        if path in audio_cache:
            datas, sample_rate = audio_cache[path]
        else:
            datas, sample_rate = torchaudio.load(path)
            audio_cache[path] = datas, sample_rate
            if last_path != None:
                del audio_cache[last_path]
            last_path = path
            
        start = float(start)
        end   = float(end)

        segmented_path = os.path.abspath(os.path.join(output_wav_path, f'{utt}.wav'))
        segmented_wavscp_datas.append([utt, segmented_path])

        segmented_datas = segment(datas, sample_rate, start, end)
        torchaudio.save(segmented_path, segmented_datas, sample_rate)

    segmented_wavscp_path = os.path.join(output_scp_path, 'wav.scp')
    write_file(segmented_wavscp_datas, segmented_wavscp_path, sp='\t')

        
