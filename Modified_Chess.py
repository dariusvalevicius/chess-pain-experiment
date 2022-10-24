# Coded by Jérôme Genzling, McGill University

import pygame
import chess
import time
import re
import sys

board = [['  ' for i in range(8)] for i in range(8)]

## Creates a chess piece class that shows what team a piece is on, what type of piece it is and whether or not it can be killed by another selected piece.
class Piece:
    def __init__(self, team, type, image, killable=False):
        self.team = team
        self.type = type
        self.killable = killable
        self.image = image


## Creates instances of chess pieces, so far we got: pawn, king, rook and bishop
## The first parameter defines what team its on and the second, what type of piece it is
bp = Piece('b', 'p', 'bp.png')
wp = Piece('w', 'p', 'wp.png')
bk = Piece('b', 'k', 'bK.png')
wk = Piece('w', 'k', 'wK.png')
br = Piece('b', 'r', 'bR.png')
wr = Piece('w', 'r', 'wR.png')
bb = Piece('b', 'b', 'bB.png')
wb = Piece('w', 'b', 'wB.png')
bq = Piece('b', 'q', 'bQ.png')
wq = Piece('w', 'q', 'wQ.png')
bn = Piece('b', 'n', 'bN.png')
wn = Piece('w', 'n', 'wN.png')


starting_order = {(0, 0): pygame.image.load(br.image), (1, 0): pygame.image.load(bn.image),
                  (2, 0): pygame.image.load(bb.image), (3, 0): pygame.image.load(bq.image),
                  (4, 0): pygame.image.load(bk.image), (5, 0): pygame.image.load(bb.image),
                  (6, 0): pygame.image.load(bn.image), (7, 0): pygame.image.load(br.image),
                  (0, 1): pygame.image.load(bp.image), (1, 1): pygame.image.load(bp.image),
                  (2, 1): pygame.image.load(bp.image), (3, 1): pygame.image.load(bp.image),
                  (4, 1): pygame.image.load(bp.image), (5, 1): pygame.image.load(bp.image),
                  (6, 1): pygame.image.load(bp.image), (7, 1): pygame.image.load(bp.image),

                  (0, 2): None, (1, 2): None, (2, 2): None, (3, 2): None,
                  (4, 2): None, (5, 2): None, (6, 2): None, (7, 2): None,
                  (0, 3): None, (1, 3): None, (2, 3): None, (3, 3): None,
                  (4, 3): None, (5, 3): None, (6, 3): None, (7, 3): None,
                  (0, 4): None, (1, 4): None, (2, 4): None, (3, 4): None,
                  (4, 4): None, (5, 4): None, (6, 4): None, (7, 4): None,
                  (0, 5): None, (1, 5): None, (2, 5): None, (3, 5): None,
                  (4, 5): None, (5, 5): None, (6, 5): None, (7, 5): None,

                  (0, 6): pygame.image.load(wp.image), (1, 6): pygame.image.load(wp.image),
                  (2, 6): pygame.image.load(wp.image), (3, 6): pygame.image.load(wp.image),
                  (4, 6): pygame.image.load(wp.image), (5, 6): pygame.image.load(wp.image),
                  (6, 6): pygame.image.load(wp.image), (7, 6): pygame.image.load(wp.image),
                  (0, 7): pygame.image.load(wr.image), (1, 7): pygame.image.load(wn.image),
                  (2, 7): pygame.image.load(wb.image), (3, 7): pygame.image.load(wq.image),
                  (4, 7): pygame.image.load(wk.image), (5, 7): pygame.image.load(wb.image),
                  (6, 7): pygame.image.load(wn.image), (7, 7): pygame.image.load(wr.image),}


## returns the input if the input is within the boundaries of the board
def on_board(position):
    if position[0] > -1 and position[1] > -1 and position[0] < 8 and position[1] < 8:
        return True


## returns a string that places the rows and columns of the board in a readable manner
def convert_to_readable(board):
    output = ''

    for i in board:
        for j in i:
            try:
                output += j.team + j.type + ', '
            except:
                output += j + ', '
        output += '\n'
    return output


## resets "x's" and killable pieces
def deselect():
    for row in range(len(board)):
        for column in range(len(board[0])):
            if board[row][column] == 'x ':
                board[row][column] = '  '
            else:
                try:
                    board[row][column].killable = False
                except:
                    pass
    return convert_to_readable(board)


## Takes in board as argument then returns 2d array containing positions of valid moves
def highlight(board):
    highlighted = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 'x ':
                highlighted.append((i, j))
            else:
                try:
                    if board[i][j].killable:
                        highlighted.append((i, j))
                except:
                    pass
    return highlighted

def check_team(moves, index):
    row, col = index
    if moves%2 == 0:
        if board[row][col].team == 'w':
            return True
    else:
        if board[row][col].team == 'b':
            return True

WIDTH = 480

WIN = pygame.display.set_mode((WIDTH, WIDTH))
# WIN = pygame.display.set_mode((2*WIDTH, 2*WIDTH))

