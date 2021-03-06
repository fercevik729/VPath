#
# Pathfinder Visualization
# by Furkan Ercevik
# Started 4 November 2021
#
import itertools
from pathlib import Path
from pathlib import PurePath
import time
import pygame
import sys

# CONSTANTS + SETUP
pygame.init()
LOGO = pygame.image.load("assets/magnifying.png")
pygame.display.set_icon(LOGO)
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("VPath - Pathfinder Visualizer")
COLORS = {"START": (10, 17, 114), "WHITE": (255, 255, 255), "BLACK": (0, 0, 0), "RED": (255, 0, 0),
          "FOUND": (72, 170, 173), "FRONTIER": (1, 96, 100), "PATH": (130, 238, 253)}
DELAY = 0.004


def time_it(method):
    """
    Timing decorator that outputs how long an algorithm takes to find or not find a path
    :return: wrapper function
    """

    def wrapper_time_it(self):
        start_time = time.time()
        method(self)
        print("", end="\r")
        print(f"The search algorithm took {time.time() - start_time:.2f} seconds", end="")

    return wrapper_time_it


# The Graph class will be used to organize all the Node objects in one place and simulate the visualization process
class Graph(object):

    # Initialize the squares
    def __init__(self):
        """
        Constructs a Graph object that is 40 x 40 Node objects
        """
        self.nodes = []
        self.dest_pos = None
        self.start_pos = None
        self.drag = False
        self.clear_drag = False

        self.MAX_ROWS = 32
        self.MAX_COLS = 40

        x = 0
        y = 5
        for n in range(self.MAX_ROWS):
            row = []
            for c in range(self.MAX_COLS):
                row.append((Node(n, c, x, y, 20, 20)))
                x += 25
            self.nodes.append(row)
            x = 0
            y += 25

    def clear_graph(self) -> None:
        """
        Clears the graph to its original state
        :return:
        """
        self.clear_visualization()
        self.start_pos = None
        self.dest_pos = None
        for r, row in enumerate(self.nodes):
            for c, col in enumerate(row):
                n = self.nodes[r][c]
                if n.dest:
                    n.toggle_dest()
                if n.start:
                    n.toggle_start()
                if n.wall_status():
                    n.toggle_wall()

    def clear_visualization(self) -> None:
        """
        Clears the visualization, returning it to the prior state of the Graph
        :return: None
        """
        for r, row in enumerate(self.nodes):
            for c, col in enumerate(row):
                n = self.nodes[r][c]
                if not n.wall_status():
                    n.change_color(COLORS["WHITE"])

    def handle_event(self, event: pygame.event) -> None:
        """
        Graph checks if certain keys are pressed and performs actions accordingly
        :param event:
        :return:
        """
        if event.type == pygame.KEYDOWN:
            # Save the maze
            if event.key == pygame.K_m:
                self.save_maze()
            if event.key in range(48, 58):
                self.load_maze(event.key - 48)
            # Clear graph
            if event.key == pygame.K_c:
                self.clear_graph()
            # Call one of the search algorithms
            if event.key == pygame.K_e:
                self.double_dijkstra()
            if event.key == pygame.K_SPACE:
                self.dijkstra_solve()
            if event.key == pygame.K_a:
                self.a_star_solve()
            if event.key == pygame.K_q:
                self.double_a_star()
            # Clear visualization
            if event.key == pygame.K_v:
                self.clear_visualization()
            # Make the node a start node
            if event.key == pygame.K_s:
                x, y = pygame.mouse.get_pos()
                if x in range(0, 1025) and y in range(0, 1025):
                    r = y // 25
                    c = x // 25
                    node = self.nodes[r][c]
                    if (not self.start_pos or self.start_pos == (r, c)) and not node.wall_status():
                        self.clear_visualization()
                        node.toggle_start()
                        self.start_pos = (r, c) if node.start else None
            # Make the node a destination node
            if event.key == pygame.K_d:
                x, y = pygame.mouse.get_pos()
                if x in range(0, 1025) and y in range(0, 1025):
                    r = y // 25
                    c = x // 25
                    node = self.nodes[r][c]
                    if (not self.dest_pos or self.dest_pos == (r, c)) and not node.wall_status():
                        self.clear_visualization()
                        node.toggle_dest()
                        self.dest_pos = (r, c) if node.dest else None

        # Check for mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if x in range(0, 1025) and y in range(0, 1025):
                r = y // 25
                c = x // 25
                node = self.nodes[r][c]
                if event.button == pygame.BUTTON_LEFT:
                    if not node.wall_status() and not(node.start or node.dest):
                        self.clear_visualization()
                        node.toggle_wall()
                    self.drag = True
                    self.clear_drag = False
                elif event.button == pygame.BUTTON_RIGHT:
                    if node.wall_status():
                        self.clear_visualization()
                        node.toggle_wall()
                    self.clear_drag = True
                    self.drag = False
        elif event.type == pygame.MOUSEBUTTONUP:
            self.drag = False
            self.clear_drag = False
        elif event.type == pygame.MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            if x in range(0, 1025) and y in range(0, 1025):
                r = y // 25
                c = x // 25
                n = self.nodes[r][c]
                if (n.wall_status() and self.clear_drag) or (not n.wall_status() and self.drag and
                                                             not (n.start or n.dest)):
                    n.toggle_wall()

    def draw(self, s):
        """
        Draws the grid
        :param s:
        :return:
        """
        for row in self.nodes:
            for n in row:
                n.draw(s)

    @time_it
    def dijkstra_solve(self):
        """
        Creates two dictionaries: one of the distances and of the preceding nodes for each respective node
        and backtracks to find the shortest path
        :return: True if a path could be found, otherwise False
        """
        self.clear_visualization()
        self.draw(screen)
        # Start solving from the start_position
        # Once the destination is reached, map the shortest route in red color
        if not self.start_pos or not self.dest_pos:
            return False
        # Create a dictionary of all the distances
        # Create a dictionary of all the previous nodes
        dists = {}
        prevs = {}
        for r, row in enumerate(self.nodes):
            for c, col in enumerate(row):
                dists[(r, c)] = float('inf')
                prevs[(r, c)] = None
        dists[self.start_pos] = 0
        # Start the dict
        collection = {self.start_pos: 0}
        # While the dict is not empty
        while collection:
            # Get the vertex with the lowest cost
            cv = min(collection, key=lambda t: collection[t])
            node = self.nodes[cv[0]][cv[1]]
            self.draw_updated_node(COLORS["FOUND"], node)
            # Delete that vertex from collection
            del collection[cv]
            if cv == self.dest_pos:
                break
            # Get the neighbors of the current node and iterate over them
            neighbors = self.get_adj_nodes(cv[0], cv[1])
            # Call dijkstra's helper method
            collection, dists, prevs = self.dijkstra_helper(collection, dists, prevs, cv, neighbors)

        # Backtrack from destination node
        self.backtrack(prevs, self.dest_pos)

    @time_it
    def double_dijkstra(self):
        """
        Creates two pairs of dictionaries: one pair of the distances and of the preceding nodes for each respective node
        and another pair of distances from the destination position and succeeding nodes
        :return: True if a path could be found, otherwise False
        """
        self.clear_visualization()
        self.draw(screen)
        # Start solving from the start_position
        # Once the destination is reached, map the shortest route in red color
        if not self.start_pos or not self.dest_pos:
            return
        # Create dictionaries of all the distances from start_pos and dest_pos
        # Create dictionaries of all the previous and succeeding nodes
        dists_s = {}
        dists_d = {}
        prevs = {}
        succs = {}

        for r, row in enumerate(self.nodes):
            for c, col in enumerate(row):
                dists_s[(r, c)] = float('inf')
                dists_d[(r, c)] = float('inf')
                prevs[(r, c)] = None
                succs[(r, c)] = None

        dists_s[self.start_pos] = 0
        dists_d[self.dest_pos] = 0
        # Start the priority queues
        pq_s = {self.start_pos: 0}
        pq_d = {self.dest_pos: 0}

        inters = None

        # While the priority queue is not empty
        while pq_s and pq_d:
            # Get the vertex with the lowest cost from each of the queues
            cv = min(pq_s, key=lambda t: pq_s[t])
            dist = pq_s[cv]
            node = self.nodes[cv[0]][cv[1]]
            self.draw_updated_node(COLORS["FOUND"], node)

            cv_2 = min(pq_d, key=lambda t: pq_d[t])
            dist_2 = pq_d[cv_2]
            node_2 = self.nodes[cv_2[0]][cv_2[1]]
            self.draw_updated_node(COLORS["FOUND"], node_2)

            # Remove the current vertices from the queues
            del pq_s[cv]
            del pq_d[cv_2]

            # Get the neighbors of the current node and iterate over them
            neighbors_s = self.get_adj_nodes(cv[0], cv[1])
            neighbors_d = self.get_adj_nodes(cv_2[0], cv_2[1])

            for neighbor_s, neighbor_d in itertools.zip_longest(neighbors_s, neighbors_d):

                diffs = [dist + 1 - dists_s[(neighbor_s.r, neighbor_s.c)] if neighbor_s else 0,
                         dist_2 + 1 - dists_d[(neighbor_d.r, neighbor_d.c)] if neighbor_d else 0]

                # If the new distance is smaller than the original cost put the neighbor in the priority queue with
                # the new distance cost
                if diffs[0] < 0:
                    # Update the color of the neighbor
                    self.draw_updated_node(COLORS["FRONTIER"], neighbor_s)
                    # Update the fastest route of the neighbor
                    prevs[(neighbor_s.r, neighbor_s.c)] = cv
                    pq_s[(neighbor_s.r, neighbor_s.c)] = dist + 1
                    dists_s[(neighbor_s.r, neighbor_s.c)] = dist + 1

                if diffs[1] < 0:
                    # Update the color of the neighbor
                    self.draw_updated_node(COLORS["FRONTIER"], neighbor_d)
                    # Update the fastest route of the neighbor
                    succs[(neighbor_d.r, neighbor_d.c)] = cv_2
                    pq_d[(neighbor_d.r, neighbor_d.c)] = dist_2 + 1
                    dists_d[(neighbor_d.r, neighbor_d.c)] = dist_2 + 1

            # If the vertex from the priority queue starting at the destination exists in the dict of previous nodes
            # a shortest path can be found
            if prevs[cv_2]:
                inters = cv_2
                break

        # Backtrack bidirectionally
        self.backtrack_2(prevs, succs, inters)

    @time_it
    def a_star_solve(self):
        """
        Using heuristics, this method solves the graph and calls a helper function to backtrack from the solution
        :return:
        """
        self.clear_visualization()
        self.draw(screen)

        # If there is no start or end node specified return False
        if not self.start_pos or not self.dest_pos:
            return False

        # Initialize dicts
        frontier = {self.start_pos: (0, 0, 0)}
        found = {}
        prevs = {}
        for r, row in enumerate(self.nodes):
            for c, col in enumerate(row):
                prevs[(r, c)] = None

        # While there are nodes in the frontier or the current vertex has not been found yet, continue
        while frontier:
            # Get the vertex with the minimum f-value and remove it from the frontier dict
            cv = min(frontier, key=lambda t: frontier[t][0])
            fgh = frontier[cv]
            # The raw distance is the second value in the fgh tuple which is g
            dist = fgh[1]
            del frontier[cv]

            # If the current vertex is the destination break out of the loop
            if cv == self.dest_pos:
                break
            # Otherwise color the current node and add it to the found dict
            node = self.nodes[cv[0]][cv[1]]
            found[node] = dist
            self.draw_updated_node(COLORS["FOUND"], node)

            frontier, prevs = self.heuristic(prevs, frontier, found, self.get_adj_nodes(cv[0], cv[1]), dist,
                                             self.dest_pos, cv)
        # Initiate backtracking
        self.backtrack(prevs, self.dest_pos)

    @time_it
    def double_a_star(self):
        """
        Using heuristics, this method solves the graph and calls a helper function to backtrack from the solution
        :return:
        """
        self.clear_visualization()
        self.draw(screen)

        # If there is no start or end node specified return False
        if not self.start_pos or not self.dest_pos:
            return False

        # Initialize dicts
        s_frontier = {self.start_pos: (0, 0, 0)}
        d_frontier = {self.dest_pos: (0, 0, 0)}

        s_found = {}
        d_found = {}
        prevs = {}
        succs = {}
        for r, row in enumerate(self.nodes):
            for c, col in enumerate(row):
                prevs[(r, c)] = None
                succs[(r, c)] = None

        # While there are nodes in the frontier or the current vertex has not been found yet, continue
        crux = None
        while s_frontier and d_frontier:
            # Get the vertices with the minimum f-value and remove it from the frontier dicts
            cv = min(s_frontier, key=lambda t: s_frontier[t][0])
            cv_2 = min(d_frontier, key=lambda t: d_frontier[t][0])
            fgh = s_frontier[cv]
            fgh2 = d_frontier[cv_2]
            # The raw distance is the second value in the fgh tuple which is g
            s_dist = fgh[1]
            d_dist = fgh2[1]

            del s_frontier[cv]
            del d_frontier[cv_2]

            # Put the current vertices in the found dictionary
            s_node = self.nodes[cv[0]][cv[1]]
            s_found[s_node] = s_dist
            self.draw_updated_node(COLORS["FOUND"], s_node)

            d_node = self.nodes[cv_2[0]][cv_2[1]]
            d_found[d_node] = d_dist
            self.draw_updated_node(COLORS["FOUND"], d_node)

            # Get all the neighbors for both current vertices
            s_neighbors = self.get_adj_nodes(cv[0], cv[1])
            d_neighbors = self.get_adj_nodes(cv_2[0], cv_2[1])

            # Call helper function
            s_frontier, prevs = self.heuristic(prevs, s_frontier, s_found, s_neighbors, s_dist, self.dest_pos, cv)

            d_frontier, succs = self.heuristic(succs, d_frontier, d_found, d_neighbors, d_dist, self.start_pos, cv_2)
            # If the vertex from the priority queue starting at the destination exists in the dict of previous nodes
            # a shortest path can be found
            if prevs[cv_2]:
                crux = cv_2
                break
        self.backtrack_2(prevs, succs, crux)

    # Helper methods for both algorithms
    def dijkstra_helper(self, queue, dists, prevs, cv, neighbors):
        for n in neighbors:
            old_distance = dists[(n.r, n.c)]
            new_distance = dists[cv] + 1
            # If the new distance is smaller than the original cost put the n in the priority queue with
            # the new distance cost
            if new_distance < old_distance:
                # Update the color of the n
                self.draw_updated_node(COLORS["FRONTIER"], n)
                # Update the fastest route of the n
                prevs[(n.r, n.c)] = cv
                queue[(n.r, n.c)] = new_distance
                dists[(n.r, n.c)] = new_distance

        return queue, dists, prevs

    def heuristic(self, prevs, frontier, found, neighbors, curr_dist, dest, cv) -> tuple:
        """
        Helper function for both A* solve
        :param prevs: dictionary containing all the nearest preceding nodes to a given node
        :param frontier: dictionary of all the nodes in the frontier and their f, g, and h values
        :param found: dictionary of all nodes and their distances
        :param neighbors: neighbors of the current vertex
        :param curr_dist: distance of the current vertex
        :param dest: destination node
        :param cv: current vertex
        :return: tuple of updated frontier, prevs
        """
        # Iterate over the max 4 neighbors of the current node and update the frontier and prevs dicts accordingly
        # # If a neighbor was already in frontier but the current route to it is faster update prevs and frontier
        # # If a neighbor is in found skip it
        for n in neighbors:
            if n in found or ((n.r, n.c) in frontier and 1 + curr_dist >= frontier[(n.r, n.c)][1]):
                continue

            # Get heuristic value and use it
            h = abs(dest[0] - n.r) + abs(dest[1] - n.c)
            frontier[(n.r, n.c)] = (1 + curr_dist + h, 1 + curr_dist, h)
            prevs[(n.r, n.c)] = cv

            # Draw the neighbor node
            self.draw_updated_node(COLORS["FRONTIER"], n)

        return frontier, prevs

    def get_adj_nodes(self, r, c) -> list:
        """
        Returns the adjacent nodes given a row and col index
        :param r: row index
        :param c: col index
        :return: list of adjacent nodes
        """
        adjacent = []
        possible_coors = [
            (r + 1, c), (r, c - 1), (r, c + 1), (r - 1, c)
        ]
        for row, col in possible_coors:
            if row in [-1, self.MAX_ROWS] or col in [-1, self.MAX_COLS]:
                continue
            n = self.nodes[row][col]
            if n.wall_status():
                continue
            adjacent.append(n)
        return adjacent

    def backtrack(self, d: dict, start_pos: tuple) -> None:
        """
        Draws out the route from the dest_pos to the start_pos using a dict
        :param d: dict of parent nodes for each node in the graph
        :param start_pos: tuple of starting position to backtrack from
        :return: None
        """
        coors = d[start_pos]
        while coors:
            node = self.nodes[coors[0]][coors[1]]
            time.sleep(DELAY)
            node.change_color(COLORS["PATH"])
            node.draw(screen)
            coors = d[coors]

    def backtrack_2(self, prevs: dict, succs: dict, inters: tuple) -> None:
        """
        Backtracks bidirectionally from an intersection point
        :param prevs: dictionary containing parent nodes of nodes in the graph
        :param succs: dictionary containing children nodes of nodes in the graph
        :param inters: intersection point
        :return: None
        """
        try:
            coors_s = prevs[inters]
            coors_d = succs[inters]
        except KeyError:
            return

        # Draw the first node
        n = self.nodes[inters[0]][inters[1]]
        self.draw_updated_node(COLORS["PATH"], n)

        # Iterate over all the coordinates
        while coors_s or coors_d:
            if coors_d:
                self.draw_updated_node(COLORS["PATH"], node=None, r=coors_d[0], c=coors_d[1])
                coors_d = succs[coors_d]

            if coors_s:
                self.draw_updated_node(COLORS["PATH"], node=None, r=coors_s[0], c=coors_s[1])
                coors_s = prevs[coors_s]

    def draw_updated_node(self, color: tuple, node=None, r=None, c=None) -> None:
        """
        Changes the color of a node and updates it
        :param color: tuple representing the color for the node to change to
        :param node: node to be modified
        :param r: row coordinates, in case a node is not provided
        :param c: col coordinates, in case a node is not provided
        :return: None
        """
        node = self.nodes[r][c] if not node else node
        time.sleep(DELAY)
        node.change_color(color)
        node.draw(screen)

    def save_maze(self) -> None:
        """
        Saves the current graph as a maze{n}.txt file in the mazes directory
        :return: None
        """
        path = PurePath.joinpath(Path.cwd(), 'mazes')
        num = int(input("\nWhat number maze would you like this to be (0-9): "))
        filename = PurePath.joinpath(path, f"maze{num}.txt")

        with open(filename, 'w') as f:
            for row in self.nodes:
                for node in row:
                    # If the node is a wall type a 1 in the maze file,
                    # 2 if it is a starting position, 3 if it's a dest position
                    # and 0 if its empty
                    if node.wall_status():
                        val = 1
                    elif node.start:
                        val = 2
                    elif node.dest:
                        val = 3
                    else:
                        val = 0
                    f.write(f"{val}")
                f.write("\n")

    def load_maze(self, num: int) -> None:
        """
        Loads a saved maze from the mazes folder
        :param num:
        :return: None
        """
        filename = PurePath.joinpath(Path.cwd(), f'mazes/maze{num}.txt')
        try:
            with open(filename, 'r') as f:
                self.clear_graph()
                for i, line in enumerate(f):
                    for j, dig in enumerate(line):
                        if dig == "\n":
                            continue
                        n = self.nodes[i][j]
                        dig = int(dig)
                        if dig == 1:
                            n.toggle_wall()
                        elif dig == 2:
                            self.start_pos = (i, j)
                            n.toggle_start()
                        elif dig == 3:
                            n.toggle_dest()
                            self.dest_pos = (i, j)
                        n.draw(screen)
        except FileNotFoundError:
            print(f"You don't have a maze{num}.txt file")


