
from app.core.database import get_db


def test_get_db_closes_session(monkeypatch):
    import app.core.database as database

    created_sessions = []
    close_calls = []

    original_session_local = database.SessionLocal

    def tracking_session_factory():
        db = original_session_local()
        original_close = db.close

        def tracked_close():
            close_calls.append(True)
            original_close()

        db.close = tracked_close
        created_sessions.append(db)
        return db

    monkeypatch.setattr(
        database,
        "SessionLocal",
        tracking_session_factory,
    )

    generator = get_db()
    db = next(generator)

    assert db is not None
    assert db in created_sessions
    assert close_calls == []

    generator.close()

    assert close_calls == [True]
