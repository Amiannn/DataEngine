import numpy as np

from Bio    import Align
from typing import List

from utils.datapre import read_file
from utils.datapre import read_json

class CheatDetector():
    def __init__(self, entity_path):
        self.entities = self._load_entity(entity_path)
        self.add_token = "-"
        self.aligner = self._get_aligner()

    def _load_entity(self, entity_path):
        contexts = []
        contexts = read_file(entity_path, sp="\t")
        contexts = [[len(e[0]), e[0]] for e in contexts]
        contexts = [entity for length, entity in sorted(contexts, reverse=True)]
        return contexts
    
    def _preprocess(self, texts):
        return [" ".join(list(text)) for text in texts]

    def _postprocess(self, datas):
        s, e, t = 0, 0, None
        entity_pos, entity_datas, text = [], [], []

        for i in range(len(datas)):
            char, _type = list(datas[i].keys())[0], list(datas[i].values())[0]
            entity_datas.append([char, _type])
            text.append(char)

        for i in range(len(entity_datas)):
            char, _type = entity_datas[i]
            e = i
            if "B-" in _type:
                s = i
                t = _type.split('-')[-1]
            elif _type == "O":
                if t != None:
                    entity_pos.append(["".join(text[s:e]), t, [s, e]])
                s = i
                t = None
        return entity_pos

    @classmethod
    def position_to_flatten(cls, text, prediction):
        flatten = [0 for t in text]
        for i in range(len(prediction)):
            ent, t, position = prediction[i]
            start, end = position
            flatten[start:end] = [i + 1 for j in range(end - start)]
        return [ent, t, flatten] 

    @classmethod
    def flatten_to_position(cls, text, datas):
        entity, t, flatten = datas
        flatten = np.array(flatten)
        length  = np.max(flatten)

        prediction = []
        for i in range(1, length + 1):
            position = np.where(flatten == i)[0]
            start, end = position[0], position[-1] + 1
            entity = text[start:end]
            prediction.append([entity, t, [start, end]])
        return prediction

    def _get_aligner(self):
        aligner = Align.PairwiseAligner()
        aligner.match_score    = 1.0 
        aligner.gap_score      = -2.5
        aligner.mismatch_score = -2.0
        return aligner

    def aligment(self, target, text):
        alignments = self.aligner.align(target, text)[0]
        alignments = str(alignments).split('\n')
        seqA, seqB = alignments[0], alignments[2]
        return [seqA, seqB]

    def shift(self, text, prediction, add_token="-"):
        entity, entity_type, flatten = self.position_to_flatten(text, prediction)
        shift, flatten_shifted = 0, []
        for i in range(len(text)):
            flatten_shifted.append(flatten[i - shift])
            if text[i] == add_token:
                shift += 1
        datas = [entity, entity_type, flatten_shifted]
        prediction = self.flatten_to_position(text, datas)
        prediction = [[
            entity.replace(add_token, " "), entity_type, position
        ] for entity, entity_type, position in prediction]

        return prediction

    def collapse(self, text, prediction, add_token="-"):
        idxmap, count = [], 0
        for i in range(len(text)):
            idxmap.append(count)
            if text[i] != add_token:
                count += 1
        idxmap.append(count)
        new_prediction = []
        for entity, type, pos in prediction:
            start, end = pos
            new_prediction.append([
                entity,
                type,
                [idxmap[start], idxmap[end]]
            ])
        return new_prediction

    def find_all_place(self, text, subtext):
        data = []
        now = text.find(subtext)
        while(now >= 0):
            data.append([now, now + len(subtext)])
            now = text.find(subtext, now + 1)
        return data

    def check_position_hited(self, hitmap, position):
        start, end = position
        delta_hitmap = np.array([0 for t in range(hitmap.shape[0])])
        delta_hitmap[start:end] = 1

        if np.sum(hitmap * delta_hitmap) > 0:
            return True, delta_hitmap
        return False, delta_hitmap

    def find_entity_mention(self, text):
        datas  = []
        hitmap = np.array([0 for t in text])
        for entity in self.entities:
            positions = self.find_all_place(text, entity)
            for position in positions:
                ifpass, delta_hitmap = self.check_position_hited(hitmap, position)
                if ifpass:
                    continue
                else:
                    hitmap += delta_hitmap
                    datas.append([entity, 'ALIGNMENT', position])
        # sort it
        datas = sorted([[data[-1][0], data] for data in datas])
        datas = [data[1] for data in datas]
        return datas

    def predict_one_step(self, target: str, text: str, return_align: bool=False) -> List[str]:
        target_prediction        = self.find_entity_mention(target)
        align_target, align_text = self.aligment(target, text)

        if len(target_prediction) > 0:
            align_prediction  = self.shift(align_target, target_prediction, self.add_token)
            align_prediction  = [[
                align_text[pos[0]:pos[1]].replace(self.add_token, " "), entity_type, pos
            ] for entity, entity_type, pos in align_prediction]
            align_prediction  = self.collapse(align_text, align_prediction, self.add_token)
        else:
            align_prediction = target_prediction
        if return_align:
            return align_prediction, [target_prediction, align_target, align_text]
        return align_prediction

    def predict(self, targets: List[str], texts: List[str]) -> List[str]:
        predictions = [self.predict_one_step(target, text) for target, text in zip(targets, texts)]
        return predictions

if __name__ == "__main__":
    entity_path = "/share/nas165/amian/experiments/speech/preprocess/dataset_pre/others/esun_dumps/crawler/esun.entity.zh.txt"
    detector = CheatDetector(entity_path)

    target = "問 一 個 比 較 小 的 問 題 就 是 我 們 創 投 持 有 那 個 oby i 發 嘛 就 是 浩 鼎 生 技 的 未 實 現 那 個 利 益 大 概 還 有 四 五 一 就 非 常 他 的 那 個 收 盤 價 那 不 知 道 公 司 在 這 方 面 有 什 麼 想 法"
    text   = "問 一 個 比 較 小 的 問 題 就 是 我 們 創 投 持 有 那 個 就 是 號 頂 生 技 的 未 實 浩 鼎 生 技 益 大 概 還 有 四 五 億 就 based on 他 的 那 個 收 盤 價 那 不 知 道 公 司 在 這 方 面 有 什 麼 想 法"

    target = target.replace(' ', '')
    text   = text.replace(' ', '')

    prediction, [target_prediction, align_target, align_text] = detector.predict_one_step(target, text, return_align=True)
    print(f'prediction: {prediction}')
    print(f'target_prediction: {target_prediction}')
    print(f'align_target: {align_target}')
    print(f'align_text: {align_text}')

    for entity, _, pos in prediction:
        print(entity)
        start, end = pos
        print(text[start:end])
        print('_' * 30)

    # print(f'target: {align_target}')
    # print(f'text__: {align_text}')