import gtp_connection
from board_util_go3 import GoBoardUtil_Go3

class GtpConnectionGo3(gtp_connection.GtpConnection):

    def policy_moves_cmd(self, args):
        """
        Return list of policy moves for the current_player of the board
        """
        policy_moves, type_of_move = GoBoardUtil_Go3.generate_all_policy_moves(self.board,
                                                        self.go_engine.use_pattern,
                                                        self.go_engine.check_selfatari)
        if len(policy_moves) == 0:
            self.respond("Pass")
        else:
            response = type_of_move + " " + GoBoardUtil_Go3.sorted_point_string(policy_moves, self.board.NS)
            self.respond(response)
