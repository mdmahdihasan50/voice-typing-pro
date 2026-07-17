from voice_typing_pro.commands import process_recognition


def test_bengali_is_default_quality_path() -> None:
    result = process_recognition("হ্যালো কমা বিশ্ব", "bn-BD")
    assert result.text == "হ্যালো, বিশ্ব"
    assert result.action is None


def test_english_punctuation() -> None:
    result = process_recognition("hello comma world question mark", "en-US")
    assert result.text == "hello, world?"


def test_bengali_voice_command() -> None:
    result = process_recognition("নতুন প্যারাগ্রাফ", "bn-BD")
    assert result.action == "paragraph"
    assert result.text == ""


def test_commands_can_be_disabled() -> None:
    result = process_recognition(
        "নতুন লাইন", "bn-BD", commands_enabled=False, punctuation_enabled=False
    )
    assert result.text == "নতুন লাইন"


def test_optional_bengali_digits() -> None:
    result = process_recognition("আমার 2 টি বই", "bn-BD", bengali_digits=True)
    assert result.text == "আমার ২ টি বই"
