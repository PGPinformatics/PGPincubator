# Minimal setup for running "ollama" with ROCm in container

The goal of this recipe is to set up the UM790XTX ("compute node") with a minimal installation of AMD/ROCm kernel modules, so that ROCm-based apps can run in containers. As an example, we will run "[ollama](https://ollama.com/)" compiled with ROCm support.

This setup is capable of automatically updating the kernel module for newly installed kernel, using the dkms mechanism.

# Install and configure support packages

## Install Ubuntu 22.04 on UM790XTX

First, make sure Ubuntu 22.04 is installed and up-to-date.

Note that the official ROCm installation documentation calls for [disabling the iGPU](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/prerequisites.html#disable-integrated-graphics-igp-if-applicable). In practice there's no evidence that this is necessary on the UM790XTX.

Make sure that the user has admin ("sudo") privileges.

## Install system tools and headers

Ensure that the following deb packages are installed.  
	`sudo apt install pciutils linux-headers-generic-hwe-22.04-edge "linux-modules-extra-$(uname -r)"`  
Some of these should be installed by default.

## Add user to GPU user groups

Reference: [https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/prerequisites.html\#setting-permissions-for-groups](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/prerequisites.html#setting-permissions-for-groups)

Check that the groups `video` and `render` exist:  
`getent group | grep -E 'video|render'`  
You should see both groups listed. If not, add them (most likely unnecessary)  
	`sudo groupadd -fr video`  
	`sudo groupadd -fr render`

Add the current user to these groups:  
	`sudo usermod -aG video,render "$(id -nu)"`

## Set up AMD/ROCm package repository

Follow the guides here for Ubuntu 22.04: [https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/native-install/ubuntu.html](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/native-install/ubuntu.html)  
Follow **only** the steps listed under "Registering ROCm repositories"

## Minimal installation of kernel modules

Do these:  
`sudo apt update`  
`sudo apt install amdgpu-dkms`

## Install Docker CE

Cf: [install Docker in guest](https://docs.google.com/document/d/1Groandn4iLw-2f6PGNlmQhdp5sO3K0LICnUw3RhMzEw/edit?pli=1&tab=t.0#bookmark=id.6ntsfczgor1g)

Follow the steps detailed in the article: [https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04)

Including the part about adding the current user to the docker group:  
	`sudo usermod -aG docker "$(id -nu)"`

## Update PCI manufacturer/product IDs (for convenience)

	`sudo update-pciids`

## Reboot computer

# Run ROCm-based docker containers

## Identify discrete GPU

Note that the UM790XTX should be attached to a functional discrete GPU via the OCuLink adapter (included) and dock. The card used as the example here is an Acer Nitro 7600XT, and the actual identifiers you see may be different.

First, do this:  
`sudo lspci | less`  
Search for the string "`ATI`" in the paged output (press `/` \[slash\], then type `ATI` \[in uppercase\], and Enter)

You should see something like this:

`05:00.0 PCI bridge: Advanced Micro Devices, Inc. [AMD/ATI] Navi 10 XL Upstream Port of PCI Express Switch (rev 12)`  
`06:00.0 PCI bridge: Advanced Micro Devices, Inc. [AMD/ATI] Navi 10 XL Downstream Port of PCI Express Switch (rev 12)`  
`07:00.0 VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Navi 33 [Radeon RX 7600/7600 XT/7600M XT/7600S/7700S / PRO W7600] (rev c0)`  
`07:00.1 Audio device: Advanced Micro Devices, Inc. [AMD/ATI] Navi 31 HDMI/DP Audio`  
`c8:00.0 VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Phoenix1 (rev c1)`  
`c8:00.1 Audio device: Advanced Micro Devices, Inc. [AMD/ATI] Rembrandt Radeon High Definition Audio Controller`

Here, you can see (highlighted) that the dGPU device is listed (you know this is the one, by the product model). Note the corresponding ID, in this case `07:00.0`.

The goal of this step is to identify the device. You can use whatever search terms that are sufficient for the job.

## Identify device files

Issue the command  
`ls -l /dev/dri/by-path`  
You should see something like this:  
`total 0`  
`lrwxrwxrwx 1 root root  8 Nov  1 10:45 pci-0000:07:00.0-card -> ../card1`  
`lrwxrwxrwx 1 root root 13 Nov  1 10:44 pci-0000:07:00.0-render -> ../renderD128`  
`lrwxrwxrwx 1 root root  8 Nov  1 10:44 pci-0000:c8:00.0-card -> ../card2`  
`lrwxrwxrwx 1 root root 13 Nov  1 10:44 pci-0000:c8:00.0-render -> ../renderD129`

Notice how the identifier found in the preceding step maps to the device files. In other words, we know that the path `/dev/dri/card1` refers to the dGPU card. (The other one is for the integrated graphics).

Ideally we should use the identifier to refer to the device for consistency; it might be possible that across reboots the serially-numbered path "card1" may refer to different cards. But there is a serious, long-standing issue with the docker command-line tool, namely it uses the colon character in device paths for other purposes and you can't escape it. In the following steps we may have to contend ourselves with designators like "card1".

## Download ollama Docker image

Do this:  
`docker pull ollama/ollama:rocm`

## Run containerized ollama from image

To run containerized ollama, we need to do some preparation, namely mapping the paths and device files.

### Create directories for ollama's working files

Pick a path and create it, for example:  
	`cd`  
	`mkdir ollama-home ollama-data`  
This will create the directory "`$HOME/ollama-home`" and "`$HOME/ollama-data`" to hold the containerized app's working files. Or, you may choose any other paths that make sense.

### Add alias for container-creation command

We need a command for creating ("running") a container from the image for the first time. This command must say which device files and ordinary file paths to map, along with other config options.

To do so, create an alias "`drun`" (based on "`docker run`"; you may choose a different name). Create the file `"$HOME/.bash_aliases"` if it does not exist (`touch "$HOME/.bash_aliases"`). Put the following line in it:

`alias drun='docker run -it --device=/dev/kfd --device=/dev/dri/card1 --device=/dev/dri/renderD128 --group-add=video --network=host --ipc=host --cap-add=SYS_PTRACE --security-opt seccomp=unconfined --shm-size 16G'`

Here, the highlighted parts (`card1` and `renderD128`) should be what we obtain from the step "[Identify device files](#bookmark=id.9dyu402bnbwf)".

For immediate effect, source the alias file:  
	`. "$HOME/.bash_aliases"`

### Create container

This step creates a container from the ollama image we [just pulled](#bookmark=id.gi8yeavhwati). We make use of the [alias](#bookmark=id.laricdrg2k9r) we just added.  
`drun -v "$HOME/ollama-home:/root/.ollama" -v "$HOME/ollama-data:/root/data" --name ollama-test ollama/ollama:rocm`

Explanation:

* The parts in lavender are [the paths we created](#bookmark=id.y5fvjtuefnh4) in our home directory that map to file paths inside the container (which is hard-coded by the container's definition file). The `-v` flag specifies path mappings.  
* The highlighted name **`ollama-test`** is the name of our container that we can refer to later.  
* The part `ollama/ollama:rocm` is the tag of the [downloaded Docker image](#bookmark=id.gi8yeavhwati) from which we just created the container **`ollama-test`**.

We have just created a live container running an instance of the `ollama` command-line tool, and this running app has access to our GPU for AI compute.

### Use container

In another shell session (terminal window, screen, etc.), we execute a command in the live container:  
	`docker exec -it ollama-test ollama run --verbose llama3.2`

To explain: this means "execute the command '`ollama run --verbose llama3.2`' in the live container **`ollama-test`** (i.e. the one we [just created](#bookmark=id.m82g7t2jnh3n)), with terminal attached".

The command "`ollama run --verbose llama3.2`" is all about using the "ollama" command-line tool. It runs the model "llama3.2" (with default tag) interactively. For the first run, it will pull the model data from ollama's own CDN. Then, when the model is loaded, you will see a message prompt (`>>>`), where you can type in "instructions" (chat messages) and let the model (chatbot) do inference (chat back). The highlighted part is the user input and everything after it is the output.

`>>> Greetings. Nice to meet you.`  
`Nice to meet you too! I'm happy to chat with you. Is there something`   
`specific you'd like to talk about, or would you like me to suggest some`   
`conversation topics?`

`total duration:       655.185454ms`  
`load duration:        14.513298ms`  
`prompt eval count:    32 token(s)`  
`prompt eval duration: 47.36ms`  
`prompt eval rate:     675.68 tokens/s`  
`eval count:           37 token(s)`  
`eval duration:        550.731ms`  
`eval rate:            67.18 tokens/s`

The output is non-deterministic so you may see something entirely different.

### Start and stop container

To stop the container, issue the command in a shell session:  
`docker stop ollama-test`  
This will terminate the container and reset its state (except for any side effects, such as files written to the working directories).

To restart the same container:  
	`docker start -ai ollama-test`  
The flags `-ai` will cause the current terminal to attach to the container's standard streams (i.e. it behaves more like a native command in shell).

A restarted container has its state reset but for the side effects. You don't have to re-map the files and devices (provided that the correct paths and device files are still there). The pulled model data will be retained as long as we didn't modify them outside the container.

Once restarted, we can re-use it by [executing](#bookmark=id.k0qb7jhf6icu) more commands.