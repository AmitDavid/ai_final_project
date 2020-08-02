import numpy as np

from util import manhattan_distance


class Board:
    """
    A Board describes the current state of the game board. It's separate from
    the game engine to allow the Input objects to check if their moves are valid,
    etc... without the help of the game engine.

    The Board stores:
    - board_w/board_h: the width and height of the playing area
    - state: a matrix (2D list) of tuples (int, int) where t[0]- the number of
    the current entry (0 = empty), t[1]- the index of the color in self colors
    of the current entry
    - colors: the number of the colors (the max value(-1) available for colors)
    - paths - dictionary where the keys are the colors and the values are
    lists of lists of paths in the key color
    { RED : [[(i1,j1), (i2,j2)...], [(i3,j3), (i4, j4)...]...]}
    """

    def __init__(self, num_of_colors, paths, b_matrix):
        self.board_w = len(b_matrix[0])
        self.board_h = len(b_matrix)
        self.num_of_colors = num_of_colors - 1
        self.state = b_matrix
        self.paths = paths

    def add_move(self, move):
        """
        Try to add <player>'s <move>.

        If the move is legal, the board state is updated; if it's not legal, a
        ValueError is raised.

        Returns the number of tiles placed on the board.
        """
        if not self.check_move_valid(player, move):
            raise ValueError("Move is not allowed")

        piece = move.piece
        self.pieces[player, move.piece_index] = False  # mark piece as used

        # Update internal state for each tile
        for (xi, yi) in move.orientation:
            (x, y) = (xi + move.x, yi + move.y)
            self.state[y, x] = player

            # Nobody can play on this square
            for p in range(self.num_players):
                self._legal[p][y][x] = False

            # This player can't play next to this square
            if x > 0:
                self._legal[player, y, x - 1] = False
            if x < self.board_w - 1:
                self._legal[player, y, x + 1] = False
            if y > 0:
                self._legal[player, y - 1, x] = False
            if y < self.board_h - 1:
                self._legal[player, y + 1, x] = False

            # The diagonals are now attached
            if x > 0 and y > 0:
                self.connected[player, y - 1, x - 1] = True
            if x > 0 and y < self.board_h - 1:
                self.connected[player, y + 1, x - 1] = True
            if x < self.board_w - 1 and y < self.board_h - 1:
                self.connected[player, y + 1, x + 1] = True
            if x < self.board_w - 1 and y > 0:
                self.connected[player, y - 1, x + 1] = True

        self.scores[player] += piece.get_num_tiles()
        return piece.get_num_tiles()

    def do_move(self, player, move):
        """
        Performs a move, returning a new board
        """
        new_board = self.__copy__()
        new_board.add_move(player, move)

        return new_board

    def get_legal_moves(self, player):
        """
        Returns a list of legal moves for given player for this board state
        """
        # Generate all legal moves
        move_list = []
        for piece in self.piece_list:
            for x in range(self.board_w):
                for y in range(self.board_h):
                    for ori in piece:
                        new_move = Move(piece,
                                        self.piece_list.pieces.index(piece),
                                        ori, x, y)
                        if self.check_move_valid(player, new_move):
                            move_list.append(new_move)
        return move_list

    def check_move_valid(self, player, move):
        """
        Check if <player> can legally perform <move>.

        For a move to be valid, it must:
        - Use a piece that is available
        - Be completely in bounds
        - Not be intersecting any other tiles
        - Not be adjacent to any of the player's other pieces
        - Be diagonally attached to one of the player's pieces or their corner

        Return True if the move is legal or False otherwise.
        """
        if not self.pieces[player, move.piece_index]:
            # piece has already been used
            return False

        attached_corner = False

        for (x, y) in move.orientation:
            # If any tile is illegal, this move isn't valid
            if not self.check_tile_legal(player, x + move.x, y + move.y):
                return False

            if self.check_tile_attached(player, x + move.x, y + move.y):
                attached_corner = True

            # If at least one tile is attached, this move is valid
        return attached_corner

    # def check_tile_legal(self, player, x, y):
    #     """
    #     Check if it's legal for <player> to place one tile at (<x>, <y>).
    #
    #     Legal tiles:
    #     - Are in bounds
    #     - Don't intersect with existing tiles
    #     - Aren't adjacent to the player's existing tiles
    #
    #     Returns True if legal or False if not.
    #     """
    #
    #     # Make sure tile in bounds
    #     if x < 0 or x >= self.board_w or y < 0 or y >= self.board_h:
    #         return False
    #
    #     # Otherwise, it's in the lookup table
    #     return self._legal[player, y, x]

    # def check_tile_attached(self, player, x, y):
    #     """Check if (<x>, <y>) is diagonally attached to <player>'s moves.
    #
    #     Note that this does not check if this move is legal.
    #
    #     Returns True if attached or False if not.
    #     """
    #
    #     # Make sure tile in bounds
    #     if x < 0 or x >= self.board_w or y < 0 or y >= self.board_h:
    #         return False
    #
    #     # Otherwise, it's in the lookup table
    #     return self.connected[player, y, x]

    def get_position(self, x, y):
        return self.state[y, x]

    def __eq__(self, other):
        return np.array_equal(self.state, other.state) and np.array_equal(self.pieces, other.pieces)

    def __hash__(self):
        return hash(str(self.state))

    def __str__(self):
        out_str = []
        for row in range(self.board_h):
            for col in range(self.board_w):
                if self.state[col, row] == -1:
                    out_str.append('_')
                else:
                    out_str.append(str(self.state[col, row]))
            out_str.append('\n')
        return ''.join(out_str)

    def __copy__(self):
        cpy_board = Board(self.board_w, self.board_h, self.num_players, self.piece_list)
        cpy_board.state = np.copy(self.state)
        cpy_board._legal = np.copy(self._legal)
        cpy_board.connected = np.copy(self.connected)
        cpy_board.pieces = np.copy(self.pieces)
        cpy_board.scores = self.scores[:]
        return cpy_board

    def get_paths(self, start, end_x, end_y, length):
        """
        :param start:
        :param end_x:
        :param end_y:
        :param length:
        :return:
        """
        if end_x < 0 or self.board_h <= end_x or end_y < 0 or self.board_w <= end_y \
                or self.get_number_in_cell(end_x, end_y) != length:
            # or self.get_number_color_in_cell(start[0], start[1]) != self.get_number_color_in_cell(end_x, end_y):
            return []

        return self.get_paths_rec([start], end_x, end_y, length - 1, length)

    def get_paths_rec(self, current_path, end_x, end_y, steps, length):
        x, y = current_path[-1]

        # If end of steps
        if steps == 0:
            # And got to end, return path found
            if current_path[-1] == (end_x, end_y):
                return [current_path]
            # Otherwise, path don't lead to end
            else:
                return []

        # If end is too far for path, don't try going there
        if manhattan_distance((x, y), (end_x, end_y)) > steps:
            return []

        if steps != length - 1 and self.get_number_in_cell(x, y) != 0:
            return []

        # collect valid paths from this point
        paths = []
        possible_steps = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

        for possible_step in possible_steps:
            # If point not on board or point already in path, skip it
            if possible_step[0] < 0 or self.board_h <= possible_step[0] or possible_step[1] < 0 or self.board_w <= \
                    possible_step[1] or possible_step in current_path:
                continue

            paths += self.get_paths_rec(current_path + [possible_step], end_x, end_y, steps - 1, length)

        return paths

    def get_number_in_cell(self, x, y):
        return self.state[x][y][0][0]

    def get_possible_paths(self, x, y):
        """

        :param self:
        :param x:
        :param y:
        :return:
        """
        paths = []
        length = self.get_number_in_cell(x, y)

        # If no path
        if length == 0:
            # print(f"Got x: {x}, y:{y}, but cell ({x}, {y}) has no number!")
            return None

        if length == 1:
            return [[(x, y)]]

        # Odd numbers must have odd manhattan distance between start and end
        # Even numbers must have even manhattan distance between start and end
        # This loop will only check possible end coordinates for the path
        offset = length % 2 == 0
        # For every possible x
        for i in range(length + 1):
            # And every other y such that i + j <= length
            for j in range(offset, length - i, 2):
                end_x = x + i
                m_end_x = x - i

                end_y = y + j
                m_end_y = y - j

                if i != 0:
                    paths += self.get_paths((x, y), end_x, end_y, length)
                    paths += self.get_paths((x, y), m_end_x, end_y, length)

                    if j != 0:
                        paths += self.get_paths((x, y), end_x, m_end_y, length)
                        paths += self.get_paths((x, y), m_end_x, m_end_y, length)

                elif j != 0:
                    paths += self.get_paths((x, y), end_x, end_y, length)
                    paths += self.get_paths((x, y), end_x, m_end_y, length)

            offset = not offset

        return paths

    def get_width(self):
        return self.board_w

    def get_height(self):
        return self.board_h


class Move:
    """
    A Move describes how one of the players is going to spend their move.

    It contains:
    - Piece: the ID of the piece being used
    - x/y: the center coordinates of the piece [0-19)
    - Rotation: how many times the piece should be rotated CW [0-3]
    - Flip: whether the piece should be flipped (True/False)
    """

    def __init__(self, path, color):
        self.path = path
        self.color = color

    def __str__(self):
        # # 5X5 matrix
        # out_str = [[' ' for _ in range(5)] for _ in range(5)]
        # for (x, y) in self.orientation:
        #     out_str[x][y] = '0'
        # out_str = '\n'.join(
        #     [''.join([x_pos for x_pos in out_str[y_val]])
        #      for y_val in range(5)]
        # )
        # return ''.join(out_str) + "x: " + str(self.x) + " y: " + str(self.y)
        pass
