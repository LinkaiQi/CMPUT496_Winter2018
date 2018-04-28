import random
from board_util import GoBoardUtil

class GoBoardUtil_Go3(GoBoardUtil):
    def __init__(self):
        super().__init__()

    @staticmethod
    def playGame(board, color, **kwargs):
        komi = kwargs.pop('komi', 0)
        limit = kwargs.pop('limit', 1000)
        random_simulation = kwargs.pop('random_simulation',True)
        use_pattern = kwargs.pop('use_pattern',True)
        check_selfatari = kwargs.pop('check_selfatari',True)
        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)
        for _ in range(limit):
            if random_simulation:
                move = GoBoardUtil.generate_random_move(board,color,True)
            else:
                move = GoBoardUtil_Go3.generate_move_with_filter(board,use_pattern,check_selfatari)
            isLegalMove = board.move(move,color)
            assert isLegalMove
            if board.end_of_game():
                break
            color = GoBoardUtil.opponent(color)
        winner,_ = board.score(komi)
        return winner

    # Genmove color
    @staticmethod
    def generate_move_with_filter(board, use_pattern, check_selfatari):
        """
            Arguments
            ---------
            check_selfatari: filter selfatari moves?
                Note that even if True, this filter only applies to pattern moves
            use_pattern: Use pattern policy?
        """
        if board.last_move != None:
            # AtariCapture move
            atari_capture_move = GoBoardUtil_Go3.generate_atari_capture_move(board)
            if atari_capture_move:
                return atari_capture_move

            # AtariDefense move
            atari_defense_moves = GoBoardUtil_Go3.generate_atari_defense_moves(board)
            if len(atari_defense_moves) > 0:
                return random.choice(atari_defense_moves)

        if use_pattern:
            moves = GoBoardUtil.generate_pattern_moves(board)
            move = GoBoardUtil.filter_moves_and_generate(board, moves,
                                                         check_selfatari)
            if move:
                return move
        return GoBoardUtil.generate_random_move(board, board.current_player,True)

    # Policy moves
    @staticmethod
    def generate_all_policy_moves(board, pattern, check_selfatari):
        """
            generate a list of policy moves on board for board.current_player.
            Use in UI only. For playing, use generate_move_with_filter
            which is more efficient
        """
        if board.last_move != None:
            # AtariCapture
            atari_capture_move = GoBoardUtil_Go3.generate_atari_capture_move(board)
            if atari_capture_move:
                return [atari_capture_move], "AtariCapture"

            # AtariDefense
            atari_defense_moves = GoBoardUtil_Go3.generate_atari_defense_moves(board)
            if len(atari_defense_moves) > 0:
                return atari_defense_moves, "AtariDefense"

        # Pattern
        if pattern:
            pattern_moves = []
            pattern_moves = GoBoardUtil.generate_pattern_moves(board)
            pattern_moves = GoBoardUtil.filter_moves(board, pattern_moves, check_selfatari)
            if len(pattern_moves) > 0:
                return pattern_moves, "Pattern"

        # Random
        return GoBoardUtil.generate_random_moves(board,True), "Random"

    # PART 1: ATARI CAPTURE
    @staticmethod
    def generate_atari_capture_move(board):
        color = GoBoardUtil.opponent(board.current_player)
        move = board._single_liberty(board.last_move, color)
        if move and not GoBoardUtil.selfatari_filter(board, move, board.current_player):
            return move
        return None

    # PART 2: ATARI DEFENSE
    @staticmethod
    def generate_atari_defense_moves(board):
        ad_moves = []
        neighbors = board._neighbors(board.last_move)
        for n in neighbors:
            if board.board[n] == board.current_player \
            and board._liberty(n, board.current_player) == 1:
                # 1. run away move
                ad_moves.append(board._single_liberty(n, board.current_player))
                # 2. capture opponent adjacent stones
                opp_stones = GoBoardUtil_Go3._get_opponent_adjacent_stones(board, n)
                for opp in opp_stones:
                    if board._liberty(opp, GoBoardUtil.opponent(board.current_player)) == 1:
                        ad_moves.append(board._single_liberty(opp, GoBoardUtil.opponent(board.current_player)))
        # remove duplicate moves and run move filter
        good_moves = []
        for move in set(ad_moves):
            if not GoBoardUtil.selfatari_filter(board, move, board.current_player):
                good_moves.append(move)
        good_moves.sort()
        return good_moves


    @staticmethod
    def _get_opponent_adjacent_stones(board, point):
        """
        Helper function
        Given a block, find all adjacent opponent stones
        """
        color = board.board[point]
        opp_stones = []

        group_points = [point]
        met_points = [point]
        while group_points:
            p = group_points.pop()
            met_points.append(p)
            neighbors = board._neighbors(p)
            for n in neighbors:
                if n not in met_points:
                    if board.board[n] == color:
                        group_points.append(n)
                    elif board.board[n] == GoBoardUtil.opponent(color):
                        opp_stones.append(n)
                    met_points.append(n)

        return opp_stones
