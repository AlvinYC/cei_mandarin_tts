FROM tensorflow/tensorflow:2.3.1-gpu
MAINTAINER alvin

# account info (pwd is not necessary for this config)
ARG user=docker
#ARG pwd=1234
#this script will create dir to  /home/{$user}/${worddir} like /home/docker/git_repository
#ARG workdir=workspace
#some large package should copy to /home/${user}/$(local_package}
ARG local_package=utils_thisbuild
ARG github=cei_mandarin_tts
#vscode server 1.54.2
ARG vscommit=fd6f3bce6709b121a895d042d343d71f317d74e7

# udpate timezone
RUN apt-get update \
    &&  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata

RUN TZ=Asia/Taipei \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata 

# init.
RUN apt-get update && apt-get install -y \
    apt-utils sudo vim zsh curl git make unzip \
    wget openssh-server \
    powerline fonts-powerline \
    # necessary ubuntu package for sudo add-apt-repository ppa:deadsnakes/ppa
    software-properties-common \
    # zsh by ssh issue : icons.zsh:168: character not in range
    language-pack-en \
    libsndfile1 \
    jupyter-notebook  

RUN useradd -m ${user} && echo "${user}:${user}" | chpasswd && adduser ${user} sudo;\
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers;\
    chmod 777 /etc/ssh/sshd_config; echo 'GatewayPorts yes' >> /etc/ssh/sshd_config; chmod 644 /etc/ssh/sshd_config

USER ${user}
WORKDIR /home/${user}

# oh-my-zsh setup
ARG omzthemesetup="POWERLEVEL9K_MODE=\"nerdfont-complete\"\n\
ZSH_THEME=\"powerlevel9k\/powerlevel9k\"\n\n\
POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(pyenv virtualenv context dir vcs)\n\
POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(status root_indicator background_jobs history time)\n\
POWERLEVEL9K_VIRTUALENV_BACKGROUND=\"green\"\n\
POWERLEVEL9K_PYENV_PROMPT_ALWAYS_SHOW=true\n\
POWERLEVEL9K_PYENV_BACKGROUND=\"orange1\"\n\
POWERLEVEL9K_DIR_HOME_SUBFOLDER_FOREGROUND=\"white\"\n\
POWERLEVEL9K_PYTHON_ICON=\"\\U1F40D\"\n"

RUN cd ~/ ; mkdir .ssh ;\
    sudo mkdir /var/run/sshd ;\
    sudo sed -ri 's/session required pam_loginuid.so/#session required pam_loginuid.so/g' /etc/pam.d/sshd ;\
    sudo ssh-keygen -A ;\
    #sudo service ssh start ;\
    wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true ;\
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ~/.oh-my-zsh/plugins/zsh-syntax-highlighting ;\
    git clone https://github.com/bhilburn/powerlevel9k.git ~/.oh-my-zsh/custom/themes/powerlevel9k ;\
    git clone https://github.com/zsh-users/zsh-autosuggestions ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions ;\
    git clone https://github.com/davidparsson/zsh-pyenv-lazy.git ~/.oh-my-zsh/custom/plugins/pyenv-lazy ;\
    echo "source ~/.oh-my-zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" >> ~/.zshrc ;\
    sed -i -r "1s/^/export TERM=\"xterm-256color\"\n/" ~/.zshrc ;\
    sed -i -r "2s/^/LC_ALL=\"en_US.UTF-8\"\n/" ~/.zshrc ;\
    sed -i -r "s/^plugins=.*/plugins=(git zsh-autosuggestions virtualenv screen pyenv-lazy)/" ~/.zshrc ;\
    sed -i -r "s/^ZSH_THEM.*/${omzthemesetup}/" ~/.zshrc ;\
    wget https://github.com/ryanoasis/nerd-fonts/releases/download/v2.1.0/SourceCodePro.zip ;\
    unzip SourceCodePro.zip -d ~/.fonts ;\
    fc-cache -fv  ;\
    sudo chsh -s $(which zsh) ${user}

