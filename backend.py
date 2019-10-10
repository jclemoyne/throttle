import mysql.connector
from mysql.connector import connection
from mysql.connector import errorcode


class backend:
	config = {
		'user': 'cubicon',
		'password': 'reseau1ntel',
		'host': '10.0.0.197',
		'database': 'reseau',
		'raise_on_warnings': True
	}

	def __init__(self):
		try:
			print("... trying to connect with database")
			self.cnx = connection.MySQLConnection(**backend.config)
			# self.cnx = connection.MySQLConnection(user='cubicon', password='reseau1ntel',
			# 								   host='10.0.0.197',
			# 								   database='reseau')
			print("== successfully connected to database: {}".format(backend.config["database"]))
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				print("Something is wrong with your user name or password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				print("Database does not exist")
			else:
				print("***** {}".format(err))
		# else:
		# 	self.cnx.close()

	def empty_table(self, tablename):
		cursor = self.cnx.cursor()
		cursor.execute("TRUNCATE TABLE {}".format(tablename))

	def exec_sql_query(self, query):
		cursor = self.cnx.cursor()
		cursor.execute(query)
		return cursor

	def test1_query(self):
		tables = ("show tables")
		c = self.exec_sql_query(tables)
		for (tables) in c:
			print(tables[0])
		print("~~~~~~~~~~~~~")
		cursor = self.cnx.cursor()
		databases = ("show databases")
		cursor.execute(databases)
		for (databases) in cursor:
			print(databases[0])


if __name__ == "__main__":
	graph = backend()
	# graph.empty_table("vertex_class")
	graph.test1_query()