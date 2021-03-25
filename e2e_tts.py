import tensorflow as tf
import yaml
import numpy as np
import matplotlib.pyplot as plt

import IPython.display as ipd

from tensorflow_tts.inference import AutoConfig
from tensorflow_tts.inference import TFAutoModel
from tensorflow_tts.inference import AutoProcessor
from synthesiser import do_synthesis
import soundfile as sf
import flask
from opencc import OpenCC
import zhon.hanzi as hanzi
import re
from pycnnum import num2cn
import uuid


d2c = lambda x: num2cn(int(x), numbering_type = 'low', alt_two = False, big = False, traditional= False) if re.sub('\.','',x).isdigit() else x
cc = OpenCC('t2s')

def load_model():
    tacotron2_config = AutoConfig.from_pretrained('TensorFlowTTS/examples/tacotron2/conf/tacotron2.baker.v1.yaml')
    tacotron2 = TFAutoModel.from_pretrained(
        config=tacotron2_config,
        pretrained_path="content/tacotron2-100k.h5",
        name="tacotron2"
    )

    fastspeech2_config = AutoConfig.from_pretrained('TensorFlowTTS/examples/fastspeech2/conf/fastspeech2.baker.v2.yaml')
    fastspeech2 = TFAutoModel.from_pretrained(
        config=fastspeech2_config,
        pretrained_path="content/fastspeech2-200k.h5",
        name="fastspeech2"
    )

    mb_melgan_config = AutoConfig.from_pretrained('TensorFlowTTS/examples/multiband_melgan/conf/multiband_melgan.baker.v1.yaml')
    mb_melgan = TFAutoModel.from_pretrained(
        config=mb_melgan_config,
        pretrained_path="content/mb.melgan-920k.h5",
        name="mb_melgan"
    )
    return  tacotron2,fastspeech2,mb_melgan

def sec2numpy(sec):
    return np.zeros(int(24000*sec))


def e2e_tts(input_text,tacotron2,fastspeech2,mb_melgan):
    uuidcode = uuid.uuid4().hex

    text = input_text
    
    # 第一步：繁轉簡 conver trandition to simple char 
    input_text =  cc.convert(input_text) 
    print('simple char: '+ input_text)
    # 第二步：處理含小數點的數字 handle digit point  6.61 ==> 6点61
    input_text = re.sub(r'(\d+)(\.)(\d+)',r'\1点\3',input_text)
    # 第三步：把阿拉伯數字轉環成簡體的中文數字   digit to mandarin char
    char_digits = re.findall(r'[\u4e00-\u9fff\uFF01-\uFF5E\u3000\u3001-\u303F]+|[0-9\.]+', input_text)
    char_char = list(map(lambda x: d2c(x), char_digits))
    input_text = ''.join(char_char)
    print('d2c:' + input_text)
    # 第四步：依照標點符號分段(句) sentence segmentation by punctuation
    input_list = re.split('['+hanzi.punctuation+']',input_text)
    input_list = list(filter(lambda x: len(x)>0, input_list))
    # 開始以句為單位進行TTS
    tacotron2.setup_window(win_front=5, win_back=5)
    au1 = np.array([])
    au2 = np.array([])
    for idx, txt in enumerate(input_list):
        mels, alignment_history, audios = do_synthesis(txt, tacotron2, mb_melgan, "TACOTRON", "MB-MELGAN")
        au1 = audios  if idx == 0 else np.concatenate((au1,sec2numpy(0.1), audios),axis=0)
        mels, audios = do_synthesis(txt, fastspeech2, mb_melgan, "FASTSPEECH2", "MB-MELGAN")
        au2 = audios  if idx == 0 else np.concatenate((au2,sec2numpy(0.05),audios),axis=0)
    
    sf.write('./output/'+str(uuidcode)+ '_tacotron.wav', au1, 24000, 'PCM_24')
    sf.write('./output/'+str(uuidcode)+ '_factspeech.wav', au2, 24000, 'PCM_24')
        
    return str(uuidcode)

if __name__=="__main__":
    #input_text = "台中持续加码补助老旧机车淘汰换电动机车，今年度淘汰1至4期老旧机车换购电动机车"
    #input_text = "台中持續加碼補助老舊機車汰換電動機車，今年度淘汰1至4期老舊機車換購電動機車"
    input_text = "大豐有線電視公布的財報顯示，民國109年全年營收再次站上20億元關卡，營業淨利達6.61億元，較去年同期成長7.5%，每股純益3.38元，與前年約當。由於有線電視的營收主要來自「視訊」和「寬頻」兩大板塊，隨著視訊收入因戶數直直落而不若以往，近年有線電視業者都聚焦爭取寬頻用戶。"
    input_text = u"1，真實報，我叫白田山則安，現在念三年三班。我的綽號是「十塊錢便宜貨」，我是個記者喔，厲害吧，今天，我們在學校，學了報紙的功用，說到新聞，從印了幾百萬份，發到日本全國各地的報紙，到最多印五十多份左右年級報，各式各樣的都有。像是家庭報啦、明信片通訊等等，一個人就可以做出來的報紙，好像也不少，所以，我也決定來出一份報紙。說是這麼說啦，可是如果要印很多份，還是要發出去，就會把零用錢花光光。不過，我想讓很多人都看到我的報紙啊！所以，我打算出一份「壁報」。在大大的紙上寫上新聞，然後找個地方貼上去就行啦！因為到處都有新聞，所以，寫新聞，也就是報紙的消息這方面，我根本不用煩惱，我馬上就寫了創刊號報紙。"
    tacotron2,fastspeech2,mb_melgan = load_model()
    e2e_tts(input_text, tacotron2,fastspeech2,mb_melgan)
    print("TTS done")

