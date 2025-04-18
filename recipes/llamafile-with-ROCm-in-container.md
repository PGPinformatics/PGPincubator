# llamafile with ROCm and GPU in container

The goal of this recipe is to create a Docker image with the necessary dependencies so that llamafile (compiled-in or external weights) can run with AMD GPU support.

# Prerequisites

For this to be done, on the host machine we must install Docker and the relevant AMDGPU kernel module. If you start from the state of the UM790XTX after completing the [ollama recipe](https://docs.google.com/document/d/1T_jKeg15AKtY30zkIHjFOxBWcXiarEPfvvW5plUzvAw/edit?usp=sharing), the prerequisites will have already been met.

Please read "[Add user to GPU groups](https://docs.google.com/document/d/1T_jKeg15AKtY30zkIHjFOxBWcXiarEPfvvW5plUzvAw/edit?tab=t.0#bookmark=id.ih850846amgs)", "[Set up AMD/ROCm package repository](https://docs.google.com/document/d/1T_jKeg15AKtY30zkIHjFOxBWcXiarEPfvvW5plUzvAw/edit?tab=t.0#bookmark=id.wcptf6f1yozc)", "[Minimal installation of kernel modules](https://docs.google.com/document/d/1T_jKeg15AKtY30zkIHjFOxBWcXiarEPfvvW5plUzvAw/edit?tab=t.0#bookmark=id.ewjgkdl2fg1k)", and "[Install Docker CE](https://docs.google.com/document/d/1T_jKeg15AKtY30zkIHjFOxBWcXiarEPfvvW5plUzvAw/edit?tab=t.0#bookmark=id.xzsgubi33iiy)" from the abovementioned guide.

# Build llamafile Docker image

First create a working directory, let's say `$HOME/llamafile-docker`  
	`mkdir "$HOME/llamafile-docker"`  
	`cd "$HOME/llamafile-docker"`  
Download the Dockerfile  
`wget https://gist.githubusercontent.com/zoe-translates/57d5ede0c9670f028525c240681a3cba/raw/d5350c4167ba1a900700ba7918cec781e28501f1/hip-libraries-rocm-ubuntu.Dockerfile`

(The Dockerfile is based on [an example from ROCm](https://github.com/ROCm/rocm-examples/blob/cfbca5428e4b7ee8abde583073fe1351fdf24d5c/Dockerfiles/hip-libraries-rocm-ubuntu.Dockerfile).)

Build the Docker image:  
	`docker build . -f hip-libraries-rocm-ubuntu.Dockerfile -t llbase`

Explanation:

* `.` (dot): current directory, as the **build context**.  
* `-f`: path to the Dockerfile we just downloaded.  
* `-t llabse`: "`llbase`" is the **tag** we use to refer to the built image. You can name it something else.

The output of docker images will show the image, in the following form  
`REPOSITORY        TAG              IMAGE ID       CREATED        SIZE`  
`llbase            latest           354a7aba1719   4 hours ago    10.5GB`

(The actual hash value may vary.)

## Note on using proxy server while building image

While building the image, certain commands that run in the container have download packages and source files from the internet. If a proxy server is necessary, we can set it with a build argument:  
	`docker build --build-arg MY_PROXY=http://host.x.y.z:port . -f hip-libraries-rocm-ubuntu.Dockerfile -t llbase`

## What these build processes do

The first stage is to compile llamafile's source code. llamafile's build process will download Justine's [Cosmopolitan](https://github.com/jart/cosmopolitan) C library and create single-file binary executables such as the `llamafile` command itself.

Meanwhile, the second stage starts with an Ubuntu Jammy base image and install the necessary packages for ROCm runtime and compiler tools.

Finally, the executables built in the first stage are copied over to the second-stage base image. The root user's home directory `/root` inside the container will be used as llamafile workspace.

# Run llamafile in containers

## Recap: using GPU in container

In the Ollama guide, [we created a shell-command alias](https://docs.google.com/document/d/1T_jKeg15AKtY30zkIHjFOxBWcXiarEPfvvW5plUzvAw/edit?tab=t.0#bookmark=id.laricdrg2k9r) to simplify the incantation bringing GPU to containers. In this recipe the same `drun` alias will be used again.

## Create working directory for (usually large) files

The `llbase` image has the root user's home (`/root`) intended to be mapped from a directory in the host (i.e. outside the container). llamafile will store temporary intermediate files there, saving much time when launching the same llamafile in different containers.

E.g. let's create a directory "$HOME/llamafile-wd"  
	`cd`  
	`mkdir llamafile-wd`  
	`cd llamafile-wd`

## Start container

In that directory, invoke `drun` (alias of a long `docker run` command)  
`drun -v "${PWD}:/root" --name llexec llbase`  
This will create the container `llexec` from the image `llbase`.  
   
We should see a shell prompt.

## Run pre-built llamafiles

In another shell session from the host, we can download a pre-built llamafile and have the container execute it. For example, a small llamafile from [Mozilla's official repo](https://huggingface.co/Mozilla/Llama-3.2-1B-Instruct-llamafile/tree/main):

`wget https://huggingface.co/Mozilla/Llama-3.2-1B-Instruct-llamafile/resolve/main/Llama-3.2-1B-Instruct.Q6_K.llamafile`

Then, after the download is complete, make it executable inside the container and run it:  
`chmod +x Llama-3.2-1B-Instruct.Q6_K.llamafile`  
`./Llama-3.2-1B-Instruct.Q6_K.llamafile -ngl 999`  
The output, after some compilation steps, will look like this:

`██╗     ██╗      █████╗ ███╗   ███╗ █████╗ ███████╗██╗██╗     ███████╗`  
`██║     ██║     ██╔══██╗████╗ ████║██╔══██╗██╔════╝██║██║     ██╔════╝`  
`██║     ██║     ███████║██╔████╔██║███████║█████╗  ██║██║     █████╗`  
`██║     ██║     ██╔══██║██║╚██╔╝██║██╔══██║██╔══╝  ██║██║     ██╔══╝`  
`███████╗███████╗██║  ██║██║ ╚═╝ ██║██║  ██║██║     ██║███████╗███████╗`  
`╚══════╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝`  
**`software`**`: llamafile 0.8.16`  
**`model`**`:    Llama-3.2-1B-Instruct.Q6_K.gguf`  
**`compute`**`:`    
**`server`**`:   http://127.0.0.1:8080/`  
`A chat between a curious human and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the human's questions.`  
`>>> say something (or type /help for help)`

## Run model with external weights (in GGUF)

Inside the container, we have built the `llamafile` executable that can be used to load model weights and run them.

For example, we can download a GGUF file into the working directory  
`wget https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q8_0.gguf`

Then, after downloading it, in the container we execute  
`llamafile -ngl 999 -m Meta-Llama-3.1-8B-Instruct-Q8_0.gguf`

## (TBA) Create new llamafile from model weights

TBA (see: [https://github.com/Mozilla-Ocho/llamafile?tab=readme-ov-file\#creating-llamafiles](https://github.com/Mozilla-Ocho/llamafile?tab=readme-ov-file#creating-llamafiles))

## Persistence of compiled loader binaries

The first time a llamafile is run, native loaders and library binaries will be compiled and saved in the root user's home (`/root`). The llamafile mechanism does some complex and smart run-time compilation and "make"-like caching (?), and seems to be able to reuse some of these binary props. I haven't investigated this in depth.

# Notes

To check that the model is actually loaded into VRAM (i.e. we're really using the GPU), use `radeontop` (`sudo apt install radeontop`) or [LACT](https://github.com/ilya-zlobintsev/LACT) (GUI). To use `radeontop`, first identify the PCI bus ID of the card (cf. [using `lspci`](https://docs.google.com/document/d/1T_jKeg15AKtY30zkIHjFOxBWcXiarEPfvvW5plUzvAw/edit?tab=t.0#bookmark=id.9k09zx7mzoa)). In the example listed there, the bus no. is 7, so invoke the tool as `radeontop -b7`

Note that speed (token rate of inference) alone is not sufficient evidence that the model is being run in GPU. A very small model may run much faster in CPU than in GPU, due to memory bandwidth.

# Problems

* The built image is huge. There's considerable bloat.