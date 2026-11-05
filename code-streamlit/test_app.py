from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_accueil():
    page = AppTest.from_file(str(Path(__file__).parent / "app.py"), default_timeout=60).run()
    assert not page.exception
