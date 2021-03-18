
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
from e2e_tts import load_model,e2e_tts

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

tacotron2,fastspeech2,mb_melgan = load_model()

@app.route('/tts', methods=['GET', 'POST'])
def do_tts():
    if request.method == 'POST':
        if not request.is_json:
            return 'Only json format is supported'
        data = request.get_json()
        if 'text' not in data:
            return 'Your POST data must contain \'text\' key'
        text = data['text']
        e2e_tts(text, tacotron2,fastspeech2,mb_melgan)        
        return "TTS done\n"
    else:
        return 'GET method is not supported here.'

if __name__ == "__main__":
    app.run(args.address, args.port)

