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

tacotron2_config = AutoConfig.from_pretrained('TensorflowTTS/examples/tacotron2/conf/tacotron2.baker.v1.yaml')
tacotron2 = TFAutoModel.from_pretrained(
    config=tacotron2_config,
    pretrained_path="content/tacotron2-100k.h5",
    name="tacotron2"
)

fastspeech2_config = AutoConfig.from_pretrained('TensorflowTTS/examples/fastspeech2/conf/fastspeech2.baker.v2.yaml')
fastspeech2 = TFAutoModel.from_pretrained(
    config=fastspeech2_config,
    pretrained_path="content/fastspeech2-200k.h5",
    name="fastspeech2"
)

mb_melgan_config = AutoConfig.from_pretrained('TensorflowTTS/examples/multiband_melgan/conf/multiband_melgan.baker.v1.yaml')
mb_melgan = TFAutoModel.from_pretrained(
    config=mb_melgan_config,
    pretrained_path="content/mb.melgan-920k.h5",
    name="mb_melgan"
)

input_text = "仁宝电脑位于台北市内湖区阳光街三八五号"
# setup window for tacotron2 if you want to try
tacotron2.setup_window(win_front=5, win_back=5)
mels, alignment_history, audios = do_synthesis(input_text, tacotron2, mb_melgan, "TACOTRON", "MB-MELGAN")
sf.write('tacotron_melgan.wav', audios, 24000, 'PCM_24')
mels, audios = do_synthesis(input_text, fastspeech2, mb_melgan, "FASTSPEECH2", "MB-MELGAN")
sf.write('factspeech_melgan.wav', audios, 24000, 'PCM_24')