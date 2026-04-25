from collections import deque

def topological_sort(graph):
    """
    :param graph: directed acyclic graph (DAG)
    :return:
        sorted: a list of vertices in topological sorting order,
        throws error if g is not a DAG
    """
    count={}

    # Step 1: initialize count (in-degree)
    for v in graph.get_vertices():
        count[v] = len(graph.inbound_neighbors(v))

    # Step 2: initialize queue with nodes of in-degree 0
    q = deque() #this is theoretically a double ended queue, however we use a single end
    for v in graph.get_vertices():
        if count[v] == 0:
            q.append(v)

    sorted_list = [] #the result of our algorithm is this sorted list of vveritices, in topological order

    # Step 3: process queue
    while q: #while queue is not empty -> it means we still have unprocessed vertices
        current = q.popleft()  #alternatilvely we can just use pop here
        sorted_list.append(current)

        # "remove" current by decreasing neighbors' counts
        for n in graph.neighbors(current):
            count[n] -= 1 #ocunt is the dynamical representation of our graph state, we dont actually change the original one
            if count[n] == 0:
                q.append(n)

    # Step 4: check for cycle -> if the queue was empty but there arent all the nodes in the list
    #it means that some nodes with degree grreater than zero were still in graph, this implies the ciclicity
    if len(sorted_list) < graph.get_v():
        raise ValueError("Not a DAG!")

    return sorted_list