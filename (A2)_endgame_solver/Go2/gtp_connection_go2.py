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

class GtpConnectionGo2(gtp_connection.GtpConnection):

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
        self.commands["go_safe"] = self.safety_cmd
        self.argmap["go_safe"] = (1, 'Usage: go_safe {w,b}')

        # timelimit seconds cmd
        self.commands["timelimit"] = self.timelimit_cmd
        self.argmap["timelimit"] = (1, 'Usage: timelimit seconds')
        # solve cmd
        self.commands["solve"] = self.solve_cmd

    def timelimit_cmd(self, args):
        """
        Set the maximum time to use for following 'genmove' or 'solve' cmd

        Arguments
        ---------
        args[0] : int range(1<= seconds <= 100)
            timelimit seconds
        """
        self.go_engine.timelimit = int(args[0])
        self.respond()

    # convert 'point' to 'board_move'
    def _point_to_move(self, point):
        if point == 'pass':
            return 'pass'
        elif point:
            coord = self.board._point_to_coord(point)
            return GoBoardUtil.format_point(coord)
        return None

    def solve_cmd(self, args):
        winner, point = self.go_engine.solve(self.board, self.board.current_player)
        board_move = self._point_to_move(point)
        # show result in stdout
        if board_move:
            self.respond('{} {}'.format(winner, board_move))
        else:
            self.respond(winner)

    def genmove_cmd(self, args):
        board_color = args[0].lower()
        color = GoBoardUtil.color_to_int(board_color)
        # Try to use the solver to solve the game perfectly
        winner, point = self.go_engine.solve(self.board, color)
        if winner == 'unknown' or winner != board_color:
            # If the solver cannot solve the game in 'timelimit' seconds, or toPlay is losing
            # then play the same move as the original Go2
            super().genmove_cmd(args)
        else:
            if point == None or point == 'pass':
                self.respond("pass")
                return
            self.board.move(point, color)
            self.debug_msg("Move: {}\nBoard: \n{}\n".format(point, str(self.board.get_twoD_board())))
            board_move = self._point_to_move(point)
            self.respond(board_move)

    # def genmove_cmd(self, args):
    #     super().genmove_cmd(args)


    def safety_cmd(self, args):
        try:
            color= GoBoardUtil.color_to_int(args[0].lower())
            safety_list = self.board.find_safety(color)
            safety_points = []
            for point in safety_list:
                x,y = self.board._point_to_coord(point)
                safety_points.append(GoBoardUtil.format_point((x,y)))
            self.respond(safety_points)
        except Exception as e:
            self.respond('Error: {}'.format(str(e)))
