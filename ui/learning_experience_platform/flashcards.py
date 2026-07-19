"""Flashcards UI."""

from __future__ import annotations

import streamlit as st

from engines.learning_experience_platform.flashcards import rate_flashcard
from engines.learning_experience_platform.service import api_flashcards


def render_flashcards(*, learner_id: str, lesson: dict | None = None, context: dict | None = None) -> None:
    st.subheader("Flashcards")
    data = api_flashcards(learner_id=learner_id, lesson=lesson, context=context)
    cards = data.get("cards") or []
    if not cards:
        st.info("No verified flashcards for this lesson yet.")
        return
    idx = st.number_input("Card", min_value=0, max_value=max(0, len(cards) - 1), value=0)
    card = cards[int(idx)]
    show = st.toggle("Reveal", value=False, key=f"fc_flip_{card.get('card_id')}")
    st.markdown(f"**{card.get('front')}**")
    if show:
        st.write(card.get("back"))
    rating = st.selectbox("Difficulty", ["easy", "medium", "hard", "again"], key=f"fc_rate_{card.get('card_id')}")
    if st.button("Rate card"):
        rate_flashcard(str(card.get("card_id")), rating, learner_id=learner_id)
        st.toast("Rated — spaced repetition updated")
