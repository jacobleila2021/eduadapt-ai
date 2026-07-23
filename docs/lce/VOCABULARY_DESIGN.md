# LCE Vocabulary Design Guide

## Premium flashcard anatomy

```
┌─────────────────────────────┐
│         EVAPORATION         │  ← large, bold, centered, Capitalized
│     noun · /e-vap-o-ra-tion/│
│ Definition …                │
│ In simple words …           │
│ Example …                   │
│ Picture …                   │
│ Synonyms · Antonyms         │
│ Related · Difficulty · Level│
└─────────────────────────────┘
```

## Rules

- Compose from Canonical Lesson Graph / SIF vocabulary — **never** frequency word lists
- Color-coded soft backgrounds (teal/sky/mint/sand/rose/…)
- Backward compatible with existing `word_wall` renderers via `lce_card: true`
- HTML helper: `vocabulary_card_html()` in `engines/lesson_composition_engine/vocabulary.py`

## Study page sections

1. Word Wall (premium cards)  
2. Flashcards  
3. Picture Words + SVG concept map  
4. Say It · Spell It · Use It  
5. Match & Review  
6. Quick Reference Chart  
