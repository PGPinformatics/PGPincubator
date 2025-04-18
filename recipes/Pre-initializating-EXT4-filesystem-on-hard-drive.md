# Pre-initializating EXT4 filesystem on hard drive

# Problem

The recent version of `mke2fs` shipped with Ubuntu creates a lazily-initialized filesystem. This speeds up the initialization but causes the kernel to spend more time doing actual initialization in the background after the filesystem has been mounted. This not only causes additional I/O stress, it also makes an unpleasant sound that may be easily taken for evidence of a bad disk. The background initialization will be low-priority so the noisy process can drag on. It also carries a small risk of journal corruption (cf. the `mke2fs` man page).

Moreover, if the drive is shipped to the user with filesystems but without initialization, we're shifting an unnecessary burden to the user (along with the noise; think of people with misophony or other sound-triggered health issues, or anxious users worrying if the disk is going bad).

This default setting of lazy initialization seems to be better suited for SSD (faster, infinitely quieter), but for HDD its advantage is questionable.

# Solution

Use the following command line options to `mkfs.ext4` (which is an alias to `mke2fs`):

`# mkfs.ext4 -c -E lazy_itable_init=0,lazy_journal_init=0 [device]`

# Explanation

* `-c`: Scan the device and update badblocks information.  
* `-E`: Extended options (comma-separated); disable lazy initialization of inode table and journal.

# Example

`# echo y | time mkfs.ext4 -c -E lazy_itable_init=0,lazy_journal_init=0 [device]`

(this is a hack to tell `mke2fs` to go ahead if there's an existing filesystem)

For the MDD 18TB hard drive, it takes about 7m30s (elapsed time) to finish the initialization.