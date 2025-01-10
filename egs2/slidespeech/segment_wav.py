import os
from scipy.io import wavfile
from tqdm import tqdm

from utils.fileio import read_file
from utils.fileio import write_file

def segment(datas, sr, s_sec, e_sec):
    """Return a slice of the audio array from s_sec to e_sec."""
    s = int(s_sec * sr)
    e = int(e_sec * sr)
    return datas[s:e]

def main(root_path, output_wav_path, output_scp_path):

    folder_name = os.path.basename(root_path)
    output_wav_path = os.path.join(output_wav_path, folder_name)
    output_scp_path = os.path.join(output_scp_path, folder_name)

    if not os.path.exists(output_wav_path):
        os.makedirs(output_wav_path)
    if not os.path.exists(output_scp_path):
        os.makedirs(output_scp_path)

    wavscp_path  = os.path.join(root_path, 'wav.scp')
    segment_path = os.path.join(root_path, 'segments')

    # Read the wav.scp as a dict: {utt_id: relative_wav_path}
    wavscp_datas = read_file(wavscp_path, sp=' ')
    wavscp_datas = {utt: path for utt, path in wavscp_datas}

    # Read the segments file as a dict: {segment_utt: (original_utt, start, end)}
    segment_lines = read_file(segment_path, sp=' ')
    segment_datas = {d[0]: d[1:] for d in segment_lines}  # e.g. {seg_id: [wav_id, start, end]}

    # ---------------------------------------------------
    # 1) Group segments by their *underlying WAV file*.
    #    We'll create a dictionary:
    #    {absolute_wav_path: [(seg_utt, start, end), ...]}
    # ---------------------------------------------------
    segments_by_wav = {}
    for seg_utt, (orig_utt, start_sec, end_sec) in segment_datas.items():
        # Rebuild the absolute path to the wav file
        wav_path = os.path.abspath(os.path.join(root_path, '../../', wavscp_datas[orig_utt]))
        if wav_path not in segments_by_wav:
            segments_by_wav[wav_path] = []
        segments_by_wav[wav_path].append((seg_utt, float(start_sec), float(end_sec)))

    # We'll store the final lines (utt_id, wav_path) to write in wav.scp.
    segmented_wavscp_datas = []

    # ---------------------------------------------------
    # 2) Process each WAV file once, writing out all segments
    # ---------------------------------------------------
    for wav_path, seg_entries in tqdm(segments_by_wav.items(), desc="Processing WAVs"):
        # Read the audio data once
        sample_rate, datas = wavfile.read(wav_path)

        # For each segment in this WAV, slice & write
        for (seg_utt, start_sec, end_sec) in seg_entries:
            # Generate output path for this segment
            out_wav_path = os.path.abspath(
                os.path.join(output_wav_path, f"{seg_utt}.wav")
            )
            # Segment the audio
            seg_data = segment(datas, sample_rate, start_sec, end_sec)
            # Write the .wav segment
            wavfile.write(out_wav_path, sample_rate, seg_data)
            # Record it in our new wav.scp data
            segmented_wavscp_datas.append([seg_utt, out_wav_path])

    # Write out the new wav.scp for all segments
    segmented_wavscp_path = os.path.join(output_scp_path, 'wav.scp')
    write_file(segmented_wavscp_datas, segmented_wavscp_path, sp=' ')

if __name__ == '__main__':
    folder_names = ['test', 'dev', 'L95']
    # folder_names = ['S95']
    for folder_name in folder_names:
        root_path = f'/mnt/storage1/experiments/DataEngine/egs2/slidespeech/slidespeech/related_files/{folder_name}'
        output_wav_path = '/mnt/storage1/experiments/DataEngine/egs2/slidespeech/segment_wav'
        output_scp_path = '/mnt/storage1/experiments/DataEngine/egs2/slidespeech/datas'
        main(root_path, output_wav_path, output_scp_path)
