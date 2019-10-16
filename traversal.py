import backend as be
import mysql


class Vertex:
	def __init__(self, be):
		self.class_id = None
		self.vx_id = None
		self.be = be
		self.vx_id = None

	def get_class_id(self, class_label):
		cursor = self.be.cnx.cursor(buffered=True)
		query_vx_class = (
			"INSERT INTO vertex_class (label) "
			"VALUES (\"{}\")".format(class_label))
		try:
			cursor.execute(query_vx_class)
			self.class_id = cursor.lastrowid
		except mysql.connector.Error as err:
			query_get_class_id = ("SELECT id FROM vertex_class WHERE label=\"{}\"".format(class_label))
			cursor.execute(query_get_class_id)
			for (id, ) in cursor:
				self.class_id = id

	def new(self, class_label, name):
		self.get_class_id(class_label)
		query_vx = (
			"INSERT INTO vertex (class, name) VALUES ({}, \"{}\")".format(self.class_id, name))
		cursor = self.be.cnx.cursor(buffered=True)
		cursor.execute(query_vx)
		self.vx_id = cursor.lastrowid


class Traversal:
	def __init__(self):
		self.be = be.backend()

	def addVertex(self, class_label, name):
		vx = Vertex(be)
		vx.new(class_label, name)


if __name__ == "__main__":
	# g = Traversal()
	# g.addVertex("human", "memory")
	vx = Vertex(be.backend())
	vx.get_class_id("logic")
	print(vx.class_id)