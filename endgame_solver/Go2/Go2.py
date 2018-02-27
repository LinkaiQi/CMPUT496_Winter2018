#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
# Set the path to your python3 above

# Set up relative path for util; sys.path[0] is directory of current program
import os, sys, signal
utilpath = sys.path[0] + "/../util/"
sys.path.append(utilpath)

from gtp_connection_go2 import GtpConnectionGo2
from board_util import GoBoardUtil
from simple_board import SimpleGoBoard

# Register an handler for the timeout
def handler(signum, frame):
    raise Exception("end of time")

class Go2():
    def __init__(self):
        """
        Player that selects moves randomly from the set of legal moves.
        With the fill-eye filter.

        Parameters
        ----------
        name : str
            name of the player (used by the GTP interface).
        version : float
            version number (used by the GTP interface).
        """
        self.name = "Go2"
        self.version = 0.1
        self.timelimit = 1
        self.depth_limit = 14

    def get_move(self, board, color):
        return GoBoardUtil.generate_random_move(board,color,True)

    def solve(self, board, to_play):
        state = board.copy()
        # to_play = state.current_player
        # Initialize proof tree and run negamax search starts with current player
        proof_tree = []
        # Set timer
        signal.signal(signal.SIGALRM, handler)

        signal.alarm(self.timelimit)
        try:
            result = self.negamaxBoolean(state, self.depth_limit, proof_tree)
        except Exception as e:
            # print(e)
            result = None
        signal.alarm(0)

        proof_tree.reverse()
        # Convert result to current player
        if result == None:
            return 'unknown', None
        elif result:
            if proof_tree[0] == None:
                proof_tree[0] = 'pass'
            return GoBoardUtil.int_to_color(to_play), proof_tree[0]
        else:
            return GoBoardUtil.int_to_color(GoBoardUtil.opponent(to_play)), None
        # elif result:
        #     # convert 'point' to 'move'
        #     coord = board._point_to_coord(proof_tree[0])
        #     first_move = GoBoardUtil.format_point(coord)
        #     return GoBoardUtil.int_to_color(to_play), first_move
        # else:
        #     return GoBoardUtil.int_to_color(GoBoardUtil.opponent(to_play)), None

    def get_legal_moves(self, state):
        legal_moves = []
        for m in state.get_empty_points():
            if state.check_legal(m, state.current_player) \
            and not state.is_eye(m, state.current_player):
                legal_moves.append(m)
        if len(legal_moves) == 0:
            legal_moves = [None]
        # print(state.current_player, legal_moves)
        return legal_moves

    def negamaxBoolean(self, state, depth, proof_tree):
        if depth == 0 or state.end_of_game():
            winner, score = state.score(self.komi)
            # print(winner)
            if winner == state.current_player:
                return True
            else:
                return False
        for m in self.get_legal_moves(state):
            # debug
            # if m:
            #     coord = state._point_to_coord(m)
            #     print(GoBoardUtil.format_point(coord))
            # else:
            #     print('pass')
            state.move(m, state.current_player)
            success = not self.negamaxBoolean(state, depth-1, proof_tree)
            state.undo_move()
            if success:
                proof_tree.append(m)
                return True
        return False



def run():
    """
    start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnectionGo2(Go2(), board)
    con.start_connection()

if __name__=='__main__':
    run()
