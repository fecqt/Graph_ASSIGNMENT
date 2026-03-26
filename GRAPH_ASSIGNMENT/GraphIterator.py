from utils import TraversalType
from collections import deque


class GraphIterator:
    def __init__(self, graph, starting_vertex, type_of_traversal):
        """
        Initializes an iterator for traversing a graph.
        params:
            - graph: the graph object on which the traversal is performed
            - starting_vertex: the vertex from which traversal starts
            - type_of_traversal: TraversalType.BFS or TraversalType.DFS
        """
        self.__graph = graph
        self.__starting_vertex = starting_vertex
        self.__current_vertex = starting_vertex
        self.__type_of_traversal = type_of_traversal

        self.__q = deque() #bfs traversal
        self.__s = [] #dfs traversal

        self.__visited = {starting_vertex}
        self.__parent = {starting_vertex: None}

        # Depth dictionary:
        # depth[v] = length of the path from starting_vertex to v
        self.__depth = {starting_vertex: 0}

    def getCurrent(self):
        """
        Returns the vertex at which the iterator currently points.

        Output:
            - the current vertex

        Raises:
            - Exception("Iterator is not valid") if the iterator is invalid

        When is the iterator invalid?
            - when traversal has finished and there are no more vertices to visit
        """
        if not self.is_valid():
            raise Exception("Iterator is not valid")
        return self.__current_vertex

    def first(self) -> None:
        """
        Resets the iterator to the initial traversal state.

        Effect:
            - current vertex becomes the starting vertex again
            - queue is cleared
            - stack is cleared
            - discovered vertices are reset
            - parent information is reset
            - depth information is reset

        After calling this method:
            - traversal starts again from the beginning
            - the iterator behaves like a freshly created iterator
        """
        self.__current_vertex = self.__starting_vertex

        # Clear BFS and DFS auxiliary structures.
        self.__q = deque()
        self.__s = []

        # Only the start vertex is known/discovered at reset.
        self.__visited = {self.__starting_vertex}

        # Reset path reconstruction info.
        self.__parent = {self.__starting_vertex: None}

        # Reset distance/path length info.
        self.__depth = {self.__starting_vertex: 0}

    def next(self) -> None:
        """
        Advances the iterator to the next vertex in the traversal.

        Behavior:
            - for BFS: visits vertices level by level using a queue
            - for DFS: visits vertices depth-first using a stack

        Raises:
            - Exception("Iterator is not valid") if the iterator is invalid
        """
        if not self.is_valid():
            raise Exception("Iterator is not valid")

        if self.__type_of_traversal == TraversalType.BFS:
            # We are currently at self.__current_vertex.
            # We inspect all its neighbors.
            for neighbor in self.__graph.neighbors(self.__current_vertex):
                # If the neighbor was never discovered before,
                # schedule it for future visit.
                if neighbor not in self.__visited:
                    # Mark it as discovered immediately so it is not added twice.
                    self.__visited.add(neighbor)

                    # Record how we reached this neighbor.
                    self.__parent[neighbor] = self.__current_vertex

                    # Its distance/path length is one more than current vertex.
                    self.__depth[neighbor] = self.__depth[self.__current_vertex] + 1

                    # BFS uses a queue, so neighbors go to the end.
                    self.__q.append(neighbor)

            # After processing the current vertex, move to the next one in queue.
            if len(self.__q) == 0:
                # No more vertices left to visit.
                # Iterator becomes invalid.
                self.__current_vertex = ""
            else:
                # FIFO order: take the oldest scheduled vertex.
                self.__current_vertex = self.__q.popleft()

        elif self.__type_of_traversal == TraversalType.DFS:
            # We inspect all neighbors of the current vertex.
            neighbors = self.__graph.neighbors(self.__current_vertex)

            # Reverse the neighbors so that when pushed onto the stack,
            # they are later popped in the original left-to-right order.
            for neighbor in reversed(neighbors):
                # If neighbor was not discovered before,
                # schedule it for future visit.
                if neighbor not in self.__visited:
                    # Mark as discovered immediately.
                    #self.__visited.add(neighbor) - I have commented this so that
                    #it will go as deep as possible in the traversal. Otherwise it would pick a
                    #shallow DFS traversal.
                    """
                    # Record parent for path reconstruction.
                    self.__parent[neighbor] = self.__current_vertex

                    # Record path length from the start.
                    self.__depth[neighbor] = self.__depth[self.__current_vertex] + 1
                    """

                    # DFS uses a stack, so neighbors are pushed on top.
                    self.__s.append((neighbor, self.__current_vertex))


            next_vertex = ""
            while self.__s:
                candidate, potential_parent = self.__s.pop()
                if candidate not in self.__visited:
                    next_vertex = candidate
                    self.__visited.add(candidate)
                    self.__parent[candidate] = potential_parent
                    self.__depth[candidate] = self.__depth[potential_parent] + 1
                    break
            self.__current_vertex = next_vertex if next_vertex != "" else ""
            """
            # After processing the current vertex, move to the next one in stack.
            if len(self.__s) == 0:
                # No more vertices left to visit.
                # Iterator becomes invalid.
                self.__current_vertex = ""
            else:
                # LIFO order: take the most recently added vertex.
                self.__current_vertex = self.__s.pop()
            """


    def is_valid(self) -> bool:
        """
        Checks whether the iterator still points to a valid vertex.
        - the empty string "" represents an invalid iterator state
        returns: True if the iterator still points to a valid vertex, False otherwise
        """
        return self.__current_vertex != ""

    def get_path_length(self) -> int:
        """
        Returns the length of the path from the starting vertex
        to the current vertex.

        Output:
            - an integer representing the path length

        Raises:
            - Exception("Iterator is not valid") if the iterator is invalid

        Meaning:
            - for BFS: this is the shortest distance from the start vertex
            - for DFS: this is the length of the path in the DFS traversal tree

        Complexity:
            - Theta(1), because the value is already stored in __depth
        """
        if not self.is_valid():
            raise Exception("Iterator is not valid")
        return self.__depth[self.__current_vertex]

    def get_path(self) -> list:
        """
        Returns the path from the starting vertex to the current vertex.
        (it works its way backwards through the parents)

        Output:
            - a list of vertices of the form [start, ..., current]

        Raises:
            - Exception("Iterator is not valid") if the iterator is invalid
        """
        if not self.is_valid():
            raise Exception("Iterator is not valid")

        path = []
        vertex = self.__current_vertex

        # Follow parent links backwards until we reach the start vertex,
        # whose parent is None.
        while vertex is not None:
            path.append(vertex)
            vertex = self.__parent[vertex]

        # We built the path from current back to start,
        # so reverse it to obtain start -> ... -> current.
        path.reverse()
        return path