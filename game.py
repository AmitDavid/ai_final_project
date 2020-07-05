import copy
from agent import *


class Game:
    def __init__(self, xml_dict):
        """
        :param file: XML file that represents the board
        """
        # TODO represent the board as coordinates
        self.initial_board = [[(0, 0) for i in range(xml_dict["width"])] for j in range(xml_dict["height"])]
        self.board = None
        self.goal_board = [[(0, 0) for i in range(xml_dict["width"])] for j in range(xml_dict["height"])]
        self.heuristic = None
        self.successors = []

    def generate_boards(self, xml_dict):
        for color, paths in xml_dict.items():

            for path in paths:
                # fill the initial board with the (len,color) of the wanted path
                cur_num = len(path)
                start = path[0]
                end = path[len(path) - 1]
                self.initial_board[start[0]][start[1]] = (cur_num, color)
                self.initial_board[end[0]][end[1]] = (cur_num, color)

                # fill the first and last entries of the path in goal board
                self.goal_board[start[0]][start[1]] = (cur_num, color)
                self.goal_board[end[0]][end[1]] = (cur_num, color)

                # fill the rest of the entries of the path with color only
                # without number
                for i, j in path[1: (len(path) - 1)]:
                    self.goal_board[i][j] = (0, color)
        # in this point we will create a deep copy of the initial board to
        # work on during the game
        self.board = copy.deepcopy(self.initial_board)

    def __str__(self):
        """
        prints the board
        :return:
        """
        print(self.board)

    def get_initial_board(self):
        return self.initial_board

    def set_heuristic(self, heuristic):
        self.heuristic = heuristic

    def get_heuristic(self):
        return self.heuristic

    def get_current_board(self):
        """
        returns the current board object
        :return:
        """
        return self.board

    def get_all_possible_actions(self, x, y):
        pass

    def get_possible_actions(self, all_possible_actions):
        pass

    def set_successors(self, possible_actions):
        successors = []
        for act_pat in possible_actions:
            successors.append(self.get_successor(act_pat))
        self.successors = successors

    def get_successors(self):
        return self.successors

    def get_successor(self, action):
        result = [[(0, 0) for i in range(self.board.board_w)] for j in range(self.board.board_h)]
        color = self.board[action[0][0]][action[0][1]]
        size = len(action)
        result[action[0][0]][action[0][1]] = (size, color)
        result[action[len(action)-1][0]][action[len(action)-1][1]] = (size, color)
        for i, j in action[1: (len(action) - 1)]:
            result[i][j] = (0, color)
        return result

    def set_successor(self, action):
        self.board = self.get_successor(action)

    def is_goal_state(self):
        return self.board == self.goal_board

    # def do_action(self, cur_state, action):
    #     """
    #     move
    #     :param action:
    #     :return:
    #     """
    #     pass
    


if __name__ == '__main__':
    xml = get_xml_from_path('boards/small_color.xml')
    my_game = Game(xml)
    print("lll")
    #updated 6:20

