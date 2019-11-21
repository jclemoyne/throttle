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
        return "class id: {};\t label: {};\tvertex id: {};\tname: {};". \
            format(self.class_id, self.label, self.vx_id, self.name)


class Edge:
    def __init__(self, edge_class_id, edge_class_label, edge_id, relation, vx_tail, vx_head):
        self.edge_class_id = edge_class_id
        self.edge_class_label = edge_class_label
        self.edge_id = edge_id
        self.relation = relation
        self.tail = vx_tail
        self.head = vx_head

    def to_string(self):
        return "class id: {};\t label: {};\tvertex id: {};\tname: {};\t({}, {})". \
            format(self.edge_class_id, self.edge_class_label, self.edge_id, self.relation, self.tail.vx_id,
                   self.head.vx_id)


class GraphService:
    def __init__(self, be):
        self.be = be
        self.current_vx = None

    def get_class_id(self, class_label):
        class_id = None
        cursor = self.be.cnx.cursor(buffered=True)
        try:
            query_get_class_id = ("SELECT id FROM vertex_class WHERE label=\"{}\"".format(class_label))
            cursor.execute(query_get_class_id)
            for (id,) in cursor:
                class_id = id
        except mysql.connector.Error as err:
            pass
        return class_id

    def get_class_label(self, class_id, table):
        class_label = None
        cursor = self.be.cnx.cursor(buffered=True)
        try:
            query_get_class_id = ("SELECT label FROM {} WHERE id=\"{}\"".format(table, class_id))
            cursor.execute(query_get_class_id)
            for (label,) in cursor:
                class_label = label
        except mysql.connector.Error as err:
            print(" ********* >> ", err, query_get_class_id)
            pass
        return class_label

    def add_class_id(self, class_label, table):
        class_id = None
        cursor = self.be.cnx.cursor(buffered=True)
        query_class = (
            "INSERT INTO {} (label) "
            "VALUES (\"{}\")".format(table, class_label))
        try:
            cursor.execute(query_class)
            class_id = cursor.lastrowid
        except mysql.connector.Error as err:
            query_get_class_id = ("SELECT id FROM {} WHERE label=\"{}\"".format(table, class_label))
            cursor.execute(query_get_class_id)
            for (id,) in cursor:
                class_id = id
        return class_id

    def get_vx_class_label(self, class_id):
        return self.get_class_label(class_id, "vertex_class")

    def add_vx_class_id(self, class_label):
        return self.add_class_id(class_label, "vertex_class")

    def newV(self, class_label, name):
        class_id = self.add_vx_class_id(class_label)
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
                "SELECT id, class as cid, name FROM vertex WHERE name=\"{}\"".format(name))
            cursor = self.be.cnx.cursor(buffered=True)
            cursor.execute(query_vx)
            for (id, cid, name,) in cursor:
                class_label = self.get_vx_class_label(cid)
                vx = Vertex(cid, class_label, id, name)
        return vx

    def get_edge_class_label(self, class_id):
        return self.get_class_label(class_id, "edge_class")

    def add_edge_class_id(self, class_label):
        return self.add_class_id(class_label, "edge_class")

    def getVertexById(self, id):
        cursor = self.be.cnx.cursor(buffered=True)
        query_vx = ("SELECT class as cid, name FROM vertex WHERE id=\"{}\"".format(id))
        cursor.execute(query_vx)
        vx = None
        for (cid, name) in cursor:
            class_label = self.get_class_label(cid, "vertex_class")
            vx = Vertex(cid, class_label, id, name)
        return vx

    def newE(self, class_label, tail, head, relation):
        vx_tail = self.getVertexByName(tail)
        vx_head = self.getVertexByName(head)
        tail_id = vx_tail.vx_id
        head_id = vx_head.vx_id
        class_id = self.add_edge_class_id(class_label)
        edge = None
        query_vx = (
            "INSERT INTO edge (class, relation, tail, head) VALUES ({}, \"{}\")".format(class_id, relation, tail_id,
                                                                                        head_id))
        cursor = self.be.cnx.cursor(buffered=True)
        try:
            cursor.execute(query_vx)
            edge_id = cursor.lastrowid
            # (edge_class_id, edge_class_label, edge_id, relation, tail_vx, head_vx)
            edge = Edge(class_id, class_label, edge_id, relation, vx_tail, vx_head)
        except mysql.connector.Error as err:
            query_vx = (
                "SELECT id, class as cid, relation, tail, head FROM edge WHERE relation=\"{}\"".format(relation))
            cursor = self.be.cnx.cursor(buffered=True)
            cursor.execute(query_vx)
            for (id, cid, relation, tail, head,) in cursor:
                edge = Edge(cid, class_label, id, relation, vx_tail, vx_head)
        return edge

    def getVertexByName(self, name):
        cursor = self.be.cnx.cursor(buffered=True)
        query_vx = ("SELECT id, class as cid FROM vertex WHERE name=\"{}\"".format(name))
        cursor.execute(query_vx)
        vx = None
        for (id, cid,) in cursor:
            class_label = self.get_class_label(cid, "vertex_class")
            vx = Vertex(cid, class_label, id, name)
        return vx

    def newE(self, tail, head, relation):
        vx_tail = self.getVertexByName(tail)
        vx_head = self.getVertexByName(head)
        edge_class_id = self.add_class_id(relation, "edge_class")
        print(vx_tail.to_string())
        print(vx_head.to_string())
        print("edge class id: ", edge_class_id)


class Traversal:
    def __init__(self):
        self.be = be.backend()
        self.service = GraphService(self.be)

    def addV(self, class_label, name):
        return self.service.newV(class_label, name)

    def V(self, name):
        return self.service.getVertexByName(name)

    def addE(self, tail, head, relation):
        return self.service.newE(tail, head, relation)


def test_run(g):
    vx = g.addV("depot", "Novato")
    print(vx.to_string())
    vx = g.addV("logic", "Aristotle")
    print(vx.to_string())
    vx = g.addV("author", "Thomas Mann")
    print(vx.to_string())
    vx = g.addV("human", "Socrates")
    print(vx.to_string())
    print("~~~~~~~ Testing Edges ~~~~~~~~")
    g.addE("philosopher", "Aristotle", "Socrates", "dynamic")


def test_check(g):
    vx_service = GraphService(g.be)
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
