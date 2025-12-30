# MODIFIERS
you can modify each input and output pin of the FPGA with an modifier pipeline

```mermaid
graph LR;
    Input-Signal-->Modifier1;
    Modifier1-->Modifier2;
    Modifier2-->Modifier...;
    Modifier...-->Output-Signal;
```

## OnError
holds the pin at 0 when an error has occurred

**Options:**
| Name | Type | Default | Info |
| --- | --- | --- | --- |
| Invert | bool | False | Inverts the Logic |

## Debounce
<img align="right" width="300" src="images/mod_debounce.png">
to filter noisy signals

**Options:**
| Name | Type | Default | Info |
| --- | --- | --- | --- |
| Delay | float | 2.5 | Delay in ms |

## Delay
<img align="right" width="300" src="images/mod_delay.png">
to delay signal edges

**Options:**
| Name | Type | Default | Info |
| --- | --- | --- | --- |
| Delay | float | 2.5 | Delay in ms |
| Rising-Edge | bool | True | do delay on rising edge |
| Falling-Edge | bool | False | do delay on falling edge |

## PWM
<img align="right" width="300" src="images/mod_pwm.png">
pwm generator

**Options:**
| Name | Type | Default | Info |
| --- | --- | --- | --- |
| Frequency | int | 1 | PWM Frequency |
| DTY | int | 50 | PWM Duty Cycle |

## Oneshot
<img align="right" width="300" src="images/mod_oneshot.png">
creates a variable-length output pulse when the input changes state

**Options:**
| Name | Type | Default | Info |
| --- | --- | --- | --- |
| PulseLen | float | 1.0 | pulse len in ms |
| Retrigger | bool | False | retrigger the time pulse |
| Hold | bool | False | hold the puls while input is set |
| Edge | select | RISING | edge to trigger |

## Toggle
<img align="right" width="300" src="images/mod_toggle.png">
toggle pin on rising edge

## Invert
inverting the pin

