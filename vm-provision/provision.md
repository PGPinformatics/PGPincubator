# Notes on early VM provisioning

This allows you to take a brand newly born baby virtual machine image
knowing nothing more than the root partition encryption key and root
password and do the early stage provisioning, specifically:

* Setting the hostname
* Connecting to Tailnet

# Image customization

This needs to happen in the "conception" stage of the VM image, before
it is cloned and further provisioned.

Edit `/etc/default/grub` and make sure these are set:

```
GRUB_TIMEOUT=3
GRUB_CMDLINE_LINUX="console=ttyS0"
```

Then run `update-grub` and save the image.

# Qemu command line

Example qemu command line to run a VM with UEFI:

```
exec qemu-system-x86_64 \
 -name guest=ubuntu24.04-local-img,debug-threads=on \
 -blockdev '{"driver":"file","filename":"/usr/share/OVMF/OVMF_CODE_4M.ms.fd","node-name":"libvirt-pflash0-storage","auto-read-only":true,"discard":"unmap"}' \
 -blockdev '{"node-name":"libvirt-pflash0-format","read-only":true,"driver":"raw","file":"libvirt-pflash0-storage"}' \
 -blockdev '{"driver":"file","filename":"/var/lib/libvirt/qemu/nvram/ubuntu24.04-local-img_VARS.fd","node-name":"libvirt-pflash1-storage","auto-read-only":true,"discard":"unmap"}' \
 -blockdev '{"node-name":"libvirt-pflash1-format","read-only":false,"driver":"raw","file":"libvirt-pflash1-storage"}' \
 -machine pc-q35-6.2,accel=kvm,usb=off,vmport=off,smm=on,dump-guest-core=off,pflash0=libvirt-pflash0-format,pflash1=libvirt-pflash1-format \
 -m 16000 \
 -smp 2 \
 -blockdev '{"driver":"file","filename":"/home/peter/work/hbar-image/hbar-image-2025-march.working1.raw","node-name":"libvirt-1-storage","auto-read-only":true,"discard":"unmap"}' \
 -blockdev '{"node-name":"libvirt-1-format","read-only":false,"driver":"raw","file":"libvirt-1-storage"}' \
 -device ide-hd,bus=ide.0,drive=libvirt-1-format,id=sata0-0-0,bootindex=1 \
 -chardev stdio,id=charserial0 \
 -device isa-serial,chardev=charserial0,id=serial0 \
 -display none
```

This will run the virtual machine with the with the Linux console
going to a virtual serial console attached to stdin/stdout.  You can
type in the root decryption password, log in as root, and then do
whatever essential setup is necessary to bootstrap to be able to use
the primary setup tools (e.g. ansible).

The next step will be to write a script to run qemu in a subprocess
and do all this automatically.

## Qemu command line breakdown

Mounting the emulated UEFI firmware image (this image comes with qemu, I think):

```
 -blockdev '{"driver":"file","filename":"/usr/share/OVMF/OVMF_CODE_4M.ms.fd","node-name":"libvirt-pflash0-storage","auto-read-only":true,"discard":"unmap"}'
 -blockdev '{"node-name":"libvirt-pflash0-format","read-only":true,"driver":"raw","file":"libvirt-pflash0-storage"}' \
 ```

Mounting the emulated non-volatile memory used by UEFI:

TODO: Figure out how to create this file initially.

```
 -blockdev '{"driver":"file","filename":"/var/lib/libvirt/qemu/nvram/ubuntu24.04-local-img_VARS.fd","node-name":"libvirt-pflash1-storage","auto-read-only":true,"discard":"unmap"}' \
 -blockdev '{"node-name":"libvirt-pflash1-format","read-only":false,"driver":"raw","file":"libvirt-pflash1-storage"}' \
```

Specify the machine type is UEFI (pc-q35-6.2), and set pflash0/pflash1 for UEFI.

```
 -machine pc-q35-6.2,accel=kvm,usb=off,vmport=off,smm=on,dump-guest-core=off,pflash0=libvirt-pflash0-format,pflash1=libvirt-pflash1-format
```

Give it 16000 MiB of RAM and 2 cores:

```
 -m 16000 \
 -smp 2 \
```

Mount the raw image file as an IDE device (change the file to point to something else):

```
 -blockdev '{"driver":"file","filename":"/home/peter/work/hbar-image/hbar-image-2025-march.working1.raw","node-name":"libvirt-1-storage","auto-read-only":true,"discard":"unmap"}' \
 -blockdev '{"node-name":"libvirt-1-format","read-only":false,"driver":"raw","file":"libvirt-1-storage"}' \
 -device ide-hd,bus=ide.0,drive=libvirt-1-format,id=sata0-0-0,bootindex=1 \
```

Set up a serial console which is attached to the stdin/stdout of qemu:

```
 -chardev stdio,id=charserial0 \
 -device isa-serial,chardev=charserial0,id=serial0 \
```

Finally, disable display (because we're using the serial console only).

```
 -display none
```
