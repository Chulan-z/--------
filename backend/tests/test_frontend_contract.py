from pathlib import Path


def test_frontend_has_required_pages_and_dark_theme():
    root = Path(__file__).resolve().parents[2]
    pages = root / "frontend" / "src" / "app" / "pages"
    assert (pages / "feed-page.component.ts").exists()
    assert (pages / "login-page.component.ts").exists()
    assert (pages / "register-page.component.ts").exists()
    assert (pages / "profile-page.component.ts").exists()
    assert (pages / "admin-page.component.ts").exists()
    assert "color-scheme: dark" in (root / "frontend" / "src" / "styles.css").read_text(encoding="utf-8")
