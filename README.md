# cei_mandarin_tt

# running flask
* docker server
    ```
    docker run -it --rm --gpus=all -p 7788:22 -p 8080:8080 -v /home/alvin/git_repo_alvin/cei_mandarin_tts/output:/home/docker/cei_mandarin_tts/output --name taco taco:latest
    ```

* container server side
    ```
    sudo python server.py
    ```
* client side
    ```
    curl -X POST -H "Content-type: application/json" -d '{"text":"中市加速淘汰烏賊車　中低收換購 電動機車最高補助四萬"}' localhost:8080/tts

    ```
