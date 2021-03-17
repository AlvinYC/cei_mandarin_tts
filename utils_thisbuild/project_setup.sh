cd ~/
#sh -c 'mv utils_thisbuild content'
sh -c 'mkdir -p ~/content'
cd ~/content
sh -c 'ln -s ~/utils_thisbuild/model-100000.h5 tacotron2-100k.h5'
sh -c 'ln -s ~/utils_thisbuild/model-200000.h5 fastspeech2-200k.h5'
sh -c 'ln -s ~/utils_thisbuild/generator-920000.h5 mb.melgan-920k.h5'
sh -c 'ln -s ~/utils_thisbuild/baker_mapper.json baker_mapper.json'
# merge all id_rsa.pub into this container
#sh -c 'cat /home/docker/utils_thisbuild/*pub > /home/docker/.ssh/authorized_keys'

