"""
Module for playing games of Go using GoTextProtocol

This code is based off of the gtp module in the Deep-Go project
by Isaac Henrion and Aamos Storkey at the University of Edinburgh.
"""
import traceback
import sys
import os
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, FLOODFILL
import gtp_connection
import numpy as np
import re

class GtpConnectionGo1(gtp_connection.GtpConnection):

    def __init__(self, go_engine, board, outfile = 'gtp_log', debug_mode = False):
        """
        GTP connection of Go1

        Parameters
        ----------
        go_engine : GoPlayer
            a program that is capable of playing go by reading GTP commands
        komi : float
            komi used for the current game
        board: GoBoard
            SIZExSIZE array representing the current board state
        """
        gtp_connection.GtpConnection.__init__(self, go_engine, board, outfile, debug_mode)
        self.commands["hello"] = self.hello_cmd
        self.commands["score"] = self.score_cmd

    def hello_cmd(self, args):
        """ Dummy Hello Command """
        self.respond("Hello! " + self.go_engine.name)

    def score_cmd(self, args):
        # self.respond('\n' + str(self.board.get_twoD_board()))
        b = self.board.copy()
        empty_points = self._get_empty_points(b)
        # self._calcuate_territory(b, empty_points)

        b_score, w_score = np.sum([self._calcuate_territory(b, empty_points),
            self._calcuate_stone(b)], axis=0)
        w_score = w_score + self.komi

        # format and send score result to the stdout
        result = "0"
        if b_score > w_score:
            result = "B+" + str(b_score - w_score)
        elif b_score < w_score:
            result = "W+" + str(w_score - b_score)
        self.respond(result)

    def _calcuate_stone(self, board):
        black, white = (0, 0)
        for y in range(1, board.size+1, 1):
            for x in range(1, board.size+1, 1):
                point = board._coord_to_point(x,y)
                if board.get_color(point) == BLACK:
                    black += 1
                elif board.get_color(point) == WHITE:
                    white += 1
        return (black, white)

    def _get_empty_points(self, board):
        points = []
        for y in range(1, board.size+1, 1):
            for x in range(1, board.size+1, 1):
                point = board._coord_to_point(x,y)
                if board.get_color(point) == EMPTY:
                    points.append(point)
        return points;

    def _calcuate_territory(self, board, empty_points):
        black_territory = 0
        white_territory = 0
        while empty_points:
            # Find Connected Component
            # start at an empty point, find the connected set of empty point from the board
            start_point = empty_points[0]
            # Initialize the territory (connect set of empty points) as unknown
            connected_to = []
            connected_empty_points = []
            visited_points = []
            pointstack = [start_point]
            while pointstack:
                p = pointstack.pop()
                visited_points.append(p)
                neighbors = board._neighbors(p)
                for n in neighbors:
                    if n in visited_points:
                        continue
                    color = board.board[n]
                    if color == EMPTY:
                        pointstack.append(n)
                        visited_points.append(n)
                    if color in [BLACK, WHITE]:
                        connected_to.append(color)
                connected_empty_points.append(p)

            # Determine Territory
            # after get the connected set of empty point, find whether its Black, White or neutral
            # if all empty point in the set can only can connect to one color
            if len(set(connected_to)) == 1:
                # only connected to black stone
                if connected_to[0] == BLACK:
                    black_territory += len(connected_empty_points)
                # only connected to white stone
                elif connected_to[0] == WHITE:
                    white_territory += len(connected_empty_points)

            # Remove the calcuated empty points from the "empty_points" list
            for point in connected_empty_points:
                empty_points.remove(point)

        return (black_territory, white_territory)
