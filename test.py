from scripts import dbconnection as db

connection  = db.DbConnection()

connection.add_elements('apparats', id=1, name='app_test')