""" This is creating the window that we are playing on, it takes a tuple argument which is the dimensions of the window so in this case 800 x 800px
"""

pygame.display.set_caption("Chess")
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
YELLOW = (204, 204, 0)
BLUE = (50, 255, 255)
BLACK = (0, 0, 0)


class Node:
    def __init__(self, row, col, width):
        self.row = row
        self.col = col
        self.x = int(row * width)
        self.y = int(col * width)
        self.colour = WHITE
        self.occupied = None

    def draw(self, WIN):
        pygame.draw.rect(WIN, self.colour, (self.x, self.y, WIDTH / 8, WIDTH / 8))

    def setup(self, WIN):
        if starting_order[(self.row, self.col)]:
            if starting_order[(self.row, self.col)] == None:
                pass
            else:
                WIN.blit(starting_order[(self.row, self.col)], (self.x, self.y))

        """
        For now it is drawing a rectangle but eventually we are going to need it
        to use blit to draw the chess pieces instead
        """


def make_grid(rows, width):
    grid = []
    gap = WIDTH // rows
    print(gap)
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(j, i, gap)
            grid[i].append(node)
            if (i+j)%2 ==1:
                grid[i][j].colour = GREY
    return grid
"""
This is creating the nodes thats are on the board(so the chess tiles)
I've put them into a 2d array which is identical to the dimesions of the chessboard
"""


def draw_grid(win, rows, width):
    gap = width // 8
    for i in range(rows):
        pygame.draw.line(win, BLACK, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, BLACK, (j * gap, 0), (j * gap, width))

    """
    The nodes are all white so this we need to draw the grey lines that separate all the chess tiles
    from each other and that is what this function does"""


def update_display(win, grid, rows, width):
    for row in grid:
        for spot in row:
            spot.draw(win)
            spot.setup(win)
    draw_grid(win, rows, width)
    pygame.display.update()


def Find_Node(pos, WIDTH):
    interval = WIDTH / 8
    y, x = pos
    rows = y // interval
    columns = x // interval
    return int(rows), int(columns)


def display_potential_moves(positions, grid):
    for i in positions:
        x, y = i
        grid[x][y].colour = BLUE
        """
        Displays all the potential moves
        """


def Do_Move(OriginalPos, FinalPosition, WIN):
    starting_order[FinalPosition] = starting_order[OriginalPos]
    starting_order[OriginalPos] = None


def remove_highlight(grid):
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if (i+j)%2 == 0:
                grid[i][j].colour = WHITE
            else:
                grid[i][j].colour = GREY
    return grid
"""this takes in 2 co-ordinate parameters which you can get as the position of the piece and then the position of the node it is moving to
you can get those co-ordinates using my old function for swap"""

def translate_chesslib_to_board(chessboard,board):
    list_board = re.sub(' ', '', str(chessboard)).split('\n')
    for i in range(8):
        for j in range(8):
            if list_board[i][j] == 'p': board[i][j] = Piece('b', 'p', 'bP.png')
            if list_board[i][j] == 'n': board[i][j] = Piece('b', 'n', 'bN.png')
            if list_board[i][j] == 'b': board[i][j] = Piece('b', 'b', 'bB.png')
            if list_board[i][j] == 'k': board[i][j] = Piece('b', 'k', 'bK.png')
            if list_board[i][j] == 'q': board[i][j] = Piece('b', 'q', 'bQ.png')
            if list_board[i][j] == 'r': board[i][j] = Piece('b', 'r', 'bR.png')

            if list_board[i][j] == 'P': board[i][j] = Piece('w', 'p', 'wP.png')
            if list_board[i][j] == 'N': board[i][j] = Piece('w', 'n', 'wN.png')
            if list_board[i][j] == 'B': board[i][j] = Piece('w', 'b', 'wB.png')
            if list_board[i][j] == 'K': board[i][j] = Piece('w', 'k', 'wK.png')
            if list_board[i][j] == 'Q': board[i][j] = Piece('w', 'q', 'wQ.png')
            if list_board[i][j] == 'R': board[i][j] = Piece('w', 'r', 'wR.png')

    return board

def starting_order_update(chessboard):
    starting_order = {}

    list_board = re.sub(' ', '', str(chessboard)).split('\n')
    for i in range(8):
        for j in range(8):
            if list_board[i][j] == 'p': starting_order[(j, i)] = pygame.image.load(bp.image)
            if list_board[i][j] == 'n': starting_order[(j, i)] = pygame.image.load(bn.image)
            if list_board[i][j] == 'b': starting_order[(j, i)] = pygame.image.load(bb.image)
            if list_board[i][j] == 'k': starting_order[(j, i)] = pygame.image.load(bk.image)
            if list_board[i][j] == 'q': starting_order[(j, i)] = pygame.image.load(bq.image)
            if list_board[i][j] == 'r': starting_order[(j, i)] = pygame.image.load(br.image)

            if list_board[i][j] == '.': starting_order[(j, i)] = None

            if list_board[i][j] == 'P': starting_order[(j, i)] = pygame.image.load(wp.image)
            if list_board[i][j] == 'N': starting_order[(j, i)] = pygame.image.load(wn.image)
            if list_board[i][j] == 'B': starting_order[(j, i)] = pygame.image.load(wb.image)
            if list_board[i][j] == 'K': starting_order[(j, i)] = pygame.image.load(wk.image)
            if list_board[i][j] == 'Q': starting_order[(j, i)] = pygame.image.load(wq.image)
            if list_board[i][j] == 'R': starting_order[(j, i)] = pygame.image.load(wr.image)

    return starting_order

