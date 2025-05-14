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
