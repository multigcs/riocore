# Changelog

## v0.9.1

### Gui and Generator
* better Windows support
* better extra gui preview
* some little fixes and improvements

### Pin-Modifier
* better debouncer (now, the delay is in milliseconds, which makes the whole thing easier to configure.)
* new modifier: oneshot (creates a variable-length output pulse when the input changes state)
* overwiew : [MODIFIERS.md](riocore/blob/dev/MODIFIERS.md)

### Plugins
* new plugin: [bitcopy](riocore/plugins/bitcopy/README.md) (copy a bit/pin to an other output pin)
* new plugin: [pdmout](riocore/plugins/pdmout/README.md) (delta-sigma modulator / dac)
* new plugin: [binout](riocore/plugins/binout/README.md) (decimal to binary output)
* new plugin: [binin](riocore/plugins/binin/README.md) (binary to decimal input)
* new plugin: [demux](riocore/plugins/demux/README.md) (binary demultiplexer)
* better [stepdir](riocore/plugins/stepdir/README.md) plugin (with pulse_len and dir_delay configuration)

### Addons
* adding Spacemouse support

