#
# Pathfinder Visualizer Visualization
# by Furkan Ercevik
# Started 4 November 2021
#
import pygame
import sys
from queue import PriorityQueue

# CONSTANTS
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("Pathfinder Visualizer")
COLORS = {"ORANGE": (255, 165, 0), "WHITE": (255, 255, 255), "BLACK": (0, 0, 0)}


# The Graph class will be used to organize all the tile objects in one place and simulate the visualization process
class Graph(object):

    # Initialize the squares
    def __init(self, dest_pos, start_pos=(0, 0)):
        self.nodes = []
        self.visited_nodes = set()
        self.start_pos = start_pos
        self.dest_pos = dest_pos

    # Draw the grid
    def draw(self):
        for n in self.nodes:
            n.draw()

    # Finds the shortest path to the destination using Dijkstra's algorithm
    def dijkstra_solve(self):
        # Start solving from the start_position
        # Once the destination is reached, map the shortest route in red color
        pass

    def get_adj_tiles(self, r, c) -> list:
        """
        Returns the adjacent nodes given a row and col index
        :param r: row index
        :param c: col index
        :return: list of adjacent nodes
        """
        adjacent = []
        for row in range(len(self.nodes)):
            for col in range(len(self.nodes[row])):
                # If the tile isn't a wall
                if not self.nodes[row][col].wall_status() and (abs(row - r) <= 1 or abs(col - c) <= 1):
                    adjacent.append(self.nodes[row][col])
        adjacent.remove(self.nodes[r][c])
        return adjacent


# The Node class will be used to handle the events of clicks, to generate walls, to signify if a node will be a
# destination, to store the least "costly" path
class Node(object):

    def __init__(self, r: int, c: int, x: float, y: float, width: float, height: float, start=False, dest=False):
        self.r = r
        self.c = c
        self.rect = pygame.rect.Rect(x, y, width, height)
        self.sq_color = COLORS["WHITE"] if not (start or dest) else COLORS["ORANGE"]
        # If the square is a destination square set the found attr to False initially, otherwise set it to None
        self.found = False if dest else None
        self.is_wall = False
        self.fastest_route = set()
        self.cost = float("inf") if not start else 0

    def handle_event(self, event: pygame.event) -> None:
        """
        Handles the mouseclick event specifically for a tile object
        :param event: a pygame event
        :return: None
        """
        # Check if there is a mouse click directly on one of the nodes
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If it's in the grid
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

    def update_cost(self):
        pass


def play():
    dest_row = int(input("Type a row index between n and m inclusive for the destination's row index: "))
    dest_col = int(input("Type a row index between n and m inclusive for the destination's column index: "))

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

        clock.tick(30)


if __name__ == '__main__':
    play()
