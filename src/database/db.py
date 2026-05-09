from contextlib import contextmanager
from typing import Generator

import psycopg
from psycopg import Connection
from pgvector.psycopg import register_vector

from src.config_loader import load_yaml_config


def get_database_config() -> dict:
    """
    config/database.yaml dosyasındaki database ayarlarını okur.
    """
    config = load_yaml_config("config/database.yaml")
    return config["database"]


def get_connection() -> Connection:
    """
    PostgreSQL bağlantısı oluşturur.

    Bu projede bağlantı bilgileri config/database.yaml dosyasından okunur.
    """
    db = get_database_config()

    connection = psycopg.connect(
        host=db["host"],
        port=db["port"],
        dbname=db["name"],
        user=db["user"],
        password=str(db["password"]),
    )

    # pgvector tipini psycopg tarafında tanıtıyoruz.
    # Böylece Python list / numpy array vektörleri PostgreSQL vector tipine yazılabilir.
    register_vector(connection)

    return connection


@contextmanager
def get_db_connection() -> Generator[Connection, None, None]:
    """
    Context manager ile güvenli veritabanı bağlantısı sağlar.

    Örnek:
        with get_db_connection() as conn:
            ...
    """
    connection = get_connection()

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def test_connection() -> None:
    """
    Veritabanı bağlantısını test eder.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user;")
            db_name, user_name = cur.fetchone()

    print(f"Bağlantı başarılı. Database: {db_name}, User: {user_name}")


if __name__ == "__main__":
    test_connection()