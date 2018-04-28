import gtp_connection
from feature import Features_weight, Feature
import numpy as np

PASS = 'PASS'

class GtpConnectionGo5(gtp_connection.GtpConnection):
    def __init__(self, go_engine, board, outfile = 'gtp_log', debug_mode = False):
        gtp_connection.GtpConnection.__init__(self, go_engine, board, outfile, debug_mode)
        self.commands["prior_knowledge"] = self.prior_knowledge_cmd

    def prior_knowledge_cmd(self, args):
        # move = self.go_engine.get_move(self.board, color)
        # initialization
        all_board_features = Feature.find_all_features(self.board)
        probs = {}
        p_max = 0
        gamma_sum = 0.0
        moves = [PASS]
        knowledge = []

        # find all legal moves
        color = self.board.current_player
        for m in self.board.get_empty_points():
            if self.board.check_legal(m, color) and not self.board.is_eye(m, color):
                moves.append(m)

        # calculate probabilistic
        for m in moves:
            probs[m] = Feature.compute_move_gamma(Features_weight, \
                all_board_features[m])
            gamma_sum += probs[m]
        for m in moves:
            probs[m] = probs[m] / gamma_sum
            # find the largest probability 'p_max'
            if probs[m] > p_max:
                p_max = probs[m]

        # calculate the numner of sims and wins
        for m in moves:
            sim = 10 * probs[m] / p_max
            winrate = 0.5 + probs[m] / p_max * 0.5
            win = winrate * sim
            if m == PASS:
                m = None
            knowledge.append((self.board.point_to_string(m), winrate, sim, win))

        # sort by the (true, not rounded) winrate in descending order
        # break ties in alphanumeric order of the move
        knowledge.sort(key=lambda move:(-move[1], move[0]))
        output = []
        for move in knowledge:
            m, winrate, sim, win = move
            output.append(m + ' ' + str(int(round(win))) + ' ' + str(int(round(sim))))
        self.respond(' '.join(output))
