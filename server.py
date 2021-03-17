
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
from flask import Flask, request
import json
import argparse
import uuid
from opencc import OpenCC
import zhon.hanzi as hanzi
import re

parser = argparse.ArgumentParser()
parser.add_argument('--address',
                    default='0.0.0.0',
                    type=str,
                    required=False,
                    help='Designate which address your app will listen to. Default is 0.0.0.0 which means listen to all address.')      
parser.add_argument('--port',
                    default=8080,
                    type=int,
                    required=False,
                    help='Designate which port your app will listen to. Default is 8080.')           

args = parser.parse_args()
app = Flask(__name__)

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

cc = OpenCC('t2s')
def sec2numpy(sec):
    return np.zeros(int(24000*sec))

@app.route('/tts', methods=['GET', 'POST'])
def do_tts():
    #logger.info('Get request')
    uuidcode = uuid.uuid4().hex
    if request.method == 'POST':
        if not request.is_json:
            return 'Only json format is supported'
        data = request.get_json()
        if 'text' not in data:
            return 'Your POST data must contain \'text\' key'
        text = data['text']
        
        #input_text = "玉山金旗下玉山銀行今日宣布數位金融服務再升級"
        input_text =  cc.convert(text)
        #input_text = text
        input_list = re.split('['+hanzi.punctuation+']',input_text)
        tacotron2.setup_window(win_front=5, win_back=5)
        au1 = np.array([])
        au2 = np.array([])
        for idx, txt in enumerate(input_list):
            mels, alignment_history, audios = do_synthesis(txt, tacotron2, mb_melgan, "TACOTRON", "MB-MELGAN")
            au1 = audios  if idx == 0 else np.concatenate((au1,sec2numpy(0.1), audios),axis=0)
            mels, audios = do_synthesis(txt, fastspeech2, mb_melgan, "FASTSPEECH2", "MB-MELGAN")
            au2 = audios  if idx == 0 else np.concatenate((au2,sec2numpy(0.1),audios),axis=0)
        
        sf.write('./output/'+str(uuidcode)+ '_tacotron.wav', au1, 24000, 'PCM_24')
        sf.write('./output/'+str(uuidcode)+ '_factspeech.wav', au2, 24000, 'PCM_24')
            
        return "TTS done\n"
    else:
        return 'GET method is not supported here.'

if __name__ == "__main__":
    #logger.info(f'Listening to {args.address} at {args.port}...')
    app.run(args.address, args.port)

