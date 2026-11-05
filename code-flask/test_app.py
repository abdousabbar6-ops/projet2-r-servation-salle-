from app import app


def test_accueil():
    assert app.test_client().get("/").status_code == 200
