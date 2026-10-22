# Aggregation of the runs

## Descriptive statistics

| Scenario | Metric | Unit | Batch | n | Mean | SD | Min | Max |
|---|---|---|---|---|---|---|---|---|
| S1 | field_agreement | condition_occurrence | - | 5 | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| S1 | field_agreement | drug_exposure | - | 5 | 0.8010 | 0.0000 | 0.8010 | 0.8010 |
| S1 | field_agreement | measurement | - | 5 | 0.9920 | 0.0055 | 0.9880 | 0.9980 |
| S1 | field_agreement | observation | - | 5 | 0.9356 | 0.1038 | 0.7500 | 0.9820 |
| S1 | field_agreement | observation_period | - | 5 | 0.9980 | 0.0000 | 0.9980 | 0.9980 |
| S1 | field_agreement | person | - | 5 | 0.9960 | 0.0000 | 0.9960 | 0.9960 |
| S1 | field_agreement | procedure_occurrence | - | 5 | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| S1 | field_agreement | visit_occurrence | - | 5 | 0.7490 | 0.0000 | 0.7490 | 0.7490 |

## H1 - mean F1 > 0.8 (one-sided t-test, alpha = 0.05)

| Scenario | n | Mean | SD | t | p | d_z | Rejected H0 | Note |
|---|---|---|---|---|---|---|---|---|

## H2 - mean field agreement per table > 0.9 (one-sided t-test, alpha = 0.05)

| Scenario | Table | n | Mean | SD | t | p | d_z | Rejected H0 | Note |
|---|---|---|---|---|---|---|---|---|---|
| S1 | condition_occurrence | 5 | 1.0000 | 0.0000 | n/a | n/a | n/a | yes | sd = 0: mean compared directly to the threshold |
| S1 | drug_exposure | 5 | 0.8010 | 0.0000 | n/a | n/a | n/a | no | sd = 0: mean compared directly to the threshold |
| S1 | measurement | 5 | 0.9920 | 0.0055 | 37.559 | <0.0001 | 16.80 | yes |  |
| S1 | observation | 5 | 0.9356 | 0.1038 | 0.767 | 0.2429 | 0.34 | no |  |
| S1 | observation_period | 5 | 0.9980 | 0.0000 | n/a | n/a | n/a | yes | sd = 0: mean compared directly to the threshold |
| S1 | person | 5 | 0.9960 | 0.0000 | n/a | n/a | n/a | yes | sd = 0: mean compared directly to the threshold |
| S1 | procedure_occurrence | 5 | 1.0000 | 0.0000 | n/a | n/a | n/a | yes | sd = 0: mean compared directly to the threshold |
| S1 | visit_occurrence | 5 | 0.7490 | 0.0000 | n/a | n/a | n/a | no | sd = 0: mean compared directly to the threshold |

## H3 - S4 schema drift, TOST on (second - first batch), margin +-0.05 (alpha = 0.05)

| Metric | n | Mean difference | SD | p (TOST) | Equivalent | Note |
|---|---|---|---|---|---|---|
