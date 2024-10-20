from ckip_transformers.nlp import CkipWordSegmenter

ws_driver  = CkipWordSegmenter(model="bert-base", device=0)

text = [
   "傅達仁今將執行安樂死，卻突然爆出自己20年前遭緯來體育台封殺，他不懂自己哪裡得罪到電視台。",
   "美國參議院taiwan針對今天總統布什所提名的勞工部長趙小蘭展開認可聽證會，預料她將會很順利通過參議院支持，成為該國有史以來第一位的華裔女性內閣成員。",
   "空白 也是可以的～",
]

# Run pipeline
ws  = ws_driver(text, use_delim=True)

for sentence, sentence_ws in zip(text, ws):
    print(f'sent: {sentence}, ws: {", ".join(sentence_ws)}')