| # | Guardrail | Miss-rate ↓ | Over-refusal (all) ↓ | **Over-refusal: security-adjacent** ↓ | F1 ↑ | TR miss | TR over-refusal |
|---|-----------|:-----------:|:--------------------:|:-------------------------------------:|:----:|:-------:|:---------------:|
| 1 | **protectai-deberta-v2** | 0.02 | 0.18 | **0.40** | 0.94 | 0.02 | 0.25 |
| 2 | **AltaySec-detector** * | 0.00 | 0.23 | **0.70** | 0.94 | 0.00 | 0.23 |
| 3 | **jackhhao-jailbreak** | 0.46 | 0.12 | **0.25** | 0.67 | 0.83 | 0.00 |
| 4 | **keyword** | 0.88 | 0.12 | **0.38** | 0.20 | 0.91 | 0.08 |
| 5 | **regex-rules** | 0.91 | 0.10 | **0.30** | 0.16 | 0.90 | 0.10 |

*\* AltaySec-detector has train-set overlap on injections + plain benign; its security-adjacent column is its only fully held-out result. All other guards are fully held-out.*
