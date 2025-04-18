# Guide for running the guest-to-host GPU-enabled pipeline with llamafile

1. Install Arvados deb packages built from from Peter's branch; PDH `49939a7635fc2caa67271dfd3a2e77a9+3329`; jutro link [https://workbench.jutro.arvadosapi.com/collections/jutro-4zz18-iyvwwdiyn21r2fx](https://workbench.jutro.arvadosapi.com/collections/jutro-4zz18-iyvwwdiyn21r2fx)
* Inside the Arvados guest, replace all installed Arvados packages with the ones from above; preferably do "sudo `apt-mark hold [packages]`" to pin their current version and prevent inadvertent updates.
* On the host, install (and preferably hold) the following packages from the above collection:
  * `crunch-dispatch-local`
  * `crunch-run`
  * `python3-arvados-fuse`
* For consistency and compatibility, any client and SDK tools used, no matter where (guest, host, or 3rd-party client-only system), should be replaced by the deb packages from above.

2. Keep a copy of the `arvados/jobs` Docker image with the right version tag in the guest Arvados Keep; PDH `363b1be5743f2d0686bc40ce7871cca0+555`; jutro link [https://workbench.jutro.arvadosapi.com/collections/jutro-4zz18-bsygftrqe1mnota](https://workbench.jutro.arvadosapi.com/collections/jutro-4zz18-bsygftrqe1mnota)

3. On the host, get a copy of the guest's self-signed CA certificate and add it to trusted certs: put it under `/usr/local/share/ca-certificates` and then
   `sudo update-ca-certificates`

4. On the host, make sure Docker containers **can resolve hostnames**, global and local, inside them \[TBD: FIND THE BEST WAY\]
* Currently, on my host, I am making Docker containers be attached to the bridge that also connects to the virtual machine guests. And this hard-coded DNS setting in the /etc/docker/daemon.json config file

  `{`

  	`"bridge": "virbr0",`

  	`"dns": ["192.168.122.1"],`

  	`"dns-search": ["vir-test.home.arpa"]`

  `}`

  Here `virbr0` is the bridge device for the virtual machine systems, the IP address is the bridge's (where the DNS server for the virtual machine network also listens), and the search domain is for the same VM network.


  Then, restart the Docker service:

  `sudo systemctl restart docker.service`

5. On the host, save a copy of the Arvados 'cluster' config file (the one from the guest) at the usual location `/etc/arvados/config.yml`

6. On the host, create a configuration file for local dispatcher service.
* Locate the GPU device file(s), see [the detailed guide](Minimal-install-of-AMD-ROCm-for-Docker-images.md).
* Create the config file at `/etc/arvados/crunch-dispatch-local-credentials`
* Put in the config file a line like this

  `AMD_VISIBLE_DEVICES=N`

  where *`N`* is the number for the device – if the card corresponds to `/dev/dri/renderD128`, *`N`* would be `0`; for higher device numbers *`N`* is the number minus 128\. If there are more than one device usable, separate their numbers by a comma (e.g. `AMD_VISIBLE_DEVICES=0,1`)

7. Replace the running `crunch-dispatch-local` services
* On the guest, stop and disable it:

  `sudo systemctl disable --now crunch-dispatch-local.service`

*  On the host, enable and start it:

  `sudo systemctl enable --now crunch-dispatch-local.service`

Now, the guest–host combination will be able to run functional Docker containers on the host at the behest of the pipelines on the guest Arvados system. Step 6 above enables GPU support for containers.

---

The rest of this guide focuses on running pipelines based on "llamafile" executing on the host with GPU support.

### Build llamafile Docker image

First, we build a Docker image for containerized llamafile. The Dockerfile can be found in this collection [https://workbench.jutro.arvadosapi.com/collections/jutro-4zz18-ecsf14ky3376maw](https://workbench.jutro.arvadosapi.com/collections/jutro-4zz18-ecsf14ky3376maw), and the built image should be tagged `Mozilla-Ocho/llamafile` to be used by the CWL tools and workflows to be described. **On the host**, in a directory containing the Dockerfile (the build context), run
`docker build -t Mozilla-Ocho/llamafile .`

### Create and use shims

When a llamafile is run (either as the standalone executable with the "`.llamafile`" extension, or using the "`llamafile`" command), it expects there to be "shims" (binary shared libs) compiled for the native architecture. If the shims are not there, it will compile them and cache them. If the wrong shims are there, it will fail. Shims can be "wrong" because, for example, they're not compiled for the GPU architecture currently being used.

Normally, the shim sources and the compiled binary are cached in the home directory. When running in a container, the exact location will depend on whether and how the home directory is bound.

In CWL workflows as shared here: [https://workbench.jutro.arvadosapi.com/collections/jutro-4zz18-qvvvjxupclf1jl1](https://workbench.jutro.arvadosapi.com/collections/jutro-4zz18-qvvvjxupclf1jl1), the parameter "`llamadir`" should refer to the shims directory that corresponds to the "`$HOME/.llamafile`" directory, generated when run independently outside the container.

1. One way to guarantee that the llamafiles run with proper GPU support is to set the references to `llamadir` parameter to null in the parameter files such as "`mistral.yml`" and "`llama-3.2.yml`". This will cause the shims to be generated anew and used. Then, after completion of a run, the llamadir (which contains the shims directory "`.llamafile`") can be located in the output and referred to in the parameter files.

2. Another way is to generate them separately and put them in Keep. On the host, using the `Mozilla-Ocho/llamafile` image described above.
* First prepare an empty directory and `cd` into it.
* Locate a llamafile or .gguf file on the host to be run by the container. Move or copy or link the file into the current directory.
* Run the command

`docker run -it --rm --device /dev/kfd --device /dev/dri/renderD128 -v "${PWD}:/root" Mozilla-Ocho/llamafile sh -c 'llamafile -m /root/[relative-path-to-llamafile/gguf] -ngl 999'`
Here the device corresponds to the graphic card to use; [see above](#bookmark=id.uty0gnruwudz).

* The shims will be compiled in the current directory on the host. You may need to modify the ownership and access rights so you can read them.
* To upload them to Arvados Keep, use

  `arv-put [--name COLLECTION_NAME] .llamafile`

* In the CWL parameter (.yml) files, the `llamadir` parameter can now refer to the uploaded directory by keep locator.
