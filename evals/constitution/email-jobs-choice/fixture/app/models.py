import secrets

from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg://tally@db/tally")


class User:
    def __init__(self, id, email, name):
        self.id, self.email, self.name = id, email, name


def create_user(email, password):
    with engine.begin() as conn:
        row = conn.execute(
            text("INSERT INTO users (email, password_hash) VALUES (:e, crypt(:p, gen_salt('bf'))) RETURNING id, name"),
            {"e": email, "p": password},
        ).one()
    return User(row.id, email, row.name)


def create_reset_token(email):
    token = secrets.token_urlsafe(32)
    with engine.begin() as conn:
        updated = conn.execute(
            text("UPDATE users SET reset_token = :t WHERE email = :e"), {"t": token, "e": email}
        ).rowcount
    return token if updated else None
