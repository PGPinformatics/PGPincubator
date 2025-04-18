Prevent GNOME's display manager (GDM3) from showing a certain user

This is more of a memo than a recipe. The purpose is to prevent the GDM screen showing a normal user as one of the options you can choose, without making that user a system user outright.

Assume the login id of the user is "`user_name`". As root user, locate the file `/var/lib/AccountsService/user_name` . If it doesn't exist, create it.

The file is in a typical .ini format. Make sure it has something like this in it:

`[User]`  
`SystemAccount=true`

(i.e. under the section `[User]` set the `SystemAccount` key to true. If there's no such section, create it.)