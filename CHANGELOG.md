# Changelog

## v0.9.1

### Gui and Generator
* better Windows support
* better extra gui preview
* some little fixes and improvements

### Modifier
* better debouncer (now, the delay is in milliseconds, which makes the whole thing easier to configure.)
* new modifier: oneshot (creates a variable-length output pulse when the input changes state)
* overwiew : [MODIFIERS.md](riocore/blob/dev/MODIFIERS.md)

### Plugins
* new plugin: bitcopy (copy a bit/pin to an other output pin)
* new plugin: pdmout (delta-sigma modulator / dac)
* new plugin: demux (binary demultiplexer)
* better stepdir plugin (with pulse_len and dir_delay configuration)

### Addons
* adding Spacemouse support

