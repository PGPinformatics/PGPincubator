How to create a Memtest86+ bootable USB stick.

Why? Because the current Ubuntu 22.04 live USB image doesn't include a functional Memtest86+ bootable option that may work with UEFI boot (it's too old). If you want to test a new device's RAM, you'll need a recent version.

Note that the open-source Memtest86+ should not be confused with the proprietary Memtest86.

1. Download the open-source Memtest86+ Linux 64-bit image:

   `wget https://memtest.org/download/v7.20/mt86plus_7.20_64.iso.zip`

   `unzip mt86plus_7.20_64.iso.zip`

	You should get a file named `memtest.iso`.  
	For newer versions, see [https://memtest.org/](https://memtest.org/)

2. Insert the USB drive. Locate its device file (typically `/dev/sdX` where X is a letter). Unmount any mounted partitions of it. The next steps will destroy any existing partitions and data. Identifying the wrong drive could be catastrophic.

   Note that if you use GNOME graphic UI, the right-click \-\> unmount operation may make the next step fail. Use the `umount` command instead:

   `df`

   `[output of df command showing the mounted partitions]`

   `sudo umount [device, e.g. /dev/sdX1]`

   Until all partitions are unmounted.

3. Overwrite the drive block device:

   `dd if=memtest.iso of=/dev/sdX`

	Now the drive is a bootable Memtest86+ utility.

On the R7, to boot from this USB image, press F7 while booting, to bring up the boot selection menu. Choose the USB stick.