from random import shuffle
import sqlite3


def get_data(difficulty=1):
    try:
        db = sqlite3.connect("data/tests.db")
        cur = db.cursor()
        ids = [i[0] for i in cur.execute("""
        SELECT id FROM Tests
        """).fetchall()]
        shuffle(ids)
        return ids
    except FileNotFoundError:
        return difficulty


def get_row(i):
    try:
        db = sqlite3.connect("data/tests.db")
        cur = db.cursor()
        return cur.execute(f"""
        select text from tests where id={i}
        """).fetchone()
    except FileNotFoundError:
        return i


if __name__ == "__main__": # Debug
    print(get_data())
    print(*get_row(get_data()[0]))