class Node(object):
    """
    The Node class will be used to handle the events of clicks, to generate walls, to signify if a node will be a
    destination, to store the least "costly" path
    """

    def __init__(self, r: int, c: int, x: float, y: float, width: float, height: float):
        """
        Creates a node object
        :param r: row index relative to Graph object it is contained in
        :param c: column index relative to Graph object it is contained in
        :param x: x coordinate of top left corner
        :param y: y coordinate of top left corner
        :param width: width of the Node
        :param height: height of the Node
        """
        self.r = r
        self.c = c
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.rect = pygame.rect.Rect(x, y, width, height)
        self.sq_color = COLORS["WHITE"]
        self.start = False
        self.dest = False
        self.is_wall = False

    def draw(self, s: pygame.surface) -> None:
        """
        Draws the nodes onto the window with the specific color or as a wall nodes if drag has been toggled
        :param s: pygame surface to draw on
        :return: None
        """
        if self.wall_status():
            self.sq_color = COLORS["BLACK"]

        if self.sq_color == COLORS["FRONTIER"]:
            # If the square is a "frontier" square draw a circle in that cell
            pygame.draw.circle(s, self.sq_color, (self.x + self.w // 2, self.y + self.h // 2), 8)
        else:
            pygame.draw.rect(s, self.sq_color, self.rect)
        pygame.display.update(self.rect)

    def change_color(self, color: tuple) -> None:
        """
        Changes the color of the square. To be used by Grid class
        :param color: 3 digit tuple representing RGB value
        :return: None
        """
        if not (self.start or self.dest):
            self.sq_color = color

    def wall_status(self):
        """
        Returns if the Node is a wall
        :return: True if it is a wall, False if otherwise
        """
        return self.is_wall

    def toggle_start(self) -> None:
        """
        Toggles the start instance variable
        :return: None
        """
        self.start = not self.start
        self.sq_color = COLORS["START"] if self.sq_color == COLORS["WHITE"] else COLORS["WHITE"]

    def toggle_dest(self) -> None:
        """
        Toggles the dest instance variable
        :return: None
        """
        self.dest = not self.dest
        self.sq_color = COLORS["START"] if self.sq_color == COLORS["WHITE"] else COLORS["WHITE"]

    def toggle_wall(self):
        self.is_wall = not self.is_wall
        self.sq_color = COLORS["BLACK"] if self.sq_color == COLORS["WHITE"] else COLORS["WHITE"]


def play() -> None:
    """
    Game loop for the pathfinder visualizer
    :return: None
    """
    instructions()
    # Initialize the grid
    g = Graph()
    # Game loop
    clock = pygame.time.Clock()
    while True:

        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # A keypress of X is also quit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                pygame.quit()
                sys.exit()
            # Let the graph handle the event
            g.handle_event(event)

        g.draw(screen)
        clock.tick(30)


def instructions() -> None:
    """
    Prints out the instructions
    :return: None
    """
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|              Welcome to VPath               |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|                 CONTROLS                    |")
    print("|     L-MOUSECLICK + DRAG = ENABLE A WALL     |")
    print("|     R-MOUSECLICK + DRAG = DISABLE A WALL    |")
    print("|     SPACE BAR = Run Dijkstra's algorithm    |")
    print("|      E = Run Double-Dijkstra's algorithm    |")
    print("|             A = Run A* algorithm            |")
    print("|           Q = Run Double A* algorithm       |")
    print("|     S = Enable/disable a start position     |")
    print("|     D = Enable/disable an end position      |")
    print("|          C = Clear board completely         |")
    print("|          V = Clear visualization            |")
    print("|          M = Save board as a maze file      |")
    print("|    0 to 9 - Load a maze file into board     |")
    print("|                   X = QUIT                  |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")


if __name__ == '__main__':
    play()
