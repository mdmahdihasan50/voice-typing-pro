import json

from voice_typing_pro.settings import AppSettings, SettingsStore


def test_defaults_are_bengali(tmp_path) -> None:
    store = SettingsStore(tmp_path / "settings.json")
    settings = store.load()
    assert settings.ui_language == "bn"
    assert settings.dictation_language == "bn-BD"


def test_settings_round_trip_and_ignore_unknown_keys(tmp_path) -> None:
    path = tmp_path / "settings.json"
    store = SettingsStore(path)
    settings = AppSettings(theme="dark", font_size=21, typing_mode="global")
    store.save(settings)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["future_setting"] = True
    path.write_text(json.dumps(payload), encoding="utf-8")
    loaded = store.load()
    assert loaded.theme == "dark"
    assert loaded.font_size == 21
    assert loaded.typing_mode == "global"


def test_invalid_settings_fall_back_to_defaults(tmp_path) -> None:
    path = tmp_path / "settings.json"
    path.write_text("not-json", encoding="utf-8")
    assert SettingsStore(path).load() == AppSettings()
