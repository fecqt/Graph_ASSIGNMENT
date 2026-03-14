#Denote V - number of vertices, e - number of edges
from GraphIterator import GraphIterator
from utils import TraversalType


class Graph:
    #implemented using list of neighbours
    def __init__(self, directed = False, weighted = False):
        self.__list_of_neighbors = {}
        self.__directed = directed
        self.__weighted = weighted

    def change_if_directed(self, directed):
        if self.__directed == directed:
            print ("The graph is already in the desired orientation.")
            return

        if not directed:
            #We move from directed -> undirected, so if we have the edge (v1, v2) we also
            #must have the edge (v2, v1) now since there's no direction.
            for vertex1 in self.__list_of_neighbors.keys():
                for vertex2 in self.__list_of_neighbors[vertex1].keys():
                    if vertex1 not in self.__list_of_neighbors[vertex2]:
                        weight = self.__list_of_neighbors[vertex1][vertex2]
                        self.__list_of_neighbors[vertex2][vertex1] = weight

        #Moving from undirected -> directed keeps the Graph the same, but we will consider
        #(v1, v2) and (v2, v1) as two different edges.
        self.__directed = directed

    def change_if_weighted(self, weighted):
        if self.__weighted == weighted:
            raise ValueError("The graph is already in the desired option.")

        self.__weighted = weighted
        for u in self.__list_of_neighbors.keys():
            for v in self.__list_of_neighbors[u]:
                self.__list_of_neighbors[u][v] = 0 if weighted else None


    def set_weight(self, startpoint, endpoint, weight):
        if not self.__weighted:
            raise ValueError("Graph is unweighted.")
        if not self.is_edge(startpoint, endpoint):
            raise ValueError(f"The edge between {startpoint} and {endpoint} does not exist.")

        self.__list_of_neighbors[startpoint][endpoint] = weight
        if not self.__directed:
            #if it's undirected, we also make (endpoint, startpoint) edge the same weight.
            self.__list_of_neighbors[endpoint][startpoint] = weight


    def get_weight(self, startpoint, endpoint):
        if not self.__weighted:
            raise ValueError("Graph is unweighted.")
        if not self.is_edge(startpoint, endpoint):
            raise ValueError(f"The edge between {startpoint} and {endpoint} does not exist.")

        #Here we simply return the value between edge startpoint-endpoints, so its weight.
        return self.__list_of_neighbors[startpoint][endpoint]



    def add_edge(self, startpoint, endpoint, weight = 0):
        #O(V)
        if startpoint not in self.__list_of_neighbors:
            raise ValueError("The starting vertex does not exist")
        if endpoint not in self.__list_of_neighbors:
            raise ValueError("The endpoint vertex does not exist")

        w = weight if self.__weighted else None #so we have a weight if the graph is weighted

        #Creating edge from startpoint to endpoint. This instruction will both assign weight
        #, but also create the edge if not already existing.
        self.__list_of_neighbors[startpoint][endpoint] = w

        #Creating edge from endpoint to startpoint now if the Graph is undirected
        if not self.__directed:
            self.__list_of_neighbors[endpoint][startpoint] = w


    def add_vertex(self, vertex):
        #O(1)
        if vertex not in self.__list_of_neighbors.keys():
            self.__list_of_neighbors[vertex]={}
        else:
            raise ValueError("The vertex already exists.")

    def remove_edge(self, startpoint, endpoint):
        #O(V)
        if startpoint in self.__list_of_neighbors.keys() and endpoint in self.__list_of_neighbors[startpoint]:
            del self.__list_of_neighbors[startpoint][endpoint]
            #if it's undirected, we simply remove the reverse edge too
            if not self.__directed:
                if startpoint in self.__list_of_neighbors[endpoint]:
                    del self.__list_of_neighbors[endpoint][startpoint]
        elif startpoint not in self.__list_of_neighbors.keys():
            raise ValueError("The starting vertex does not exist.")
        elif endpoint not in self.__list_of_neighbors.keys():
            raise ValueError("The endpoint vertex does not exist.")
        elif endpoint not in self.__list_of_neighbors[startpoint]:
            raise ValueError("The edge does not exist.")

    def remove_vertex(self,vertex):
        #O(V + e)
        if vertex not in self.__list_of_neighbors:
            raise ValueError("The vertex does not exist")
        self.__list_of_neighbors.pop(vertex)
        for v in self.__list_of_neighbors:
            if vertex in self.__list_of_neighbors[v].keys():
                self.__list_of_neighbors[v].pop(vertex)

    def get_v(self):
        #O(1)
        return len(self.__list_of_neighbors.keys())

    def get_e(self):
        #O(V)
        e=0
        for v in self.__list_of_neighbors:
            e += len(self.__list_of_neighbors[v])
        return e

    def is_edge(self,startpoint,endpoint):
        #O(e/V)
        if startpoint not in self.__list_of_neighbors.keys():
            raise ValueError("The starting vertex does not exist")
        if endpoint not in self.__list_of_neighbors.keys():
            raise ValueError("The endpoint vertex does not exist")
        #This works in undirected too, since having an edge from S-D also implies the edge from D-S
        return endpoint in self.__list_of_neighbors[startpoint]

    def neighbors(self, vertex):
        #O(1)
        if vertex not in self.__list_of_neighbors:
            raise ValueError("Vertex does not exist.")

        return list(self.__list_of_neighbors[vertex])

    def inbound_neighbors(self, vertex):
        #O(V + e), if e > V we would have O(e)
        if vertex not in self.__list_of_neighbors:
            raise ValueError("Vertex does not exist.")
        if not self.__directed:
            #For an undirected graph, the list of inbound neighbours is the same as outbound ones.
            return list(self.__list_of_neighbors[vertex])

        #For directed, we have to search for the vertex in the neighbours of every other vertex
        #to see what vertices have it as an outbound (those will be its inbound vertices)
        inbound_neighbors = []
        for node, adj_list in self.__list_of_neighbors.items():
            if vertex in adj_list:
                inbound_neighbors.append(node)

        return list(inbound_neighbors)

    def get_vertices(self):
        #O(1)
        return list(self.__list_of_neighbors.keys())

    def get_edges(self):
        #O(V + e)
        edges = []
        for start_node, adj_list in self.__list_of_neighbors.items():
            for end_node in adj_list:
                edges.append((start_node, end_node))

        return edges

    def __str__(self):
        #O(V + e)
        #To specify when printing what type of Graph we're working with.
        direction_type = "directed" if self.__directed else "undirected"
        weight_type = "weighted" if self.__weighted else "unweighted"
        result_to_print_type = f"{direction_type} {weight_type}\n"

        printed_edges = set()

        for vertex, adj_list in self.__list_of_neighbors.items():
            if not adj_list:
                result_to_print_type += f"{vertex}\n"
            for v, weight in adj_list.items():
                edge = tuple(sorted((vertex, v))) if not self.__directed else (vertex, v)
                if edge not in printed_edges:
                    weight_info = f"(weight: {weight})" if self.__weighted else ""
                    result_to_print_type += f"{vertex} {v} {weight_info}\n"
                    printed_edges.add(edge)


        return result_to_print_type.strip()

    def iterator(self, starting_vertex, type_of_traversal:TraversalType) -> GraphIterator:
        """
        :param starting_vertex: the vertex the traversal starts on
        :param type_of_traversal: BFS or DFS
        :return: newly created GraphIterator for our object ;D
        """
        return GraphIterator(self, starting_vertex, type_of_traversal)

    @staticmethod
    def create_from_file(filename):
        """
        Creates and returns a Graph object from a file.

        File format:
        - first line: "<directed/undirected> <weighted/unweighted>"
        - next lines:
            * 1 token: isolated vertex
            * 2 tokens: unweighted edge
            * 3 tokens: weighted edge
        """

        #open file, read all lines
        with open(filename, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        #treat the case where the file is empty
        if not lines:
            raise ValueError("The file is empty.")

        #read the first line -> this tells you what type of graph you have
        first_line = lines[0].split()

        #treat the case in which the first line is not valid
        if len(first_line) != 2:
            raise ValueError("First line must contain exactly 2 words.")

        #save into variables the direction type(directed/undirected graph) and
        #if it is weighted or not
        direction_type, weight_type = first_line

        #Create the graph accoring to these variables
        if direction_type == "directed":
            directed = True
        elif direction_type == "undirected":
            directed = False
        else:
            raise ValueError("Graph orientation must be 'directed' or 'undirected'.")

        if weight_type == "weighted":
            weighted = True
        elif weight_type == "unweighted":
            weighted = False
        else:
            raise ValueError("Graph type must be 'weighted' or 'unweighted'.")

        graph = Graph(directed=directed, weighted=weighted)

        #for the rest of the lines split into tokens
        for line in lines[1:]:
            parts = line.split()

            #we have just a node, no neighbour, no weight
            if len(parts) == 1:
                vertex = parts[0]
                if vertex not in graph.get_vertices():
                    graph.add_vertex(vertex)

            #we have a node with a neighbour
            elif len(parts) == 2:
                start, end = parts

                #if it is weighted each lines must have 3 tokens(according to the lab document)
                if weighted:
                    raise ValueError("Weighted graphs must specify a weight for each edge.")

                #add the edge to the graph
                if start not in graph.get_vertices():
                    graph.add_vertex(start)
                if end not in graph.get_vertices():
                    graph.add_vertex(end)

                graph.add_edge(start, end)

            #we have a node with a neighbour and a weight between them
            elif len(parts) == 3:
                start, end, weight = parts

                #this case is not valid unless we have a weighted graph
                if not weighted:
                    raise ValueError("Unweighted graphs cannot have weighted edges in file.")

                #add the edge to the graph
                if start not in graph.get_vertices():
                    graph.add_vertex(start)
                if end not in graph.get_vertices():
                    graph.add_vertex(end)

                #treat the case were the weight is not a number -> raies error
                try:
                    weight = int(weight)
                except ValueError:
                    raise ValueError(f"Invalid weight '{weight}'. Weight must be an integer.")

                graph.add_edge(start, end, weight)

            else:
                raise ValueError(f"Invalid line in file: '{line}'")
        #return the created from file new graph object ;D
        return graph