# python package setup
ARG cudapathsetup="alias python=\'python3\'\n\
alias pip=\'pip3\'\n\
alias watch1=\'watch -n 0.5\'\n\
#export PATH=\"/usr/local/cuda/bin:$PATH\"\n\
export PATH=\"/home/${user}/.local/bin:$PATH\"\n\
export LD_LIBRARY_PATH=\"/usr/local/cuda/lib64:$LD_LIBRARY_PATH\""



#RUN export PATH="/home/${user}/.local/bin:$PATH";\
#    sudo add-apt-repository ppa:deadsnakes/ppa -y
#RUN sudo apt-get update -y; \
#    sudo apt-get autoremove python3.5 -y; \
#    sudo apt-get install python3.6 -y;\
#    sudo apt-get install python3-pip -y;\
#    echo ${cudapathsetup} >> ~/.zshrc;\
#    cd /usr/bin; sudo unlink python3; sudo ln -s python3.6 python3; \
#    sudo unlink python; sudo ln -s python3.6 python; cd ~/ ;\
#    mkdir ${workdir}; mkdir ${local_package};\
#    cd ${workdir}
 
# numpy=1.19.4, pytorch=1.5, torchvision=0.6
RUN python3 -m pip install --upgrade pip;\
    python3 -m pip install ipython==7.16.1;\
    python3 -m pip install Flask==1.1.2;\
    python3 -m pip install opencc-python-reimplemented==0.1.6;\
    python3 -m pip install zhon==1.1.5;\
    python3 -m pip install pycnnum==1.0.1;\
    # project git clone
    git clone https://github.com/AlvinYC/${github}.git /home/${user}/${github};\
    # fix pycnnum issue, ref: https://github.com/zcold/pycnnum/issues/4
    sed -ir 's/return \[system\.digits\[0.*/return \[system.digits\[0\], system.digits\[int\(striped_string\)\]\]/' \
    /home/${user}/.local/lib/python3.6/site-packages/pycnnum/pycnnum.py


#RUN mkdir /home/${user}/${workdir}; mkdir /home/${user}/${local_package}
COPY ${local_package} /home/${user}/${local_package}
RUN sh /home/${user}/${local_package}/project_setup.sh

#WORKDIR /home/${user}/${github}/TensorFlowTTS
RUN python3 -m pip install ./${github}/TensorFlowTTS/. 

# vscode server part
RUN curl -sSL "https://update.code.visualstudio.com/commit:${vscommit}/server-linux-x64/stable" -o /home/${user}/${local_package}/vscode-server-linux-x64.tar.gz;\
    mkdir -p ~/.vscode-server/bin/${vscommit};\
    tar zxvf /home/${user}/${local_package}/vscode-server-linux-x64.tar.gz -C ~/.vscode-server/bin/${vscommit} --strip 1;\
    touch ~/.vscode-server/bin/${vscommit}/0

# jupyter notebook config
RUN jupyter notebook --generate-config;\
    sed -ir "s/\#c\.NotebookApp\.token.*/c\.NotebookApp\.token = \'\'/" ~/.jupyter/jupyter_notebook_config.py;\
    sed -ir "s/#c\.NotebookApp\.password =.*/c\.NotebookApp\.password = u\'\'/" ~/.jupyter/jupyter_notebook_config.py;\
    sed -ir "s/#c\.NotebookApp\.ip = .*/c\.NotebookApp\.ip = \'\*\'/" ~/.jupyter/jupyter_notebook_config.py;\
    sed -ir "s/#c\.NotebookApp\.notebook_dir.*/c\.NotebookApp\.notebook_dir = \'\/home\/docker\/cei_mandarin_tts\'/" ~/.jupyter/jupyter_notebook_config.py
 
ADD id_rsa.pub /home/${user}/.ssh/authorized_keys

ENTRYPOINT sudo service ssh restart && zsh
                    

