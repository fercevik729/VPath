#
# Pathfinder Visualizer Visualization
# by Furkan Ercevik
# Started 4 November 2021
#
import time

import pygame
import sys
from queue import PriorityQueue

# CONSTANTS
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("Pathfinder Visualizer")
COLORS = {"ORANGE": (255, 165, 0), "WHITE": (255, 255, 255), "BLACK": (0, 0, 0), "RED": (255, 0, 0)}


# The Graph class will be used to organize all the Node objects in one place and simulate the visualization process
class Graph(object):

    # Initialize the squares
    def __init__(self, dest_pos: tuple, start_pos=(0, 0)):
        self.nodes = []
        self.visited_nodes = []
        self.start_pos = start_pos
        self.dest_pos = dest_pos

        start_x = 0
        start_y = 5
        for n in range(41):
            row = []
            for c in range(41):
                if (n, c) == start_pos:
                    row.append((Node(n, c, start_x, start_y, 20, 20, start=True)))
                elif (n, c) == dest_pos:
                    row.append((Node(n, c, start_x, start_y, 20, 20, dest=True)))
                else:
                    row.append((Node(n, c, start_x, start_y, 20, 20)))

                start_x += 25
            self.nodes.append(row)
            start_x = 0
            start_y += 25

    # Draw the grid
    def draw(self, s):
        for row in self.nodes:
            for n in row:
                n.draw(s)

    # Creates two lists: one of the distances and of the preceding nodes for each respective node
    # and backtracks to find the shortest path
    def dijkstra_solve(self):
        # # GOALS
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

        # While the priority queue is not empty
        while not pq.empty():
            # Get the vertex with the lowest cost
            dist, current_vertex = pq.get()
            # Check if it is a wall and if so skip over it
            if self.nodes[current_vertex[0]][current_vertex[1]].wall_status():
                continue
            # Get the neighbors of the current node and iterate over them
            for neighbor in self.get_adj_tiles(current_vertex[0], current_vertex[1]):
                # If the neighbor is a wall skip over it
                if neighbor.wall_status():
                    continue

                old_distance = dists[(neighbor.r, neighbor.c)]
                new_distance = dists[current_vertex] + 1
                # If the new distance is smaller than the original cost put the neighbor in the priority queue with
                # the new distance cost
                if new_distance < old_distance:
                    # Update the color of the neighbor
                    time.sleep(.001)
                    if not(neighbor.start or neighbor.dest):
                        neighbor.change_color((0, 255, 0))
                    neighbor.draw(screen)
                    # Update the fastest route of the neighbor
                    prevs[(neighbor.r, neighbor.c)] = current_vertex

                    pq.put((new_distance, (neighbor.r, neighbor.c)))
                    dists[(neighbor.r, neighbor.c)] = new_distance

        # Backtrack from destination node
        coors = prevs[self.dest_pos]
        while coors:
            node = self.nodes[coors[0]][coors[1]]
            node.change_color(COLORS["RED"])
            coors = prevs[coors]
        #return self.nodes[self.dest_pos[0]][self.dest_pos[1]].fastest_route

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


# The Node class will be used to handle the events of clicks, to generate walls, to signify if a node will be a
# destination, to store the least "costly" path
class Node(object):

    def __init__(self, r: int, c: int, x: float, y: float, width: float, height: float, start=False, dest=False):
        self.r = r
        self.c = c
        self.rect = pygame.rect.Rect(x, y, width, height)
        self.dest = dest
        self.start = start
        if start or dest:
            self.sq_color = COLORS["ORANGE"]
        else:
            self.sq_color = COLORS["WHITE"]
        self.is_wall = False

    def handle_event(self, event: pygame.event) -> None:
        """
        Handles the mouseclick event specifically for a tile object
        :param event: a pygame event
        :return: None
        """
        # Check if there is a mouse click directly on one of the nodes
        if event.type == pygame.MOUSEBUTTONDOWN and not self.start:
            # If it's in the grid and not the start or dest position
            if self.rect.collidepoint(event.pos):
                self.is_wall = True
                self.sq_color = COLORS["BLACK"]

    def draw(self, s: pygame.surface) -> None:
        """
        Draws the tile onto the window with the specific color
        :param s: pygame surface to draw on
        :return: None
        """
        pygame.draw.rect(s, self.sq_color, self.rect)
        pygame.display.update(self.rect)

    def change_color(self, color: tuple) -> None:
        """
        Changes the color of the square. To be used by Grid class
        :param color: 3 digit tuple representing RGB value
        :return: None
        """
        self.sq_color = color

    def wall_status(self):
        return self.is_wall

    def __repr__(self):
        return f"Row: {self.r}, Col: {self.c}"


def play():
    dest_row = 20
    dest_col = 20

    # Initialize the grid
    g = Graph((dest_row, dest_col))

    # Game loop
    clock = pygame.time.Clock()
    while True:

        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print(g.dijkstra_solve())
            for row in g.nodes:
                for node in row:
                    node.handle_event(event)
        g.draw(screen)

        clock.tick(30)


if __name__ == '__main__':
    play()
