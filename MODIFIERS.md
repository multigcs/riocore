# MODIFIERS
## onerror
holds the pin on error

### Options
| Name | Type | Default | Info |
| --- | --- | --- |
| Invert | bool | False |  |

## debounce
debounce filter

### Options
| Name | Type | Default | Info |
| --- | --- | --- |
| Delay | int | 16 |  |

## pwm
pwm generator

### Options
| Name | Type | Default | Info |
| --- | --- | --- |
| Frequency | int | 16 |  |
| DTY | int | 50 |  |

## oneshot
onshot filter

### Options
| Name | Type | Default | Info |
| --- | --- | --- |
| PulseLen | float | 1.0 | pulse len in ms |
| Retrigger | bool | False | retrigger the time pulse |
| Hold | bool | False | hold the puls while input is set |
| Edge | select | RISING | edge to trigger |

## toggle
toggle pin on rising edge

## invert
inverting the pin

