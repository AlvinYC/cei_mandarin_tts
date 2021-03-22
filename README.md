# cei_mandarin_tts
# useage
    - git clone ${this_github}
    - docker build taco .
    after clone this github, file struce will like this

    you shoud prepare some files
    
    ```
                .
        ├── Dockerfile
        ├── docker_run.txt
        ├── e2e_tts.py
        ├── id_rsa.pub                  # (1) ssh public key in your devcelop pc
        ├── README.md
        ├── server.py
        ├── server_web.ipynb
        ├── synthesiser.py
        ├── TensorFlowTTS
        └── utils_thisbuild          #  some model file or bug size file not in gitub
            ├── baker_mapper.json        #(2) Baker Mapper Json https://drive.google.com/uc?id=1cS8jNEgovxUNuCVQSOM68HujrzMGKXNB
            ├── generator-920000.h5      #(3) MelGan Vocoder https://drive.google.com/uc?id=17Db2R2k8mJmbO5utX80AVK8ssAr-JpCB
            ├── model-100000.h5             #(4) Tacoton model https://drive.google.com/uc?id=1n36vcrEPQ0SyL7wVrYsNVrPiuGhiOF4h
            ├── model-200000.h5             #(5)  Fastspeech model https://drive.google.com/uc?id=1PAFpsILkih5zSTbYQw-hpAe5eaNJh0hb
            ├── project_setup.sh
            └── vscode-server-linux-x64.tar.gz #(6) VS coder server 1.54.2 commit=fd6f3bce6709b121a895d042d343d71f317d74e7

    ```
## run as service
        * flask
            - [server side] docker run -it --rm --gpus=all  -p 7788:22 -p 8080:8080 -v any_where_in_your_pc:/home/docker/cei_mandarin_tts/output --name taco taco:lates
            - [docker side] python server.py
            - [client side] curl -X POST -H "Content-type: application/json" -d '{"text":"中市加速淘汰烏賊車　中低收換購 電動機車最高補助四萬"}' localhost:8080/tts
            - playing wav on audio player in your pc
        * jupyter  notebook
            - [server side] docker run -it --rm --gpus=all  -p 7788:22-p 8888:88888 -v any_where_in_your_pc:/home/docker/cei_mandarin_tts/output --name taco taco:lates
            - [docker side] jupyter notebook
            - [clinet side] http://server_ip:8888
            - playing wav on browser


# reference
 1. https://colab.research.google.com/drive/1YpSHRBRPBI7cnTkQn1UcVTWEQVbsUm1S?usp=sharing
