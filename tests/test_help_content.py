from voice_typing_pro import APP_DISPLAY_NAME, PORTFOLIO_URL
from voice_typing_pro.help_content import developer_html, guide_html


def test_bengali_help_contains_shortcuts_and_rules() -> None:
    content = guide_html("bn")
    assert APP_DISPLAY_NAME in content
    assert "Ctrl+Shift+Space" in content
    assert "Alt+Shift+B" in content
    assert "নতুন প্যারাগ্রাফ" in content
    assert "Administrator" in content


def test_developer_profile_contains_verified_public_information() -> None:
    content = developer_html("bn")
    assert PORTFOLIO_URL in content
    assert "হাফেজ মাহদী হাসান" in content
    assert "৫+ বছর" in content
    assert "২৩+" in content
    assert "mdmahdihasan50" in content
