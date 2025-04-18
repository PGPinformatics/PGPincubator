# Creating a desktop shortcut to a specific URL

Create a file called something like `arvados.desktop` in `~/.local/share/applications` with +x

```
[Desktop Entry]
Name=Arvados
Exec=firefox -new-window https://xpgp2.demo.vir-test.home.arpa
Terminal=false
Type=Application
Icon=/home/peter/work/arvados/doc/images/dax.png
```
