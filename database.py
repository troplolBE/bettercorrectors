import sqlite3


def insert_evaluation(connection, evaluation):
    """Insert evaluation into the database

    :param connection: connection to the database
    :param tuple evaluation: bad evaluation that needs to be saved in tuple form
    """
    insert_eval = """INSERT INTO evaluations(scale_id,corrector_id,corrector_login,
                                            corrected_id,corrected_login,project_name,
                                            project_id,rule,begin_at) VALUES(?,?,?,?,?,?,?,?,?)"""
    try:
        cursor = connection.cursor()
        cursor.execute(insert_eval, evaluation)
        connection.commit()
    except sqlite3.Error as e:
        print(e)


def create_connection(database):
    """Create a database connection to the SQLite database specified by database.
    If the connection fails, None is returned.

    :param str database: name of the to create database
    :return: connectionto the database
    """
    connection = None
    create_table = """ CREATE TABLE IF NOT EXISTS evaluations (
                        id INTEGER PRIMARY KEY,
                        scale_id INTEGER NOT NULL,
                        corrector_id INTEGER NOT NULL,
                        corrector_login TEXT NOT NULL,
                        corrected_id INTEGER NOT NULL,
                        corrected_login TEXT NOT NULL,
                        project_name TEXT NOT NULL,
                        project_id INTEGER NOT NULL,
                        rule INTEGER NOT NULL,
                        begin_at TEXT NOT NULL
                    ); """
    try:
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        cursor.execute(create_table)
        connection.commit()
    except sqlite3.Error as e:
        print(e)
    return connection
