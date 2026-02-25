"""tests/test_theme_toggle.py — Unit tests for theme toggle callback."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_toggle_dark_to_light():
    """Clicking toggle while in dark mode should return light."""
    from app import toggle_theme
    result = toggle_theme(1, "dark")
    assert result == "light"


def test_toggle_light_to_dark():
    """Clicking toggle while in light mode should return dark."""
    from app import toggle_theme
    result = toggle_theme(1, "light")
    assert result == "dark"


def test_toggle_no_click():
    """n_clicks=0 on initial load should return dark (unchanged)."""
    from app import toggle_theme
    result = toggle_theme(0, "dark")
    assert result == "dark"


def test_chart_template_dark():
    """build_charts should use 'bloomberg' template in dark mode."""
    from app import get_chart_template
    assert get_chart_template("dark") == "bloomberg"


def test_chart_template_light():
    """build_charts should use 'muji' template in light mode."""
    from app import get_chart_template
    assert get_chart_template("light") == "muji"
