# Developer

some help for developers

## Plugins

i have add some comments to one of the simpler plugins to understand the plugin-system

[pwmout/plugin.py](../riocore/plugins/pwmout/plugin.py)


### create a new plugin

to create a new plugin, just copy an exsisting one with similar options or pins

```
cp -a riocore/plugins/pwmout/ riocore/plugins/myplugin/
```

rename the verilog file (preferably in the same name as the plugin)

```
mv riocore/plugins/myplugin/pwmout.v riocore/plugins/myplugin/myplugin.v
```

and edit plugin.py and the verilog file

thats all, rio will find it and the rio-setup can read all infos from the plugin.py

if you are done, run:
```
make readmes
```
to update the plugin lists and the README.md inside the plugin folder for github

