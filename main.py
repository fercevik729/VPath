#
# Pathfinder Visualization
# by Furkan Ercevik
# Started 4 November 2021
#
import time
import pygame
import sys
from queue import PriorityQueue

# CONSTANTS + SETUP
pygame.init()
LOGO = pygame.image.load("assets/magnifying.png")
pygame.display.set_icon(LOGO)
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("Pathfinder Visualizer")
COLORS = {"START": (10, 17, 114), "WHITE": (255, 255, 255), "BLACK": (0, 0, 0), "RED": (255, 0, 0),
          "FOUND": (72, 170, 173), "FRONTIER": (1, 96, 100), "PATH": (130, 238, 253)}
DELAYS = {"A-STAR": 0.008, "DIJKSTRA": 0.002}
# Global variables
drag = False
clear_drag = False
reached = False


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

        x = 0
        y = 5
        for n in range(41):
            row = []
            for c in range(41):
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

                n.force_color_change(COLORS["WHITE"])

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
        # Make the node a start or destination node
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                self.clear_graph()
            if event.key == pygame.K_SPACE:
                self.dijkstra_solve()
            if event.key == pygame.K_a:
                self.a_star_solve()
            if event.key == pygame.K_v:
                self.clear_visualization()
            if event.key == pygame.K_s:
                x, y = pygame.mouse.get_pos()
                if x in range(0, 1025) and y in range(0,1025):
                    r = y // 25
                    c = x // 25
                    if not self.start_pos or self.start_pos == (r,c):
                        node = self.nodes[r][c]
                        node.toggle_start()
                        self.start_pos = (r, c) if node.start else None
                        node.force_color_change(COLORS["START"] if node.sq_color == COLORS["WHITE"] else COLORS["WHITE"])
            if event.key == pygame.K_d:
                x, y = pygame.mouse.get_pos()
                if x in range(0, 1025) and y in range(0, 1025):
                    r = y // 25
                    c = x // 25
                    if not self.dest_pos or self.dest_pos == (r, c):
                        node = self.nodes[r][c]
                        node.toggle_dest()
                        node.force_color_change(COLORS["START"] if node.sq_color == COLORS["WHITE"] else COLORS["WHITE"])
                        self.dest_pos = (r, c) if node.dest else None

    def draw(self, s):
        """
        Draws the grid
        :param s:
        :return:
        """
        for row in self.nodes:
            for n in row:
                n.draw(s)

    def dijkstra_solve(self) -> bool:
        """
        Creates two lists: one of the distances and of the preceding nodes for each respective node
        and backtracks to find the shortest path
        :return: True if a path could be found, otherwise False
        """
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
        # Start the priority queue
        pq = PriorityQueue()
        pq.put((0, self.start_pos))

        # While the priority queue is not empty
        while not pq.empty():
            # Get the vertex with the lowest cost
            dist, current_vertex = pq.get()
            node = self.nodes[current_vertex[0]][current_vertex[1]]
            node.change_color(COLORS["FOUND"])
            node.draw(screen)
            # Check if it is a wall and if so skip over it
            if self.nodes[current_vertex[0]][current_vertex[1]].wall_status():
                continue
            # Get the neighbors of the current node and iterate over them
            neighbors = self.get_adj_nodes(current_vertex[0], current_vertex[1])
            for neighbor in neighbors:
                old_distance = dists[(neighbor.r, neighbor.c)]
                new_distance = dists[current_vertex] + 1
                # If the new distance is smaller than the original cost put the neighbor in the priority queue with
                # the new distance cost
                if new_distance < old_distance:
                    # Update the color of the neighbor
                    time.sleep(DELAYS["DIJKSTRA"])
                    neighbor.change_color(COLORS["FRONTIER"])
                    neighbor.draw(screen)
                    # Update the fastest route of the neighbor
                    prevs[(neighbor.r, neighbor.c)] = current_vertex

                    pq.put((new_distance, (neighbor.r, neighbor.c)))
                    dists[(neighbor.r, neighbor.c)] = new_distance

        # Backtrack from destination node
        self.backtrack(prevs)

    def get_adj_nodes(self, r, c) -> list:
        """
        Returns the adjacent nodes given a row and col index
        :param r: row index
        :param c: col index
        :return: list of adjacent nodes
        """
        adjacent = []
        possible_coors = [
            (r+1, c), (r, c-1), (r, c+1), (r-1, c)
        ]
        for row, col in possible_coors:
            if row in [-1, len(self.nodes)] or col in [-1, len(self.nodes)]:
                continue
            n = self.nodes[row][col]
            if n.wall_status():
                continue
            adjacent.append(n)
        return adjacent

    def a_star_solve(self):
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
            current_vertex = min(frontier, key=lambda t: frontier[t][0])
            fgh = frontier[current_vertex]
            # The raw distance is the second value in the fgh tuple which is g
            dist = fgh[1]
            del frontier[current_vertex]

            # If the current vertex is the destination break out of the loop
            if current_vertex == self.dest_pos:
                break
            # Otherwise color the current node and add it to the found dict
            node = self.nodes[current_vertex[0]][current_vertex[1]]
            found[node] = dist
            node.change_color(COLORS["FOUND"])
            node.draw(screen)

            # Iterate over the max 4 neighbors of the current node and update the frontier and prevs dicts accordingly
            # # If a neighbor was already in frontier but the current route to it is faster update prevs and frontier
            # # If a neighbor is in found skip it
            neighbors = self.get_adj_nodes(current_vertex[0], current_vertex[1])
            for n in neighbors:
                if n in found or ((n.r, n.c) in frontier and 1 + dist >= frontier[(n.r, n.c)][1]):
                    continue

                # Get heuristic value and use it
                h = abs(self.dest_pos[0] - n.r) + abs(self.dest_pos[1] - n.c)
                frontier[(n.r, n.c)] = (1 + dist + h, 1 + dist, h)
                prevs[(n.r, n.c)] = current_vertex

                # Draw the neighbor node
                time.sleep(DELAYS["A-STAR"])
                n.change_color(COLORS["FRONTIER"])
                n.draw(screen)

        # Initiate backtracking
        self.backtrack(prevs)

    def backtrack(self, prevs: dict) -> None:
        """
        Draws out the route from the dest_pos to the start_pos using a dict
        :param prevs: dict of parent nodes for each node in the graph
        :return: None
        """
        coors = prevs[self.dest_pos]
        while coors:
            node = self.nodes[coors[0]][coors[1]]
            node.draw(screen)
            time.sleep(.04)
            node.change_color(COLORS["PATH"])
            node.draw(screen)
            coors = prevs[coors]


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

    def handle_event(self, event: pygame.event) -> None:
        """
        Handles the mouseclick event specifically for a node object
        :param event: a pygame event
        :return: None
        """
        global drag
        global clear_drag
        # Check if there is a mouse click directly on one of the nodes
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                # If the mouse button was the left button enable wall status for the selected node
                drag = True
            elif event.button == pygame.BUTTON_RIGHT:
                # If the mouse button was the right button disable wall status for the selected node
                clear_drag = True
        # Check if the mouse is no longer clicked at which point drag is no longer true
        if event.type == pygame.MOUSEBUTTONUP:
            drag = False
            clear_drag = False

    def draw(self, s: pygame.surface) -> None:
        """
        Draws the nodes onto the window with the specific color or as a wall nodes if drag has been toggled
        :param s: pygame surface to draw on
        :return: None
        """
        if drag and self.rect.collidepoint(pygame.mouse.get_pos()) and not (self.start or self.dest):
            # If the drag variable is enabled, enable the wall status of this nodes
            self.is_wall = True
            self.sq_color = COLORS["BLACK"]

        if clear_drag and self.rect.collidepoint(pygame.mouse.get_pos()) and not (self.start or self.dest):
            # If the clear drag variable is enabled, disable the wall status of this nodes
            self.is_wall = False
            self.sq_color = COLORS["WHITE"]

        if self.sq_color == COLORS["FRONTIER"]:
            # If the square is a "frontier" square draw a circle in that cell
            pygame.draw.circle(s, self.sq_color, (self.x + self.w//2, self.y + self.h//2), 8)
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

    def force_color_change(self, color: tuple) -> None:
        """
        Changes the color of a Node object regardless of if it is the destination or starting Node
        :param color: 3 digit tuple representing RGB value
        :return: None
        """
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

    def toggle_dest(self) -> None:
        """
        Toggles the dest instance variable
        :return: None
        """
        self.dest = not self.dest

    def toggle_wall(self):
        self.is_wall = not self.is_wall


def play() -> None:
    """
    Game loop for the pathfinder visualizer
    :return: None
    """
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

            # Let the nodes in the graph handle the event
            for row in g.nodes:
                for node in row:
                    node.handle_event(event)
        g.draw(screen)
        clock.tick(30)


def instructions() -> None:
    """
    Prints out the instructions
    :return: None
    """
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|    Welcome to my Pathfinder Visualizer!!    |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|                 CONTROLS                    |")
    print("|     L-MOUSECLICK + DRAG = ENABLE A WALL     |")
    print("|     R-MOUSECLICK + DRAG = DISABLE A WALL    |")
    print("|     SPACEBAR = Run Dijkstra's algorithm     |")
    print("|           A = Run A-star algorithm          |")
    print("|     S = Enable/disable a start position     |")
    print("|     D = Enable/disable an end position      |")
    print("|          C = Clear board completely         |")
    print("|          V = Clear visualization            |")
    print("|                   X = QUIT                  |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")


if __name__ == '__main__':
    instructions()
    play()
