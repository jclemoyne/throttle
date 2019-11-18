import backend as be
import mysql
from mysql.connector.errors import Error


class Vertex:
	def __init__(self, class_id, label, vx_id, name):
		self.class_id = class_id
		self.label = label
		self.vx_id = vx_id
		self.name = name

	def to_string(self):
		return "class id: {};\t label: {};\tvertex id: {};\tname: {};".\
			format(self.class_id, self.label, self.vx_id, self.name)


class VertexService:
	def __init__(self, be):
		self.be = be
		self.current_vx = None

	def get_class_id(self, class_label):
		class_id = None
		cursor = self.be.cnx.cursor(buffered=True)
		try:
			query_get_class_id = ("SELECT id FROM vertex_class WHERE label=\"{}\"".format(class_label))
			cursor.execute(query_get_class_id)
			for (id, ) in cursor:
				class_id = id
		except mysql.connector.Error as err:
			pass
		return class_id

	def get_class_label(self, class_id):
		class_label = None
		cursor = self.be.cnx.cursor(buffered=True)
		try:
			query_get_class_id = ("SELECT label FROM vertex_class WHERE id=\"{}\"".format(class_id))
			cursor.execute(query_get_class_id)
			for (label, ) in cursor:
				class_label = label
		except mysql.connector.Error as err:
			pass
		return class_label

	def add_class_id(self, class_label):
		class_id = None
		cursor = self.be.cnx.cursor(buffered=True)
		query_vx_class = (
			"INSERT INTO vertex_class (label) "
			"VALUES (\"{}\")".format(class_label))
		try:
			cursor.execute(query_vx_class)
			class_id = cursor.lastrowid
		except mysql.connector.Error as err:
			query_get_class_id = ("SELECT id FROM vertex_class WHERE label=\"{}\"".format(class_label))
			cursor.execute(query_get_class_id)
			for (id, ) in cursor:
				class_id = id
		return class_id

	def newV(self, class_label, name):
		class_id = self.add_class_id(class_label)
		vx = None
		query_vx = (
			"INSERT INTO vertex (class, name) VALUES ({}, \"{}\")".format(class_id, name))
		cursor = self.be.cnx.cursor(buffered=True)
		try:
			cursor.execute(query_vx)
			vx_id = cursor.lastrowid
			vx = Vertex(class_id, class_label, vx_id, name)
		except mysql.connector.Error as err:
			query_vx = (
				"SELECT id, class as cid, name  FROM vertex WHERE name=\"{}\"".format(name))
			cursor = self.be.cnx.cursor(buffered=True)
			cursor.execute(query_vx)
			for (id, cid, name, ) in cursor:
				class_label = self.get_class_label(cid)
				vx = Vertex(cid, class_label, id, name)
		return vx

	def getVertex(self, name):
		cursor = self.be.cnx.cursor(buffered=True)
		query_vx = ("SELECT id, class as cid FROM vertex WHERE name=\"{}\"".format(name))
		cursor.execute(query_vx)
		vx = None
		for (id, cid, ) in cursor:
			class_label = self.get_class_label(cid)
			vx = Vertex(cid, class_label, id, name)
		return vx


class Traversal:
	def __init__(self):
		self.be = be.backend()
		self.service = VertexService(self.be)

	def addV(self, class_label, name):
		return self.service.newV(class_label, name)

	def V(self, name):
		return self.service.getVertex(name)


def test_run(g):
	vx = g.addV("depot", "Novato")
	print(vx.to_string())
	vx = g.addV("logic", "Aristotle")
	print(vx.to_string())
	vx = g.addV("author", "Thomas Mann")
	print(vx.to_string())
	vx = g.addV("human", "Socrates")
	print(vx.to_string())


def test_check(g):
	vx_service = VertexService(g.be)
	class_id = vx_service.get_class_id("logic")
	print(class_id)
	class_id = vx_service.get_class_id("human")
	print(class_id)
	vx = g.V("Novato")
	if vx is not None:
		print(vx.to_string())
	vx = g.V("Aristotle")
	if vx is not None:
		print(vx.to_string())


if __name__ == "__main__":
	g = Traversal()
	test_run(g)
	# test_check(g)


