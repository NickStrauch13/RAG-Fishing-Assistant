from src.aws_utils import connect_to_database, query_db


def test_connect_to_database():
    conn, cursor = connect_to_database()
    assert conn is not None
    assert cursor is not None
    cursor.close()
    conn.close()


def test_query_db():
    conn, cursor = connect_to_database()
    query = "SELECT * FROM raw_paragraphs LIMIT 10"
    records = query_db(cursor, query)
    assert records is not None
    assert type(records) == tuple
    assert len(records) == 10
    cursor.close()
    conn.close()