def square_to_coords(uci):
    # b2 corresponds to [6][1], d5 corresponds to [3][3] coordinates
    first_coord = abs(int(uci[1])-8)
    second_coord = ord(uci[0])-97   #ord(a) = 97
    return (first_coord,second_coord)


def UCI_to_matrix_coords(uci_string):

    inc_square, going_square = uci_string[:2], uci_string[2:]
    return [square_to_coords(inc_square),square_to_coords(going_square)]

def coords_to_square(coords):
    x,y= coords
    letter = chr(y+97) #chr(97) = 'a'
    row = str(8-x)
    return letter+row

def select_possible_moves(coords,board,legal_moves):
    #We suppose here that the square has a piece, checked true in the main function
    x,y = coords
    possible = []
    for i in legal_moves:
        if (x,y) == i[0]:
            possible.append(i[1])
    print(possible)
    for i in possible:
        if board[i[0]][i[1]] == '  ':
            board[i[0]][i[1]] = 'x '
        else: board[i[0]][i[1]].killable = True

    return highlight(board)

def update_the_chessboard(chessboard,records):
    lastmove = records[-1]
    chessboard.push(chess.Move.from_uci(lastmove))

    legal_moves = list(chessboard.legal_moves)
    for i in range(len(legal_moves)):
        legal_moves[i] = UCI_to_matrix_coords(str(legal_moves[i]))

    return chessboard,legal_moves

def parser_puzzle(puzzle_line):
    split_line = puzzle_line.split(',')[1:5]    #PuzzleId/Fen/Moves/Rating
    return split_line

def define_the_puzzle(fen,board):
    recorded_moves = []
    chessboard = chess.Board()
    chessboard.set_fen(fen)
    translate_chesslib_to_board(chessboard, board)
    starting_order = starting_order_update(chessboard)
    moves = chessboard.fullmove_number - 1
    legal_moves = list(chessboard.legal_moves)
    for i in range(len(legal_moves)):
        legal_moves[i] = UCI_to_matrix_coords(str(legal_moves[i]))

    return chessboard,board,starting_order,moves,legal_moves,recorded_moves

test_fen = '8/1p3p1k/6r1/p1p2KR1/P2pP3/1P1P4/2P5/8 b - - 8 52'

def main(WIN, WIDTH):
    global board
    global starting_order
    try_chess_board,board,starting_order,moves,legal_moves,recorded_moves = define_the_puzzle(test_fen,board)

    selected = False
    piece_to_move=[]
    grid = make_grid(8, WIDTH)
    while True:
        pygame.time.delay(50) ##stops cpu dying
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            """This quits the program if the player closes the window"""

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                y, x = Find_Node(pos, WIDTH)
                if selected == False:
                    try:
                        possible = select_possible_moves((x,y),board,legal_moves)
                        for positions in possible:
                            row, col = positions
                            grid[row][col].colour = BLUE
                        piece_to_move = x,y
                        selected = True
                    except:
                        piece_to_move = []
                        print('Can\'t select')

                else:
                    try:
                        if board[x][y].killable == True:
                            row, col = piece_to_move ## coords of original piece
                            board[x][y] = board[row][col]
                            board[row][col] = '  '
                            deselect()
                            remove_highlight(grid)
                            Do_Move((col, row), (y, x), WIN)
                            moves += 1
                            recorded_moves.append(coords_to_square((row,col))+coords_to_square((x,y)))
                            print(convert_to_readable(board))
                            print(recorded_moves)
                            try_chess_board, legal_moves = update_the_chessboard(try_chess_board, recorded_moves)
                            print(try_chess_board)
                            print(legal_moves)
                        else:
                            deselect()
                            remove_highlight(grid)
                            selected = False
                            print("Deselected")
                    except:
                        if board[x][y] == 'x ':
                            row, col = piece_to_move
                            board[x][y] = board[row][col]
                            board[row][col] = '  '
                            deselect()
                            remove_highlight(grid)
                            Do_Move((col, row), (y, x), WIN)
                            moves += 1
                            recorded_moves.append(coords_to_square((row, col)) + coords_to_square((x, y)))
                            print(convert_to_readable(board))
                            print(recorded_moves)
                            try_chess_board, legal_moves = update_the_chessboard(try_chess_board,recorded_moves)
                            print(try_chess_board)
                            print(legal_moves)
                        else:
                            deselect()
                            remove_highlight(grid)
                            selected = False
                            print("Invalid move")
                    selected = False

            update_display(WIN, grid, 8, WIDTH)


main(WIN, WIDTH)