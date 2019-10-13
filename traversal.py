import backend as be
import mysql


class Traversal:
	def __init__(self):
		self.be = be.backend()
	# self.be.test1_query()

	def addVertex(self, name, class_label):
		cursor = self.be.cnx.cursor(buffered=True)
		# query_vx_class = (
		# 	"INSERT INTO vertex_class (label) "
		# 	"VALUES (\"{}\")".format(class_label))
		query_vx_class = (
			"INSERT INTO vertex_class (label) "
			"VALUES (\"{}\")".format(class_label))
		print("\t{}".format(query_vx_class))
		try:
			cursor.execute(query_vx_class)
		except mysql.connector.Error as err:
			pass

		query_get_class_id = ("SELECT id FROM vertex_class WHERE label=\"{}\"".format(class_label))
		print(query_get_class_id)
		cursor.execute(query_get_class_id)
		class_id = -1
		for (id, ) in cursor:
			print("~~~> {}".format(id))
			class_id = id
		query_vx = (
			"INSERT INTO vertex (class, name) VALUES ({}, \"{}\")".format(class_id, name))
		print(query_vx)
		cursor = self.be.cnx.cursor(buffered=True)
		cursor.execute(query_vx)
		new_id = cursor.lastrowid
		print("returned id: {}".format(new_id))


if __name__ == "__main__":
	g = Traversal()
	g.addVertex("human", "memory")