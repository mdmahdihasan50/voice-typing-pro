from voice_typing_pro.i18n import Translator


def test_both_catalogs_have_the_same_keys() -> None:
    translator = Translator()
    assert set(translator._catalogs["bn"]) == set(translator._catalogs["en"])


def test_translation_and_formatting() -> None:
    translator = Translator("bn")
    assert translator.t("app_name") == "বাংলা ভয়েস টাইপিং প্রো"
    assert "3" in translator.t("words_chars", words=3, chars=10)
    translator.set_language("en")
    assert translator.t("settings") == "Settings"
