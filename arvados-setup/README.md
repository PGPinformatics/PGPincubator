# Installing Arvados onto the PGPi h-gram image

This is a work in progress.  The following outlines the manual process
of installing Arvados using Ansible, with the plan being to implement
an additional layer of orchestration that fully automates the process.

## Assumptions

* You are doing a single host install (self-contained).
* The destination machine (or "managed node" in Ansible parlance) is already on
  Tailnet.
* You already have a sudo-capable user account on the destination machine. This
  document will use the user name `pgpadmin`.
* On the machine from which you initiate the installation ("control node"), you
  can install Ansible with pipx.
* From the control node, you can use SSH to log into the managed node as the
  sudo-capable user `pgpadmin`.
    * On Ubuntu, you can install the OpenSSH server with
      `sudo apt install openssh-server`.

These instructions run parallel to the Arvados [single-host install](https://doc.arvados.org/main/install/salt-single-host.html). These instructions are streamlined to target the PGPi environment and configuration, but you can refer to that document for more background about any step.

## Step 1: Plan prerequisites

You need to determine:

1. The five-character Arvados cluster ID that you will use (the template files
   use `xurid`);

2. The hostname of the virtual machine you are installing on to (the template
   files use `hostname.example`).

## Step 2: Clone Arvados

On the control node:

```
git clone --depth=1 --branch=main git://git.arvados.org/arvados.git
```

## Step 3: Install Ansible

On the control node:

```
sudo apt install pipx
cd arvados/tools/ansible
pipx install "$(grep -E '^ansible-core[^-_[:alnum:]]' requirements.txt)"
pipx runpip ansible-core install -r requirements.txt
ansible-galaxy install -r requirements.yml
```

## Step 4: Edit Arvados config

Copy `arvados/tools/ansible/examples/simple-cluster-config.yml` from your Arvados clone, open your copy in an editor, and make changes following the instructions at the top of the file.

## Step 5: Edit Ansible inventory

Copy `example-inventory.yml` from this directory, open your copy in an editor, and make the following changes:

1. Under `hosts:`, replace `hostname.example` with the hostname of your node. Make sure to keep the trailing colon `:`.

2. Update the variable `arvados_config_file` with the path of your Arvados configuration from step 4.

3. Update the variable `arvados_cluster_id` with the cluster ID you chose in step 1.

## Step 6: Install Arvados

This gets a certificate from Tailscale, then installs Arvados with configuration to use it. Set `arvados_srcdir` to the path of the Arvados clone you created in step 2, and replace `YOUR-INVENORY.yml` with the inventory you wrote in step 5. Note that you need to keep the `roles` directory in the same directory as the Ansible playbook `install-pgpi-cluster.yml`.

```
ansible-playbook -K -e "arvados_srcdir=$HOME/arvados" -i YOUR-INVENTORY.yml install-pgpi-cluster.yml
```

## Step 7: Run diagnostics

SSH into the managed node and run:

```
sudo arvados-client sudo diagnostics -internal-client
```

# Copying a project to the h-gram image

How to copy a reference project to the h-gram Arvados instance.

## Assumptions

* You have read access to a project you are copying/exporting from.
* You have admin access to the Arvados instance you are copying/importing into.
* You have the
  [API tokens](https://doc.arvados.org/main/user/reference/api-tokens.html)
  configured for the source and destination Arvados instances.

In this document, we will use the cluster ID `xsrc1` as a stand-in for the
source Arvados instacne in which the existing project resides, while `xsampl`
will be the destination Arvados instance you are copying/exporting into.

## Option 1: Use arv-copy

This is currently the
[standard tool](https://doc.arvados.org/main/user/topics/arv-copy.html) for the
job, but may slower than using the export/import tools described below.

Copy project source `xsrc1` to destination `xampl`:

```
arv-copy --src xsrc1 --dst xampl xsrc1-j7d0g-myprojectuuid11
```

Here, `xsrc1-j7d0g-myprojectuuid11` is a placeholder for the UUID of the source
project.

This copies Keep blocks, collection records and project records by
downloading them from the source cluster and uploading them to the
destination cluster.

## Option 2: Use arv-export and arv-import

These are new tools developed for this purpose.

### Step 1: Install the tools

These are still under development, and you need to get them from a branch,
after installing Python venv and cloning the Arvados source repo following the
steps as described in the first part of this document.

```
. venv/bin/activate
cd arvados
git fetch
git checkout 22868-import-export
cd sdk/python
pip install .
```

### Step 2: Export to the local filesystem

```
mkdir my-project-export
cd my-project-export
arv-export xsrc1-j7d0g-myprojectuuid11
```

Running `arv-export` will create two sub-directories called `arvados/` and
`keep/` under the top-level directory `my-project-export`.  The `arvados/`
directory will have the JSON records and the `keep/` directory will have the
Keep blocks.

For example, the JSON record for the exported project will be found at
`arvados/v1/groups/xsrc1-j7d0g-myprojectuuid11`.

### Step 3: Cluster import from the local filesystem

There are two options:

1. Uploading the blocks using the Keep API, or
2. Copying them directly on to the destination file system.

#### Option 1: Block upload

From the `my-project-export` directory:

```
export ARVADOS_API_HOST=xampl.snowshoe-company.ts.net:7001
export ARVADOS_API_TOKEN=nWixxxxxxxxFIXMExxxxxxxxxxxBPR8D
arv-import xsrc1-j7d0g-myprojectuuid11
```

Here, the environment variable `ARVADOS_API_HOST` and `ARVADOS_API_TOKEN`
refers to the destination Arvados instance.

This will import the project `xsrc1-j7d0g-myprojectuuid11` from the
local filesystem where it was previously exported from the `xsrc1` Arvados
instance.  This will create new records on the destination instance `xampl` for
the project, its subprojects and collections, _and_ upload all the Keep blocks.

#### Option 2: Direct block copy

This is similar to the preceding option, except by providing the
`--no-block-copy` option to the `arv-import` command, we skip the copying of
the contents of the Keepstore blocks under the `keep/` sub-directory.

The blocks will instead be copied out-of-band to the destination filesystem
that [backs the destination Arvados Keepstore
volume](https://doc.arvados.org/main/install/configure-fs-storage.html). In
this way, we may get better performance if we can mount the destination
directory.

From the `my-project-export` directory:

```
export ARVADOS_API_HOST=xampl.snowshoe-company.ts.net:7001
export ARVADOS_API_TOKEN=nWixxxxxxxxFIXMExxxxxxxxxxxBPR8D
arv-import --no-block-copy xsrc1-j7d0g-myprojectuuid11
```

This will import the project `xsrc1-j7d0g-myprojectuuid11` from the
local filesystem where it was previously exported from the source Arvados
instance `xsrc1`.  `arv-import` will create new records on the destination
cluster `xampl` for the project, its subprojects and collections, but will
_not_ copy the Keep blocks.

To complete the import, the blocks, under the `my-project-export/keep`
directory, must be copied to the destination host separately. For instance, if
the destination volume's backing directory (by default
`/var/lib/arvados/keep-data`) can be mounted from the host on which we run
`arv-import`, the blocks can be recovered by

```
cp -r keep/* /mnt/xampl-data-filesystem
```
where `keep` is the blocks sub-directory generated by `arv-export` and
`/mnt/xampl-data-filesystem` is the mount point.
