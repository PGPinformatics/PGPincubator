# Single-host Arvados installation in VM guest

The purpose is to make a “single-host single-hostname” installation of Arvados on top of the [base image](Create-base-image-for-Arvados/Create-base-image-for-Arvados.md). This process will be initiated from the host.

Currently the official Arvados “single-host” installer creates an instance that can run, but is far from production-ready. For example,

* The default installation script creates a volume with a hard-coded underlying replication factor of 2, which doesn’t correspond to reality unless the underlying device happens to have some sort of duplex redundancy (and on the R7 we’re not going to do this).
* Shell node will not work. Even if it appears to work, it does not.

# Choose an Arvados Cluster ID

See: [https://doc.arvados.org/main/install/install-manual-prerequisites.html\#clusterid](https://doc.arvados.org/main/install/install-manual-prerequisites.html#clusterid)

A 5-character alphanumeric identifier is required. In this recipe we will use “`x0000`” for documentation purposes. The ID should be unique to a particular instance.

# Prepare Arvados source repo on host

\[As of Oct 24, 2024\]

Log-in (or su) as the `arvdev` user on the **host**. [Start a shell session with ssh-agent; load the SSH key](Create-base-image-for-Arvados/Create-base-image-for-Arvados.md).

We have already [cloned the Arvados source repository](Create-base-image-for-Arvados/Create-base-image-for-Arvados.md) (located at `$HOME/src/arvados` but the exact location is not material to our process). Notice that we will be checking out the live main branch (NOTE: Should find a way for binaries in repo and source git repo to match)
	`cd ~/src/arvados`
	`git checkout main`
	`git pull`
	`cd tools/salt-install`

Then [follow the official guide](https://doc.arvados.org/main/install/salt-single-host.html#:~:text=Without%20Terraform) to initialize the installer:
	`export CLUSTER=x0000`
	`./installer.sh initialize "$HOME/setup-arvados-$CLUSTER" single_host_single_hostname single_host/single_hostname`
`cd "$HOME/setup-arvados-$CLUSTER"`

# Create secrets

In total 6 secrets will be used. The installer script can be used for this:
	`./installer.sh generate-tokens > ~/x0000-secrets.txt`
The content of the output file `~/x0000-secrets.txt` (in the home directory) will look like the following –

`BLOB_SIGNING_KEY=E3p0iL3F86wd1PHGAOfreWimSy5l7X7a`
`MANAGEMENT_TOKEN=MGQIMJNdy74hkRjyYvNtWLKhhskTT1C0`
`SYSTEM_ROOT_TOKEN=4U0jxla2XmFaTK8vj8T1o62pXewsi866`
`ANONYMOUS_USER_TOKEN=RE8EYHxOG1OW2qcGnEgXtv77ZXLxkR9O`
`DATABASE_PASSWORD=awGwQXljMIDkYTrr0ZPbFSpvnsPS0kVP`

The initial user password should also be generated. You can use the token generator again, or roll your own:
`tr -dc A-Za-z0-9 < /dev/urandom | head -c 32`

For each distinct Arvados instance, the set of secrets should be generated anew.

# Prepare installation script and config files

In a [previous step](#bookmark=id.5yp1eeho6gfh), we created the directory `"$HOME/setup-arvados-$CLUSTER"` in the **host**. It is from there that we will initiate the installation. Assume we are still in the ssh-agent-enabled shell session with SSH keys loaded. We go to the directory by
`cd "$HOME/setup-arvados-$CLUSTER"`

## ~~Patch installer script \[NO LONGER NECESSARY\]~~

Then, download the following patch to the `installer.sh` script:
	`wget https://gist.githubusercontent.com/zoe-translates/800530a5955fd82f267359eda857f376/raw/22aaedbd599c9b9437a2e2e0ef90b024a536b037/fix-installer-sh-syntax.patch`

Then, patch the script:
	`patch -p1 < fix-installer-sh-syntax.patch`

(The two steps are equivalent to `curl https://gist.githubusercontent.com/zoe-translates/800530a5955fd82f267359eda857f376/raw/22aaedbd599c9b9437a2e2e0ef90b024a536b037/fix-installer-sh-syntax.patch | patch -p1`)

## Write config files

Download the `local.params` config file:
`curl https://gist.githubusercontent.com/zoe-translates/48557bb7a8daa01f65b8304c50a0ba49/raw/b9c402b2a7dc0b7ebf6aa4875c198690e34ef2ae/local.params > local.params`

This will overwrite the (non-secret) local parameter file.

Summary of key ideas in the above parameter file that lead to successful installation –

* The `NODES` associative array must be keyed by the actual domain name of the guest, in this case `demo.vir-test.home.arpa` (default key is `"localhost"` which will not work)
* `DATABASE_POSTGRESQL_VERSION` should be set
* `RELEASE` should be set to `"development"` (default value is `"production"`) to base the installation on the current development branch.

### Write secrets

Edit `local.params.secrets` file so that

* Each of the keys `INITIAL_USER_PASSWORD`, `BLOB_SIGNING_KEY`, `MANAGEMENT_TOKEN`, `SYSTEM_ROOT_TOKEN`, `ANONYMOUS_USER_TOKEN,` and `DATABASE_PASSWORD` is set to one of [the secret values created earlier](#bookmark=id.n3ytxb7ko2po). (We saved these secrets in `~/x0000-secrets.txt`.)
* The keys `LE_AWS_ACCESS_KEY_ID`, `LE_AWS_SECRET_ACCESS_KEY`, `LOKI_AWS_S3_ACCESS_KEY_ID`, `LOKI_AWS_S3_SECRET_ACCESS_KEY`, `DISPATCHER_SSH_PRIVKEY` are all set to the string value `"no"`.

## Start guest VM

Start the [base image](Create-base-image-for-Arvados/Create-base-image-for-Arvados.md) from the host. Either using Virtual Machine Manager GUI, or
`virsh start demo`

### Make sure you can control guest from host

1. You can do

   `ssh demo.vir-test.home.arpa`

	successfully, without being prompted for passphrase.

2. Inside the guest, you can use `sudo` without password.

# Install Arvados in guest

`./installer.sh deploy`
This will start the installation process. I.e. the host will install Arvados into the guest.

If this is the first time you ssh into the guest using the cluster domain-name configured in the parameter files, you will be asked to verify the key fingerprint. Once you get past that, the process is non-interactive.

## Check installation (WB2)

Note that we can check out the WB2 installation in the guest if you don't feel like accepting the "snakeoil" CA in the host.

In the **guest**, open Firefox. Go to Settings \-\> Privacy & Security \-\> View Certificates (or search for 'view certificates' in the search box on the Settings page).

Select "Authorities" tab \-\> Import… \-\> Other Locations \-\> Computer \-\> /usr/local/share/ca-certificates/arvados-snakeoil-ca.crt

Choose "Trust this CA to identify websites" \-\> OK

Navigate to https://demo.vir-test.home.arpa/ from the URL bar.

In the login page, enter arvdev as username and [the password we used](#bookmark=id.j2rpwwjttevf) for `INITIAL_USER_PASSWORD` in the `local.params.secrets` file.

# Post-installation (minor) fixes

## Remove certain aliases from /etc/hosts

The post-install `/etc/hosts` is basically a static split-horizon DNS setup.

Remove the items "shell" and "workbench" (and their FQDN equivalents) from the hosts file. Shell node should be a separate node. Workbench (1) is no longer in use.

## Fix architecture of 3rd-party APT sources

Edit `/etc/apt/sources.list.d/phusionpassenger-official-jammy.list` so it reads

`deb [signed-by=/usr/share/keyrings/phusionpassenger-archive-keyring.gpg arch=amd64] https://oss-binaries.phusionpassenger.com/apt/passenger jammy main`

The architecture specifier is added just to prevent some annoying warning messages from `apt`.

Similarly, edit `/etc/apt/sources.list.d/salt3006.sources` and append the following line:
`Architecture: amd64`
