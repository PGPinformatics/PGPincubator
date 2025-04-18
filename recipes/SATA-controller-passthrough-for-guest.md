# SATA controller passthrough for guest

# Purpose

This note describes how to assign a SATA controller to the guest for its exclusive use. To maintain data encryption at rest, the hard drives are encrypted with LUKS. This means that when the host is powered down, the guest's data on the disk cannot be read.

# Pass SATA controller through

It is straightforward to do this with VirtManager. For the SATA controller, handing-off happens automatically when the guest is booted. There's no special setup on the host necessary.

Using Virtual Machine Manager (VirtManager) GUI, in the virtual machine guest's details page, click on "Add Hardware", and in the next step, choose "PCI Host Device", followed by the actual device to pass through. Finish adding the SATA controller and save/apply.

## Disk setup in guest

The **rest of the instructions** are meant to be carried out inside the **guest**.

## Prepare encryption key file

As root, create a random data file of 2048 bytes for use as disk encryption key  
`# dd if=/dev/random of=~/.extkey bs=512 count=4`  
`# chmod 400 ~/.extkey`

## Install system tools

`# apt install cryptsetup-bin lvm2`

## Format block device with LUKS

First, examine the hard drive block device files exposed to the guest. In the rest of the guide, we will use "`/dev/sda`" as a stand-in for (one of) the drive(s). The drive letter is not vital (we will be using UUIDs) but is used here as a human-friendly name.

`# cryptsetup luksFormat /dev/sda ~/.extkey`

(Type literal YES at the prompt)

Here in the command line we are referring to the key file just created.

## Open (unlock) drive block device

`# cryptsetup --key-file ~/.extkey luksOpen /dev/sda sda_crypt`

This creates the block device corresponding to the decrypted drive. The name "sda\_crypt" is not special, but just for human-readability.

## Make use of decrypted drive (with LVM)

`# pvcreate /dev/mapper/sda_crypt`  
`# vgcreate vgguesthd1 /dev/mapper/sda_crypt`  
`# lvcreate -l '100%FREE' -n lvguesthd1 vgguesthd1 /dev/mapper/sda_crypt`

These commands make the *decrypted* block device a physical volume (PV) and create a volume group (VG) with one logical volume (LV). The LV is functionally roughly the equivalent of a partition.

Here "`vgguesthd1`" is the VG name and "`lvguesthd1`" is the LV name, used as examples.

### Create EXT4 file system on LV

(see [how to do this with preinitialization](https://docs.google.com/document/d/1wi-fUvOltceBCv0SpwhVRbl2lsmGk3vntfvhtnBi810/edit?usp=sharing))  
`# mkfs.ext4 -c -E lazy_itable_init=0,lazy_journal_init=0 /dev/mapper/vgguesthd1-lvguesthd1`

Note that you can refer to the LV block device as `/dev/mapper/[VG name]-[LV name]`, among other ways.

### Make FS automatically mounted upon guest start

#### Make mount points

`# mkdir -p /data/guesthd1`

#### Configure `crypttab` and `fstab` with block device UUIDs

For the encrypted drive (underlying encrypted physical drive)  
`# blkid /dev/sda`  
`/dev/sda: UUID="[DRIVE_UUID]" TYPE="crypto_LUKS"`

Edit `/etc/crypttab` (create if missing) with the following line  
`sda_crypt UUID=[DRIVE_UUID] /root/.extkey luks,noearly`

For the logical volume (like a partition on which a FS exists):  
`# blkid /dev/mapper/vgguesthd1-lvguesthd1`  
`[output with UUID for the LV]`

Edit `/etc/fstab`, append to the file  
`UUID=[LV_UUID]	/data/guesthd1	ext4	defaults,noinit_itable	0	2`

#### Try out

`# mount -a`

Reboot the guest, and the hard drive should be mounted automatically.