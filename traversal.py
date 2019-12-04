import sys
import os
import random
import pickle

import backend as be
import mysql
from mysql.connector.errors import Error

import numpy as np

cache_dir = "/Users/jclaudel/work/Data/reseau_cache/"
simulated_graph_path = cache_dir + "simulated_graph.pkl"

if not os.path.exists(cache_dir):
    os.mkdir(cache_dir)


class Vertex:
    def __init__(self, class_id, label, vx_id, name):
        self.class_id = class_id
        self.label = label
        self.vx_id = vx_id
        self.name = name

    def to_string(self):
        return "class id: {};\t label: {};\tvertex \tid: {};\tname: {};". \
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
        return "class id: {};\t label: {};\tvertex \tid: {};\tname: {};\t({}, {})". \
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

    def forwardV(self, vx):
        cursor = self.be.cnx.cursor(buffered=True)
        query_forward = ("SELECT head FROM edge WHERE tail={};".format(vx.vx_id))
        cursor.execute(query_forward)
        out_vx_list = []
        for (head, ) in cursor:
            ov = self.getVertexById(head)
            out_vx_list += [ov]
        return out_vx_list

    def getVdegree(self, vx):
        ovx_list = self.forwardV(vx)
        return len(ovx_list)

    def getEdgeById(self, id):
        cursor = self.be.cnx.cursor(buffered=True)
        query_edge = ("SELECT class as cid, relation, tail, head FROM edge WHERE id=\"{}\"".format(id))
        cursor.execute(query_edge)
        edge = None
        for (cid, relation, tail, head, ) in cursor:
            class_label = self.get_class_label(cid, "edge_class")
            vx_tail = self.getVertexById(tail)
            vx_head = self.getVertexById(head)
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

    def newE(self, class_label, tail, head, relation):
        vx_tail = self.getVertexByName(tail)
        vx_head = self.getVertexByName(head)
        tail_id = vx_tail.vx_id
        head_id = vx_head.vx_id
        class_id = self.add_edge_class_id(class_label)
        # print("**** class_id: {}\trelation: {}\ttail_id: {}\thead_id: {}".
        #       format(class_id, relation, tail_id, head_id))
        edge = None
        query_vx = (
            "INSERT INTO edge (class, relation, tail, head) VALUES ({}, \"{}\", {}, {})".format(class_id, relation, tail_id,
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

    def get_tablenames(self):
        query = """
            select table_schema as database_name, table_name
            from information_schema.tables
            where table_type = 'BASE TABLE' and table_schema = database() 
            order by database_name, table_name;        
        """
        table_name_list = []
        cursor = self.be.cnx.cursor(buffered=True)
        try:
            cursor.execute(query)
            for (database_name, table_name,) in cursor:
                table_name_list += [table_name]
        except mysql.connector.Error as err:
            print("********** ", err)
        return table_name_list

    # should be used with care
    def truncate_all_tables(self):
        tables = self.get_tablenames()
        cursor = self.be.cnx.cursor(buffered=True)
        for table_name in tables:
            try:
                truncate_query = "TRUNCATE TABLE {};".format(table_name)
                cursor.execute(truncate_query)
            except:
                pass
        print("truncated tables: ", tables)

    def integrity_test(self, G):
        verset, edge_set = G
        # for inode in verset:
        #     print(inode, verset[inode])
        query_vx = "SELECT id, class as cid, name FROM vertex;"
        cursor = self.be.cnx.cursor(buffered=True)
        cursor.execute(query_vx)
        vx_hit = 0
        for (id, cid, name) in cursor:
            print("id: {} class: {} name: {}".format(id, cid, name))
            if verset[id]["name"] == name:
                vx_hit += 1

        query_edge = "SELECT id, class as cid, relation, tail, head FROM edge;"
        cursor.execute(query_edge)
        edge_hit = 0
        for (id, cid, relation, tail, head) in cursor:
            print("id: {} class: {} relation: {} tail: {} head: {}".format(id, cid, relation, tail, head))
            if edge_set[relation]["id"] == id:
                edge_hit += 1

        print("# vertex hit: ", vx_hit)
        print("# edge hit: ", edge_hit)

    # deprecated
    def test_newE(self, tail, head, relation):
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

    def addE(self, class_label, tail, head, relation):
        return self.service.newE(class_label, tail, head, relation)

    def V(self, vx_id):
        return self.service.getVertexById(vx_id)

    def outV(self, vx_id):
        vx = self.V(vx_id)
        return self.service.forwardV(vx)

    def degreeV(self, vx_id):
        self.outV(vx_id)
        vx = self.V(vx_id)
        return self.service.getVdegree(vx)


def cache_simulated_graph(G):
    with open(simulated_graph_path, "wb") as f:
        pickle.dump(G, f)


def simulate_test_gen_graph(g):
    nV = 10000      # number of nodes
    nL = 20         # number of layers
    verset = dict()     # vertex set
    layers = dict()
    edge_set = dict()

    # generate 10 vertex classes
    vertex_labels = list(range(1, 11))
    vertex_labels = ["vxclass" + str(i) for i in vertex_labels]
    print("vertex labels: ", vertex_labels)
    edge_labels = list(range(1, 11))
    edge_labels = ["edgeclass" + str(i) for i in edge_labels]
    print("edge labels: ", edge_labels)
    # build Vertex labels
    kk = 0
    for i in range(1, nV +1):
        name = "v-{}".format(i)
        verset[i] = dict()
        verset[i]["name"] = name
        label = random.choice(vertex_labels)
        verset[i]["label"] = label
        kk += 1
        # print("==id: {}\t label: {}".format(i, label))
    root_node = 1
    layer_sizes = np.random.multinomial(nV, np.ones(nL)/nL, size=1)[0]
    print("--- layer sizes ", layer_sizes)
    sum_sizes = 0
    for sz in layer_sizes:
        sum_sizes += sz
    print("--- sum of sizes: {}".format(sum_sizes))

    ix_list = list(range(1, nV + 1))
    random.shuffle(ix_list)
    ngl = 0
    for k in range(len(layer_sizes)):
        sz = layer_sizes[k]
        # print(k, ngl, sz)
        gen_set = ix_list[ngl:ngl + sz]
        if root_node in gen_set:
            gen_set.remove(root_node)
        ngl += len(gen_set)
        layers[k+1] = gen_set
    for k in layers:
        layer_vertices = layers[k]
        nlv = len(layer_vertices)
        print("{})\tsize: {}\t{}".format(k, nlv, layer_vertices))
    print("total # layers elements: {}".format(ngl))
    print("# layers: {}".format(len(layers)))
    # generate edges
    # connect root node to first layer
    m = 0
    for n in layers[1]:
        m += 1
        relation = "edge-{}".format(m)
        edge_set[relation] = dict()
        edge_set[relation]["id"] = m
        edge_set[relation]["arc"] = (verset[root_node]["name"], verset[n]["name"])
        label = random.choice(edge_labels)
        edge_set[relation]["label"] = label

    print("# edges: ", len(edge_set))

    for k in range(2, nL + 1):
        prev_layer = layers[k - 1]
        # print("{}) # previous layer: {}".format(k, len(prev_layer)))
        current_layer = layers[k]
        # print("{}) # current layer: {}".format(k, len(current_layer)))
        for tail in prev_layer:
            repeat = random.randint(3, 10)
            for j in range(repeat):
                head = random.choice(current_layer)
                m += 1
                relation = "edge-{}".format(m)
                edge_set[relation] = dict()
                edge_set[relation]["id"] = m
                edge_set[relation]["arc"] = (verset[tail]["name"], verset[head]["name"])
                label = random.choice(edge_labels)
                edge_set[relation]["label"] = label

    G = (verset, edge_set)
    cache_simulated_graph(G)
    dump_simulate_graph(G)
    print("# vertices: {}\t generated: {}".format(len(verset), kk))
    print("# edges: {}\t generated: {}".format(len(edge_set), m))


def dump_simulate_graph(G):
    verset, edge_set = G
    for node in verset:
        print(node, verset[node])
    for edge in edge_set:
        print(edge, edge_set[edge])


def populate_from_simulated_graph(g):
    with open(simulated_graph_path, "rb") as f:
        G = (verset, edge_set) = pickle.load(f)
        dump_simulate_graph(G)
    for inode in verset:
        vx = g.addV(verset[inode]['label'], verset[inode]['name'])
        verset[inode]["id"] = vx.vx_id
        print(inode, verset[inode])
    for relation in edge_set:
        tail, head = edge_set[relation]['arc']
        edge = g.addE(edge_set[relation]['label'], tail, head, relation)
        edge_set[relation]["id"] = edge.edge_id
        print(relation, edge_set[relation])
    cache_simulated_graph(G)


def integrity_test(g):
    with open(simulated_graph_path, "rb") as f:
        G = (verset, edge_set) = pickle.load(f)
        dump_simulate_graph(G)
    service = GraphService(g.be)
    service.integrity_test(G)


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


def test_db_utilities(g):
    service = GraphService(g.be)
    # service.get_tablenames()
    service.truncate_all_tables()


def test_graph_commands(g):
    for vx_id in range(2, 10):
        ovx_list = g.outV(vx_id)
        for vx in ovx_list:
            print(vx.to_string())
        print("list len: ", len(ovx_list))
        print("degree: ", g.degreeV(vx_id))


if __name__ == "__main__":
    g = Traversal()
    # test_run(g)
    # test_check(g)
    # test_db_utilities(g)
    # simulate_test_gen_graph(g)
    # populate_from_simulated_graph(g)
    # integrity_test(g)
    test_graph_commands(g)
