# SIF Plug-in Development Guide

1. Create `engines/subject_packs/<subject>_intelligence/` (suggested layout).
2. Subclass `SubjectIntelligencePack` from `engines.subject_intelligence_framework.interfaces`.
3. Implement at least `capabilities()` and `analyse_lesson()`.
4. Optionally override visual / assessment / accessibility / tutor / LXP helpers.
5. Register at import time:

```python
from engines.subject_intelligence_framework import get_registry
get_registry().register(MyMathPack(), overwrite=True)
```

6. Add unit tests that call `validate_pack_interface(pack)`.
7. Never call LLMs for factual content; reuse Computation Layer / ULI / CIE / AME.

Until a real pack exists, the registry serves `PlaceholderSubjectPack` for every listed subject.

**Production packs:** STEM (`mathematics`, `physics`, `chemistry`, `biology`),
`english` (ELIP), the social-science family (`social_science`, `history`,
`geography`, `civics`, `environmental_science` via SSIP),
`computer_science` (CSIP), the commerce family (`commerce`, `economics`,
`business_studies` via CEIP), and `languages` (WLIP) replace placeholders
on import / registry ensure.
Shared builders: SICS (`docs/sics/`).
See also `docs/elip/`, `docs/ssip/`, `docs/csip/`, `docs/ceip/`, `docs/wlip/`,
and Platform Excellence `docs/uvie/` (Universal Visual Intelligence Engine).
