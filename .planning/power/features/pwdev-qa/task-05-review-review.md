## SPEC

PASS

## QUALITY

PASS — 35 testes frescos passaram; `git diff --check 3846a91..8db1e6b` passou; HEAD permaneceu em `8db1e6b`.

## FINDINGS

ADDRESSED — o finding Important de prontidão mobile parcial foi corrigido. Os cenários agora exigem probes separados de tool, host, SDK/toolchain, ADB quando aplicável, driver, build, signing, device e service. Probes negativos produzem `BLOCKED`; ausentes ou `not_run` produzem `unverified`; os testes cobrem host, build, signing e ADB sem permitir `READY`.

## REVIEW

APPROVED
