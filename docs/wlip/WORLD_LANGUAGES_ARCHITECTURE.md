# World Languages Architecture

**Pack:** World Languages Intelligence Pack (WLIP)  
**Version:** 1.0.0  
**Smoke:** `WORLD_LANGUAGES_INTELLIGENCE_SMOKE_OK`

## Role

WLIP is Alora AI’s multilingual Subject Intelligence Pack. Built on **SIF + SICS**. Enriches verified ULI with pronunciation, grammar, vocabulary, skills, culture, and translation metadata—never invents curriculum.

## Subject registration

Registers production pack for: `languages`

English subject key remains owned by **ELIP** (`integration_only` in the WLIP catalogue).

## Language plugins

Initial catalogues: English (integration), French, German, Spanish, Italian, Portuguese, Arabic, Hindi, Malayalam, Tamil, Kannada, Telugu, Japanese, Korean, Chinese, Latin, Greek.

Add languages via `register_language_plugin()` without engine changes.

## Guarantees

- No invented definitions, audio, translations, or assessment answers  
- Reuses VMLE / AIE / ATIE / AME / LAIE / ALCIS / LXP  
- Additive ULIQE `ULIQE.WLIP.*` only — certification unchanged  
