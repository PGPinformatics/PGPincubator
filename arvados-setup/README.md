# Installing Arvados onto the PGPi h-gram image

This is a work in progress.

## Step 1: Collect information

You need to decide:

1. The five-character Arvados cluster id that you will use (the template files use "xampl")

2. The hostname you are installing on to (the template files use "xampl.snowshoe-company.ts.net")

## Step 2: Edit arvados config

Copy and rename `example-config.yml` and then open the file for editing:

1. Generate essential tokens (ManagementToken, SystemRootToken, BlobSigningKey, PostgreSQL.Connection.password)
   an easy command to do this is: `tr -dc A-Za-z0-9 </dev/urandom | head -c 32`

2.

## Step 3: Edit the inventory

Copy and rename `example-inv.yml` and then open the file for editing:

1. Search-and-replace "xampl" with the five-character arvados cluster id that you are using.

2. Search-and-replace "snowshoe-company.ts.net" with the correct subdomain that you are using.

3. Update the variable `arvados_config_file` to the correct path from step (2).



## Step 3:
