# CEIP Extension Guide

1. Reuse SICS builders (`taxonomy`, `misconceptions`, `pedagogy`, `diagrams`, `assessment`, `accessibility`, `tutor_metadata`, `analytics`).
2. Add domain foci in a new module under `engines/commerce_economics_intelligence/` and wire into `pack.analyse_lesson`.
3. Register related subject keys via `iter_family_packs` / `register_commerce_economics_pack`.
4. Extend ULIQE only with additive INFO seeds (`ULIQE.CEIP.*`); never change certification thresholds.
5. Keep LXP as the renderer for statements, graphs, canvases, and dashboards.
6. CEIP is the reference architecture for future professional / vocational packs; WLIP (`docs/wlip/`) covers multilingual language learning.
