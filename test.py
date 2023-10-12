from scripts import db_connection as db

connection  = db.db_connection()

connection.add_elements('apparats', id=1, name='app_test')