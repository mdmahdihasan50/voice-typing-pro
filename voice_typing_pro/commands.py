from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommandResult:
    text: str = ""
    action: str | None = None


_ACTIONS = {
    "নতুন লাইন": "newline",
    "লাইন পরিবর্তন": "newline",
    "new line": "newline",
    "নতুন প্যারাগ্রাফ": "paragraph",
    "new paragraph": "paragraph",
    "শেষ শব্দ মুছুন": "undo_word",
    "শেষ শব্দ মুছে দাও": "undo_word",
    "delete last word": "undo_word",
    "শেষ বাক্য মুছুন": "undo_sentence",
    "শেষ বাক্য মুছে দাও": "undo_sentence",
    "delete last sentence": "undo_sentence",
    "সব মুছুন": "clear",
    "সব মুছে দাও": "clear",
    "clear all": "clear",
    "বাংলা মোড": "language_bn",
    "বাংলা চালু": "language_bn",
    "bengali mode": "language_bn",
    "ইংরেজি মোড": "language_en",
    "ইংরেজি চালু": "language_en",
    "english mode": "language_en",
    "টাইপিং বন্ধ": "stop",
    "শোনা বন্ধ": "stop",
    "stop listening": "stop",
}

_INLINE_BN = {
    "প্রশ্নবোধক চিহ্ন": "?",
    "বিস্ময়বোধক চিহ্ন": "!",
    "সেমিকোলন": ";",
    "কোলন": ":",
    "ফুলস্টপ": "।",
    "দাঁড়ি": "।",
    "দাড়ি": "।",
    "কমা": ",",
}

_INLINE_EN = {
    "question mark": "?",
    "exclamation mark": "!",
    "full stop": ".",
    "semicolon": ";",
    "colon": ":",
    "comma": ",",
}

_BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def process_recognition(
    text: str,
    language: str,
    *,
    commands_enabled: bool = True,
    punctuation_enabled: bool = True,
    bengali_digits: bool = False,
) -> CommandResult:
    cleaned = " ".join(text.strip().split())
    if not cleaned:
        return CommandResult()

    normalized = cleaned.casefold()
    if commands_enabled and normalized in _ACTIONS:
        return CommandResult(action=_ACTIONS[normalized])

    if punctuation_enabled:
        replacements = _INLINE_BN if language.startswith("bn") else _INLINE_EN
        for phrase in sorted(replacements, key=len, reverse=True):
            cleaned = re.sub(
                rf"(?<!\S){re.escape(phrase)}(?!\S)",
                replacements[phrase],
                cleaned,
                flags=re.IGNORECASE,
            )

    cleaned = re.sub(r"\s+([,.;:!?।])", r"\1", cleaned)
    cleaned = re.sub(r"([,.;:!?।])(?=\S)", r"\1 ", cleaned)
    if bengali_digits and language.startswith("bn"):
        cleaned = cleaned.translate(_BN_DIGITS)
    return CommandResult(text=cleaned.strip())
