#
# Pathfinder Visualizer Visualization
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
COLORS = {"NAVY": (10, 17, 114), "WHITE": (255, 255, 255), "BLACK": (0, 0, 0), "RED": (255, 0, 0),
          "FOUND": (72, 170, 173), "FRONTIER": (1, 96, 100), "PATH": (130, 238, 253)}

# Drag variables for walls
drag = False
clear_drag = False


# The Graph class will be used to organize all the Node objects in one place and simulate the visualization process
class Graph(object):

    # Initialize the squares
    def __init__(self, dest_pos: tuple, start_pos=(5, 5)):
        self.nodes = []
        self.visited_nodes = []
        self.start_pos = start_pos
        self.dest_pos = dest_pos

        x = 0
        y = 5
        for n in range(41):
            row = []
            for c in range(41):
                if (n, c) == start_pos:
                    row.append((Node(n, c, x, y, 20, 20, start=True)))
                elif (n, c) == dest_pos:
                    row.append((Node(n, c, x, y, 20, 20, dest=True)))
                else:
                    row.append((Node(n, c, x, y, 20, 20)))

                x += 25
            self.nodes.append(row)
            x = 0
            y += 25

    # Draw the grid
    def draw(self, s):
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

        found = False
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
            neighbors = self.get_adj_tiles(current_vertex[0], current_vertex[1])
            for neighbor in neighbors:
                # If the neighbor is a wall skip over it
                if neighbor.wall_status():
                    continue

                if (neighbor.r, neighbor.c) == self.dest_pos:
                    found = True
                old_distance = dists[(neighbor.r, neighbor.c)]
                new_distance = dists[current_vertex] + 1
                # If the new distance is smaller than the original cost put the neighbor in the priority queue with
                # the new distance cost
                if new_distance < old_distance:
                    # Update the color of the neighbor
                    time.sleep(.005)
                    neighbor.change_color(COLORS["FRONTIER"])
                    neighbor.draw(screen)
                    # Update the fastest route of the neighbor
                    prevs[(neighbor.r, neighbor.c)] = current_vertex

                    pq.put((new_distance, (neighbor.r, neighbor.c)))
                    dists[(neighbor.r, neighbor.c)] = new_distance

        # Backtrack from destination node
        coors = prevs[self.dest_pos]
        while coors:
            node = self.nodes[coors[0]][coors[1]]
            node.draw(screen)
            time.sleep(.05)
            node.change_color(COLORS["PATH"])
            node.draw(screen)
            coors = prevs[coors]

        return found

    def get_adj_tiles(self, r, c) -> list:
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
            adjacent.append(self.nodes[row][col])
        return adjacent


class Node(object):
    """
    The Node class will be used to handle the events of clicks, to generate walls, to signify if a node will be a
    destination, to store the least "costly" path
    """
    def __init__(self, r: int, c: int, x: float, y: float, width: float, height: float, start=False, dest=False):
        self.r = r
        self.c = c
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.rect = pygame.rect.Rect(x, y, width, height)
        self.dest = dest
        self.start = start
        if start or dest:
            self.sq_color = COLORS["NAVY"]
        else:
            self.sq_color = COLORS["WHITE"]
        self.is_wall = False

    def handle_event(self, event: pygame.event) -> None:
        """
        Handles the mouseclick event specifically for a tile object
        :param event: a pygame event
        :return: None
        """
        global drag
        global clear_drag
        # Check if there is a mouse click directly on one of the nodes
        if event.type == pygame.MOUSEBUTTONDOWN and not (self.start or self.dest) and self.rect.collidepoint(pygame.mouse.get_pos()):
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
        Draws the tile onto the window with the specific color or as a wall tile if drag has been toggled
        :param s: pygame surface to draw on
        :return: None
        """
        if drag and self.rect.collidepoint(pygame.mouse.get_pos()):
            # If the drag variable is enabled, enable the wall status of this tile
            self.is_wall = True
            self.sq_color = COLORS["BLACK"]

        if clear_drag and self.rect.collidepoint(pygame.mouse.get_pos()):
            # If the clear drag variable is enabled, disable the wall status of this tile
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

    def wall_status(self):
        return self.is_wall


def play():
    dest_row = 20
    dest_col = 20

    # Initialize the grid
    g = Graph((dest_row, dest_col))

    # Game loop
    clock = pygame.time.Clock()
    # Sentinel variable
    run = True
    reached = False
    while run:

        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    reached = g.dijkstra_solve()
                    run = False
            for row in g.nodes:
                for node in row:
                    node.handle_event(event)
        g.draw(screen)
        clock.tick(30)

        # Wait 10 seconds after the destination has been found
        if not run:
            time.sleep(7)

    if reached:
        print("A minimum path was found")
    else:
        print("A minimum path was NOT found")


if __name__ == '__main__':
    play()
