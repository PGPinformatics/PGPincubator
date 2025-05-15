# Installing Arvados onto the PGPi h-gram image

This is a work in progress.  The following outlines the manual process
of installing Arvados using Ansible, with the plan being to implement
an additional layer of orchestration that fully automates the process.

## Assumptions

* You are doing a single host install (self-contained).
* The target machine (or "managed node" in Ansible parlance) is already on
  Tailnet.
* You already have a sudo-capable user account on the target machine. This
  document will use the user name `pgpadmin`.
* On the machine from which you initiate the installation ("control node"), you
  can install Ansible in a Python venv.
  * On Ubuntu, you can install the venv module with
  `sudo apt install python3-venv`.

## Step 0: Install Ansible and clone Arvados playbooks

On the "control node":

```
python3 -m venv venv
. venv/bin/activate
pip install ansible~=8.7
```

```
git clone https://github.com/arvados/arvados.git
git -C arvados checkout main
```

## Step 1: Collect information

You need to determine:

1. The five-character Arvados cluster ID that you will use (the template files
   use `xampl`);

2. The hostname of the virtual machine you are installing on to (the template
   files use `xampl.snowshoe-company.ts.net`).

## Step 2: Edit Arvados config

Copy `example-config.yml` from this repo, and then open the file for editing:

1. Search-and-replace `xampl.snowshoe-company.ts.net` with the correct hostname
   that you are using.

2. Search-and-replace `xampl` with the five-character Arvados cluster ID that
   you are using.

3. Generate essential tokens (`ManagementToken`, `SystemRootToken`,
   `BlobSigningKey`, `PostgreSQL.Connection.password`) and replace them in the
   configuration file.
   * An easy command to do this is:
     ```
     tr -dc A-Za-z0-9 </dev/urandom | head -c 32
     ```

## Step 3: Edit Ansible inventory

Copy `example-inv.yml` from this repo, and then open the file for editing:

1. Update the variable `arvados_config_file` to the correct path from Step 2.

2. Search-and-replace `xampl.snowshoe-company.ts.net` with the correct hostname
   that you are using.

3. Search-and-replace `xampl` with the five-character Arvados cluster id that
   you are using.

## Step 4: Install certificate

This gets the certificates from Tailscale and installs them on the target host.

```
ansible-playbook -u pgpadmin -Ki example-inv.yml get-tailscale-cert.yml
```

## Step 5: Run Arvados installer

This installs the Arvados packages and configures the cluster.

```
ansible-playbook -u pgpadmin -Ki example-inv.yml arvados/tools/ansible/install-arvados-cluster.yml
```

Here, the path `arvados/tools/ansible/install-arvados-cluster.yml` refers to
the Ansible playbook for Arvados cluster installation in the Arvados repository we cloned with Git in Step 0.

## Step 6: Run diagnostics

Confirm that you have a working installation.  Start by installing
`arvados-client` locally, if you do not already have it installed.

```
ansible-playbook -K install-arvados-client.yml

export ARVADOS_API_HOST=xampl.snowshoe-company.ts.net:7001
export ARVADOS_API_TOKEN=nWixxxxxxxxFIXMExxxxxxxxxxxBPR8D
arvados-client diagnostics
```

As of this writing, one error `ERROR 44: connecting to service
endpoint (0 ms): Get "": unsupported protocol scheme ""` is expected.
This is actually bug in the diagnostic tool -- it should skip over the
unconfigured non-essential service rather than reporting it as an
error.  It will be fixed in a future version.

# Copying a project on the h-gram image

How to copy a reference project to the h-gram Arvados instance.

## Assumptions

* You have read access to a project you are copying/exporting from.
* You have admin access to the Arvados instance you are copying/importing into.

## Option 1: Use arv-copy

This is currently the standard tool for the job, but may slower than
using the export/import tools described below.

Copy project source `xsrc1` to destination `xampl`:

```
arv-copy --src xsrc1 --dst xampl xsrc1-j7d0g-uvrkek9o6yhqy4e
```

This copies keep blocks, collection records and project records by
downloading them from the source cluster and uploading them to the
destination cluster.

## Option 2: Use arv-export and arv-import

These are new tools developed for this purpose.

### Step 1: Install the tools

These are still under development, you need to get them from a branch:

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

This will create two directories called `arvados/` and `keep/`.  The
`arvados/` directory will have the JSON records and the `keep/`
directory will have the keep blocks.

For example, the JSON record for the exported project will be found at
`arvados/v1/groups/xsrc1-j7d0g-myprojectuuid11`.

### Step 3: Cluster import from the local filesystem

There are two options, (1) uploading the blocks using the keep API or
(2) copying them directly on to the target file system.

#### Option 1: Block upload

From the `my-project-export` directory:

```
export ARVADOS_API_HOST=xampl.snowshoe-company.ts.net:7001
export ARVADOS_API_TOKEN=nWixxxxxxxxFIXMExxxxxxxxxxxBPR8D
arv-import xsrc1-j7d0g-myprojectuuid11
```

This will import the project `xsrc1-j7d0g-myprojectuuid11` from the
local filesystem that was previously exported.  This will create new
records on the destination cluster `xampl` for all the projects,
subprojects and collections, and upload all the keep blocks.

#### Option 2: Direct block copy

This is the same as before, except provide `--no-block-copy` and then
copy the contents of `keep` directly to the target file system that
will be used as a keepstore "Directory" volume.  From the
`my-project-export` directory:

```
export ARVADOS_API_HOST=xampl.snowshoe-company.ts.net:7001
export ARVADOS_API_TOKEN=nWixxxxxxxxFIXMExxxxxxxxxxxBPR8D
arv-import --no-block-copy xsrc1-j7d0g-myprojectuuid11
cp -r keep /mnt/xampl-data-filesystem/keep
```

This will import the project `xsrc1-j7d0g-myprojectuuid11` from the
local filesystem that was previously exported.  This will create new
records on the destination cluster `xampl` for all the projects,
subprojects and collections, but _not_ copy the keep blocks, which are
instead copied directly using `cp`.
