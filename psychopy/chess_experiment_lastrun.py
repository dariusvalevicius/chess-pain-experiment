#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2022.2.4),
    on November 28, 2022, at 14:10
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y

"""

# --- Import packages ---
from psychopy import locale_setup
from psychopy import prefs
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding

import psychopy.iohub as io
from psychopy.hardware import keyboard

# Run 'Before Experiment' code from global_timer_start

## Initialize global clock var
global_clock = core.Clock()
global_time = 0
# Run 'Before Experiment' code from move_piece
import time
import chess

def coord_to_pos(coord):
    '''Convert coordinate system to
    position (in units of screen height)'''
    if type(coord) == int:
        pos = (coord/8) - 9/16
    else:
        pos = [0, 0]
        for i in range(len(coord)):
            pos[i] = (coord[i]/8) - 9/16
    return pos
    
def pos_to_coord(pos):
    '''Convert position (in units of screen height)
    to coordinate system'''
    if type(pos) == int:
        coord = int(round((pos + 9/16) * 8))
    else:
        coord = [1, 1]
        for i in range(len(pos)):
            coord[i] = int(round((pos[i] + 9/16) * 8))
    return coord
    
def code_to_coord(code):
    '''Convert FEN code to coordinate system'''
    x_axis = ["a", "b", "c", "d", "e", "f", "g", "h"]
    x_pos = x_axis.index(code[0]) + 1
    y_pos = int(code[1])
    return [x_pos, y_pos]
    
def coord_to_code(coord):
    '''Convert coord to UCI move code'''
    x_axis = ["a", "b", "c", "d", "e", "f", "g", "h"]
#    print(f"COORD: {coord}")
    index = coord[0] - 1
#    print(f"INDEX: {index}")
    x_code = x_axis[index]
    y_code = coord[1]
    return f"{x_code}{y_code}"

    
def lerp_position(start_pos, end_pos, fraction):
    '''Linear interpolation between two points'''
    move_vector = np.subtract(end_pos, start_pos)
    current_pos = start_pos + (fraction * move_vector)
    return current_pos
    
def create_piece(code, x, y, i):
    '''Initialize and display a chess piece'''
    if code.islower():
        image_path = "images/" + code + ".png"
    else:
        image_path = "images/" + code + "_w.png"
    x_pos = coord_to_pos(x)
    y_pos = coord_to_pos(y)
    piece = visual.ImageStim(win=win, name=(code + str(x) + str(y)), image=image_path, 
    anchor="center", pos=(x_pos, y_pos), size=(1/10, 1/10), depth = (-10 - i),
    texRes=128.0, interpolate=True)
    return piece
    
def create_pieces(fen, board_state):
    '''Create all pieces in the FEN'''
    x = 1
    y = 8
    for i in range(len(fen[0])):
        element = fen[0][i]
        if (element == "/"):
            x = 1
            y -= 1
        if (element.isdigit()):
            x += int(element)
        if (element in piece_codes):
            piece = create_piece(element, x, y, i)
            piece.setAutoDraw(True)
            if element.isupper():
                white_pieces.append(piece)
            else:
                black_pieces.append(piece)
            board_state[y][x] = piece.name
            x += 1
    return white_pieces, black_pieces, board_state
    
def draw_square(code):
    coord = code_to_coord(code)
    x_pos = coord_to_pos(coord[0])
    y_pos = coord_to_pos(coord[1])
    
    polygon = visual.Rect(
        win=win, name=(code + '_square'),
        width=(1/8), height=(1/8),
        ori=0.0, pos=(x_pos, y_pos), anchor='center',
        lineWidth=0,     colorSpace='rgb',  lineColor=[0, 0, 0], fillColor=[249/256, 194/256, 46/256],
        depth=-5, interpolate=True)
    polygon.setAutoDraw(True)
    return polygon
    
def search_pieces(piece_array, piece_name):
    '''Search for a piece in array by piece.name'''
    for piece in piece_array:
        if piece_name == piece.name:
            return piece
    print("Warning: Did not find piece by name " + piece_name + " in array.")
    return None

def evaluate_move(board_state, enemy_pieces, player_pieces, target_square):
    '''See if player move is taking an enemy piece'''
#    print(target_square)
    target_square_content = board_state[target_square[1]][target_square[0]]
    if target_square_content:
        piece_to_take = search_pieces(enemy_pieces, target_square_content)
        if piece_to_take is None:
            piece_to_take = search_pieces(player_pieces, target_square_content)
        return piece_to_take

def move_piece(time_elapsed, piece, start_coord, end_coord, move_time):
    '''Move piece by a certain amount this frame'''
    start_pos = coord_to_pos(start_coord)
    end_pos = coord_to_pos(end_coord)
    move_finished = False
    if (time_elapsed < move_time):
        piece.pos = lerp_position(start_pos, end_pos, time_elapsed / move_time)
    else:
        piece.pos = end_pos
        move_finished = True
    return piece, move_finished
    
def begin_move(piece, start_coord, end_coord):
    '''Initiate the computer movemement of a piece'''
    if piece is None:
        return None
    else:
        return piece, start_coord, end_coord
        
def update_board_state(board_state, old_coord, new_coord, value):
    '''Update the board state matrix
    when a piece changes squares'''
    board_state[new_coord[1]][new_coord[0]] = value
    
    if board_state[old_coord[1]][old_coord[0]] == value: # Only delete old entry if it has not already been replaced
        board_state[old_coord[1]][old_coord[0]] = ''
    
#    for row in board_state:
#        print(row)
    
    return board_state
                       
        
def clear_pieces(pieces):
    for piece in pieces:
        piece.setAutoDraw(False)
#        piece._unload()

# Could combine this function with evaluate_move():
def check_valid_move(board_state, player_pieces, coord, possible_moves):
    '''See if player move is valid'''
    target_square_content = board_state[coord[1]][coord[0]]
    if coord[0] < 1 or coord[0] > 8 or coord[1] < 1 or coord[1] > 8:
        return False
    elif search_pieces(player_pieces, target_square_content):
        return False
    elif coord not in possible_moves:
        return False
    else:
        return True
        
def check_correct_move(move_num, moves, start_coord, end_coord):
    correct_start = code_to_coord(moves[move_num][0:2])
    correct_end = code_to_coord(moves[move_num][2:4])
    if (start_coord == correct_start) and (end_coord == correct_end):
        return True
    else:
        return False
    
def find_empty_take_square(board_state):
    num_cols = 3
    
    target = [9,8]
    while board_state[target[1]][target[0]]:
        if target[0] == 8 + num_cols:
            target[0] = 9
            target[1] = target[1] - 1
        else:
            target[0] = target[0] + 1
    return target
    
    
def start_enemy_move(moves, move_num, board_state, enemy_pieces):
    # Generate yellow rectangles over first black move
    move_start = moves[move_num][0:2]
    move_end = moves[move_num][2:4]
    highlight_squares = []
    for move in [move_start, move_end]:
        highlight_squares.append(draw_square(move))
        
    # Begin first move
    # This code needs to be generalized in a function
    start_coord = code_to_coord(move_start)
    end_coord = code_to_coord(move_end)
    piece_name = board_state[start_coord[1]][start_coord[0]]
    
    moving_piece = search_pieces(enemy_pieces, piece_name)
        
    return moving_piece, start_coord, end_coord, highlight_squares
            
def scan_legal_moves(board_lib, piece):
    piece_coord = pos_to_coord(piece.pos)
    start = coord_to_code(piece_coord)
    
    legal_moves = board_lib.legal_moves
    x_axis = ["a", "b", "c", "d", "e", "f", "g", "h"]
    
    possible_moves = []

    for x in range(1,9):
        for y in range(1,9):
           
            uci_code = f"{start}{x_axis[x-1]}{y}"
            if uci_code[0:2] == uci_code[2:4]:
                continue
            move = chess.Move.from_uci(uci_code)
            if move in legal_moves:
               possible_moves.append([x, y])
               
    return possible_moves
 
def draw_possible_moves(possible_moves):
    image_path = "images/valid_move.png"
    valid_move_highlights = []
    
    for move in possible_moves:
        x_pos = coord_to_pos(move[0])
        y_pos = coord_to_pos(move[1])
        
        highlight = visual.ImageStim(win=win, name=f"highlight", image=image_path, 
        anchor="center", pos=(x_pos, y_pos), size=(1/8, 1/8), depth = -20,
        texRes=128.0, interpolate=True)
        highlight.setAutoDraw(True)
        
        valid_move_highlights.append(highlight)
        
    return valid_move_highlights
    
def check_uci_move(board_lib, start_coord, end_coord):
    '''Update python chess board representation'''
    uci_code = coord_to_code(start_coord) + coord_to_code(end_coord)
    
    move = chess.Move.from_uci(uci_code)
    
    castling_king = board_lib.is_kingside_castling(move)
    castling_queen = board_lib.is_queenside_castling(move)

    en_passant = board_lib.is_en_passant(move)
    
#    if move in board_lib.legal_moves:
#        board_lib.push(move)  # Make the move
#    else:
#        print("Illegal move. May be a castling rook move.")
#        print(f"Start coord: {start_coord}; End coord: {end_coord}")
        
#    board_lib.push(move)  # Make the move
    
    return move, castling_king, castling_queen, en_passant
    
def make_en_passant_move(piece, white_pieces, black_pieces, board_state, end_coord):
#    print("EN PASSANT MOVE")
    target_square_content = []
    piece_taken = []
    if piece in white_pieces:
        target_square_content = board_state[end_coord[1] - 1][end_coord[0]]
        piece_taken = search_pieces(black_pieces, target_square_content)
    elif piece in black_pieces:
        target_square_content = board_state[end_coord[1] + 1][end_coord[0]]
        piece_taken = search_pieces(white_pieces, target_square_content)
#    print(f"PIECE TAKEN: {piece_taken.name}")
    return piece_taken

def try_pawn_promotion(piece, end_coord):
    if end_coord[1] in [1, 8]:
        if "P" in piece.name:
            print("PAWN PROMOTION")
            piece.image = "images/q_w.png"
        elif "p" in piece.name:
            print("PAWN PROMOTION")
            piece.image = "images/q.png"
    return None
        
def start_rook_castle(pieces, start_coord, end_coord):
    '''Move rook to target square during castling move'''
    
    target_square_content = board_state[start_coord[1]][start_coord[0]]
    
#    for piece in pieces:
#        print(f"Piece name: {piece.name}")
#    print(f"Target square content: {target_square_content}")
    
    target_rook = search_pieces(pieces, target_square_content)
    moving_piece, start_coord, end_coord = begin_move(target_rook, start_coord, end_coord)
    
    return moving_piece, start_coord, end_coord
    
def try_castling_move(castling_king, castling_queen, pieces, player_color):
    moving_piece = None
    start_coord = []
    end_coord = []
    
    if castling_king:
        print("CASTLING KINSIDE")
        if player_color == "b":
            # move rook g1e1
            moving_piece, start_coord, end_coord = start_rook_castle(pieces, [8,1], [6,1])
        elif player_color == "w":
            # move rook a8c8
            moving_piece, start_coord, end_coord = start_rook_castle(pieces, [8,8], [6,8])
    elif castling_queen:
        print("CASTLING QUEENSIDE")
        if player_color == "b":
            # move rook a1d1
            moving_piece, start_coord, end_coord = start_rook_castle(pieces, [1,1], [4,1])
        elif player_color == "w":
            # move rook g8e8
            moving_piece, start_coord, end_coord = start_rook_castle(pieces, [1,8], [4,8])
        
    return moving_piece, start_coord, end_coord
    
    
    
    
feedback_text = ''   
correct_color = "springgreen"
incorrect_color = "red"

puzzle_time = 0

# Data for piece codes and x axis labels
piece_codes = ["p", "n", "b", "r", "q", "k", "P", "N", "B", "R", "Q", "K"]

# Time it takes for a piece to move from A to B
# Could instead make it a speed parameter
move_time = 1


# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
# Store info about the experiment session
psychopyVersion = '2022.2.4'
expName = 'chess_experiment'  # from the Builder filename that created this script
expInfo = {
    'participant': f"{randint(0, 999999):06.0f}",
    'participant_elo': '1600',
}
# --- Show participant info dialog --
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName
expInfo['psychopyVersion'] = psychopyVersion

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = _thisDir + os.sep + u'data/%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath='C:\\Users\\dariu\\Documents\\Roy Lab Freelance Work\\Chess Experiment\\chess-pain-experiment\\psychopy\\chess_experiment_lastrun.py',
    savePickle=True, saveWideText=True,
    dataFileName=filename)
# save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

endExpNow = False  # flag for 'escape' or other condition => quit the exp
frameTolerance = 0.001  # how close to onset before 'same' frame

# Start Code - component code to be run after the window creation

# --- Setup the Window ---
win = visual.Window(
    size=[1920, 1080], fullscr=False, screen=0, 
    winType='pyglet', allowStencil=False,
    monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
    blendMode='avg', useFBO=True, 
    units='height')
win.mouseVisible = True
# store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess
# --- Setup input devices ---
ioConfig = {}

# Setup iohub keyboard
ioConfig['Keyboard'] = dict(use_keymap='psychopy')

ioSession = '1'
if 'session' in expInfo:
    ioSession = str(expInfo['session'])
ioServer = io.launchHubServer(window=win, **ioConfig)
eyetracker = None

# create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard(backend='iohub')

# --- Initialize components for Routine "intro" ---
intro_text = visual.TextStim(win=win, name='intro_text',
    text='Welcome to the experiment.',
    font='Open Sans',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
    color='black', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
start_experiment = keyboard.Keyboard()

# --- Initialize components for Routine "instructions_chess_puzzle" ---
chess_instructions = visual.TextStim(win=win, name='chess_instructions',
    text='Instructions slide\n\nComplete the chess puzzles.',
    font='Open Sans',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
    color=[-1.0000, -1.0000, -1.0000], colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
start_block = keyboard.Keyboard()

# --- Initialize components for Routine "chess_puzzle" ---
mouse = event.Mouse(win=win)
x, y = [None, None]
mouse.mouseClock = core.Clock()
chess_board = visual.ImageStim(
    win=win,
    name='chess_board', 
    image='images/board_2.png', mask=None, anchor='center',
    ori=0.0, pos=(0, 0), size=(1, 1),
    color=[1,1,1], colorSpace='rgb', opacity=None,
    flipHoriz=False, flipVert=False,
    texRes=128.0, interpolate=True, depth=-1.0)
chess_feedback = visual.TextStim(win=win, name='chess_feedback',
    text=feedback_text,
    font='Open Sans',
    pos=(-5/8, 0), height=0.05, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=-3.0);
puzzle_timer = visual.TextStim(win=win, name='puzzle_timer',
    text=puzzle_time,
    font='Open Sans',
    pos=(-5/8, 2/8), height=0.05, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=-4.0);
global_timer = visual.TextStim(win=win, name='global_timer',
    text=None,
    font='Open Sans',
    pos=(-5/8, 3/8), height=0.05, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=-5.0);

# --- Initialize components for Routine "instructions_two_back" ---
text_2 = visual.TextStim(win=win, name='text_2',
    text="This is the 2-back experiment.\n\nLook at the letter appearing on the screen. Your task is to remember the letter appearing two steps before the current letter. If the current letter is the same as the letter two steps before, e.g. an 'X' followed by a 'Y' followed by another 'X', press the spacebar.\n\nPress 'space' to begin.",
    font='Open Sans',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
press_to_continue = keyboard.Keyboard()

# --- Initialize components for Routine "two_back" ---
fixation = visual.TextStim(win=win, name='fixation',
    text='+',
    font='Open Sans',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
letter = visual.TextStim(win=win, name='letter',
    text='',
    font='Open Sans',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=-1.0);
key_resp = keyboard.Keyboard()

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.Clock()  # to track time remaining of each (possibly non-slip) routine 

# --- Prepare to start Routine "intro" ---
continueRoutine = True
routineForceEnded = False
# update component parameters for each repeat
start_experiment.keys = []
start_experiment.rt = []
_start_experiment_allKeys = []
# keep track of which components have finished
introComponents = [intro_text, start_experiment]
for thisComponent in introComponents:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
frameN = -1

# --- Run Routine "intro" ---
while continueRoutine:
    # get current time
    t = routineTimer.getTime()
    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *intro_text* updates
    if intro_text.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        intro_text.frameNStart = frameN  # exact frame index
        intro_text.tStart = t  # local t and not account for scr refresh
        intro_text.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(intro_text, 'tStartRefresh')  # time at next scr refresh
        intro_text.setAutoDraw(True)
    
    # *start_experiment* updates
    waitOnFlip = False
    if start_experiment.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        start_experiment.frameNStart = frameN  # exact frame index
        start_experiment.tStart = t  # local t and not account for scr refresh
        start_experiment.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(start_experiment, 'tStartRefresh')  # time at next scr refresh
        start_experiment.status = STARTED
        # keyboard checking is just starting
        waitOnFlip = True
        win.callOnFlip(start_experiment.clock.reset)  # t=0 on next screen flip
        win.callOnFlip(start_experiment.clearEvents, eventType='keyboard')  # clear events on next screen flip
    if start_experiment.status == STARTED and not waitOnFlip:
        theseKeys = start_experiment.getKeys(keyList=['space'], waitRelease=False)
        _start_experiment_allKeys.extend(theseKeys)
        if len(_start_experiment_allKeys):
            start_experiment.keys = _start_experiment_allKeys[-1].name  # just the last key pressed
            start_experiment.rt = _start_experiment_allKeys[-1].rt
            # a response ends the routine
            continueRoutine = False
    
    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        routineForceEnded = True
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in introComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# --- Ending Routine "intro" ---
for thisComponent in introComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# the Routine "intro" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

# set up handler to look after randomisation of conditions etc
chess_levels = data.TrialHandler(nReps=1.0, method='sequential', 
    extraInfo=expInfo, originPath=-1,
    trialList=data.importConditions('conditions_chess_levels.tsv'),
    seed=None, name='chess_levels')
thisExp.addLoop(chess_levels)  # add the loop to the experiment
thisChess_level = chess_levels.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisChess_level.rgb)
if thisChess_level != None:
    for paramName in thisChess_level:
        exec('{} = thisChess_level[paramName]'.format(paramName))

for thisChess_level in chess_levels:
    currentLoop = chess_levels
    # abbreviate parameter names if possible (e.g. rgb = thisChess_level.rgb)
    if thisChess_level != None:
        for paramName in thisChess_level:
            exec('{} = thisChess_level[paramName]'.format(paramName))
    
    # --- Prepare to start Routine "instructions_chess_puzzle" ---
    continueRoutine = True
    routineForceEnded = False
    # update component parameters for each repeat
    start_block.keys = []
    start_block.rt = []
    _start_block_allKeys = []
    # keep track of which components have finished
    instructions_chess_puzzleComponents = [chess_instructions, start_block]
    for thisComponent in instructions_chess_puzzleComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "instructions_chess_puzzle" ---
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *chess_instructions* updates
        if chess_instructions.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            chess_instructions.frameNStart = frameN  # exact frame index
            chess_instructions.tStart = t  # local t and not account for scr refresh
            chess_instructions.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(chess_instructions, 'tStartRefresh')  # time at next scr refresh
            chess_instructions.setAutoDraw(True)
        
        # *start_block* updates
        waitOnFlip = False
        if start_block.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            start_block.frameNStart = frameN  # exact frame index
            start_block.tStart = t  # local t and not account for scr refresh
            start_block.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(start_block, 'tStartRefresh')  # time at next scr refresh
            start_block.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(start_block.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(start_block.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if start_block.status == STARTED and not waitOnFlip:
            theseKeys = start_block.getKeys(keyList=['space'], waitRelease=False)
            _start_block_allKeys.extend(theseKeys)
            if len(_start_block_allKeys):
                start_block.keys = _start_block_allKeys[-1].name  # just the last key pressed
                start_block.rt = _start_block_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False
        
        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in instructions_chess_puzzleComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "instructions_chess_puzzle" ---
    for thisComponent in instructions_chess_puzzleComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # Run 'End Routine' code from global_timer_start
    
    ## Start clock for the block
    global_clock.reset()
    # the Routine "instructions_chess_puzzle" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # set up handler to look after randomisation of conditions etc
    chess_trials = data.TrialHandler(nReps=1.0, method='random', 
        extraInfo=expInfo, originPath=-1,
        trialList=data.importConditions('conditions_chess.tsv'),
        seed=None, name='chess_trials')
    thisExp.addLoop(chess_trials)  # add the loop to the experiment
    thisChess_trial = chess_trials.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisChess_trial.rgb)
    if thisChess_trial != None:
        for paramName in thisChess_trial:
            exec('{} = thisChess_trial[paramName]'.format(paramName))
    
    for thisChess_trial in chess_trials:
        currentLoop = chess_trials
        # abbreviate parameter names if possible (e.g. rgb = thisChess_trial.rgb)
        if thisChess_trial != None:
            for paramName in thisChess_trial:
                exec('{} = thisChess_trial[paramName]'.format(paramName))
        
        # --- Prepare to start Routine "chess_puzzle" ---
        continueRoutine = True
        routineForceEnded = False
        # update component parameters for each repeat
        # setup some python lists for storing info about the mouse
        mouse.clicked_name = []
        gotValidClick = False  # until a click is received
        # Run 'Begin Routine' code from move_piece
        # Begin Routine
        
        # Initialize board state and piece arrays
        board_state = [['' for i in range(12)] for i in range(9)]
        white_pieces = []
        black_pieces = []
        
        # Chess board from chess library
        
        board_lib = chess.Board()
        board_lib.set_fen(FEN)
        
        # For testing: sample FEN string
        fen_str = FEN
        fen = fen_str.split(" ")
        
        moves_str = moves
        moves = moves_str.split()
        
        # Populate the board based on the FEN
        white_pieces, black_pieces, board_state = create_pieces(fen, board_state)
        clicked_piece = None
        
        player_pieces = []
        enemy_pieces = []
        
        player_color = fen[1]
        
        # Identify player and enemy
        if player_color == "b":
            player_pieces = white_pieces
            enemy_pieces = black_pieces
        elif player_color == "w":
            player_pieces = black_pieces
            enemy_pieces = white_pieces
        else:
            raise Exception("ERROR: FEN does not have team label.")
        
        
        # Set up first computer move
        enemy_move = True
        move_num = 0
            
        moving_piece, start_coord, end_coord, highlight_squares = start_enemy_move(moves, move_num, board_state, enemy_pieces)
        
        # Initialize computer movement clock
        move_clock = core.Clock()
        move_clock.reset(newT=0.0)
        
        # Start mouse clock
        # This is for a click cooldown to prevent accidental double-clicking
        mouse_clock = core.Clock()
        mouse_clock.addTime(100)
        
        # Track correct/incorrect moves
        player_move_start = []
        possible_moves = []
        valid_move_highlights = []
        correct_move = True
        
        #global global_clock
        
        puzzle_clock = core.Clock()
        puzzle_time = puzzle_clock.getTime()
        
        timeout_clock = core.Clock()
        timout_time = 0
        timeout = False
        
        feedback_text = ''   
        chess_feedback.text = feedback_text
        
        is_castling_move = False
        
        
        
        
        
        # keep track of which components have finished
        chess_puzzleComponents = [mouse, chess_board, chess_feedback, puzzle_timer, global_timer]
        for thisComponent in chess_puzzleComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "chess_puzzle" ---
        while continueRoutine:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            # *mouse* updates
            if mouse.status == NOT_STARTED and t >= 0-frameTolerance:
                # keep track of start time/frame for later
                mouse.frameNStart = frameN  # exact frame index
                mouse.tStart = t  # local t and not account for scr refresh
                mouse.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(mouse, 'tStartRefresh')  # time at next scr refresh
                mouse.status = STARTED
                mouse.mouseClock.reset()
                prevButtonState = mouse.getPressed()  # if button is down already this ISN'T a new click
            
            # *chess_board* updates
            if chess_board.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                # keep track of start time/frame for later
                chess_board.frameNStart = frameN  # exact frame index
                chess_board.tStart = t  # local t and not account for scr refresh
                chess_board.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(chess_board, 'tStartRefresh')  # time at next scr refresh
                chess_board.setAutoDraw(True)
            # Run 'Each Frame' code from move_piece
            # Each Frame
            
            puzzle_time = puzzle_clock.getTime()
            global_time = global_clock.getTime()
            
            if timeout:
                timeout_time = timeout_clock.getTime()
                if timeout_time > 2:
                    continueRoutine = False
            elif puzzle_time > 30: # Puzzle timeout
                feedback_text = "Out of time"
                chess_feedback.text = feedback_text
                chess_feedback.color = incorrect_color
                
                timeout_clock.reset()
                timeout = True
                thisChess_trial["max_time"] = 1
                
            elif global_time > 180: # Block timeout
                feedback_text = "Out of time:\nBlock over"
                chess_feedback.text = feedback_text
                chess_feedback.color = "black"
                
                timeout_clock.reset()
                timeout = True
                thisChess_trial["max_time"] = 1
                chess_trials.finished = True
            
            # Update clock displays
            puzzle_timer.text = time.strftime('%M:%S', time.gmtime(30 - puzzle_time))
            global_timer.text = time.strftime('%M:%S', time.gmtime(global_time))
            
            # Code executed if a piece is crrently being
            # moved by the computer
            if moving_piece is not None:
                time_elapsed = move_clock.getTime()
                moving_piece, move_finished = move_piece(time_elapsed, moving_piece, start_coord, end_coord, move_time)
                if move_finished:
                    
                    # Check for castling
                        # if piece is king or rook
                            # and target is rook or king of same colour
                                # swap places
                    
                    piece_taken = evaluate_move(board_state, enemy_pieces, player_pieces, end_coord)
                           
                    if end_coord[0] < 9: # Not moving piece off board
                        
                        move, castling_king, castling_queen, en_passant = check_uci_move(board_lib, start_coord, end_coord)
                        if not is_castling_move:
                            board_lib.push(move)
                        
                        # En passant
                        if en_passant:
                            piece_taken = make_en_passant_move(moving_piece, white_pieces, black_pieces, board_state, end_coord)
                        
                        # Castling
                        if castling_king or castling_queen:
                            pieces = []
                            if enemy_move:
                                pieces = enemy_pieces
                            else:
                                pieces = player_pieces
                            moving_piece, start_coord, end_coord = try_castling_move(castling_king, castling_queen, pieces, player_color)
                            is_castling_move = True
                        else:
                            is_castling_move = False
                            
                        # Pawn promotion
                        try_pawn_promotion(moving_piece, end_coord)
                       
                    # Update custom board state representation
                    board_state = update_board_state(board_state, start_coord, end_coord, moving_piece.name)
                    
                    # Reset clock
                    move_clock.reset()
                    
                    if enemy_move:
                        move_num = move_num + 1
                        enemy_move = False
                        
                    if piece_taken:
                        take_coord = find_empty_take_square(board_state) # Create function to get empty coord
                        moving_piece, start_coord, end_coord = begin_move(piece_taken, end_coord, take_coord)
                    else:
                        moving_piece = None
            
            # Check mouse click cooldown
            cooldown = mouse_clock.getTime() < 0.1
            
            if not timeout:
                # Check for piece selection
                if clicked_piece is None and moving_piece is None:
                    for piece in player_pieces:                # for each pic
                        if not cooldown and mouse.isPressedIn(piece, buttons=[0]):    # If the picture is currently click
                            clicked_piece = piece
                            player_move_start = pos_to_coord(clicked_piece.pos)
                            mouse_clock.reset()
                            
                            # Look for legal moves
                            possible_moves = scan_legal_moves(board_lib, clicked_piece)
                            valid_move_highlights = draw_possible_moves(possible_moves)
                            
                # Check for piece placement
                elif clicked_piece is not None:
                    clicked_piece.pos = mouse.getPos()
                    
                    if not cooldown and mouse.isPressedIn(clicked_piece, buttons=[0]):
                        snapped_coord = pos_to_coord(mouse.getPos())
                        
                        # See if move is a redeposit
                        redeposit = False
                        if snapped_coord == player_move_start:
                            redeposit = True
                        
                        valid_move = check_valid_move(board_state, player_pieces, snapped_coord, possible_moves)
                        
                        if redeposit:
                            clicked_piece.pos = coord_to_pos(snapped_coord)
                            clicked_piece = None
                            clear_pieces(valid_move_highlights)
            
                        elif valid_move:
                    
                            clicked_piece.pos = coord_to_pos(snapped_coord)
                            piece_taken = evaluate_move(board_state, enemy_pieces, player_pieces, snapped_coord)
                            
                            clear_pieces(valid_move_highlights)
                            
                            # Reset clock
                            move_clock.reset()
                                            
                            if snapped_coord[0] < 9: # Not moving piece off board
                                
                                move, castling_king, castling_queen, en_passant = check_uci_move(board_lib, player_move_start, snapped_coord)
                                if not is_castling_move:
                                    board_lib.push(move)
                                    
                                # En passant
                                if en_passant:
                                    piece_taken = make_en_passant_move(clicked_piece, white_pieces, black_pieces, board_state, snapped_coord)
                                
                                # Castling
                                if castling_king or castling_queen:
                                    moving_piece, start_coord, end_coord = try_castling_move(castling_king, castling_queen, player_pieces, player_color)
                                    is_castling_move = True
                                else:
                                    is_castling_move = False
                                    
                                # Pawn promotion
                                try_pawn_promotion(clicked_piece, snapped_coord)
                                
                            board_state = update_board_state(board_state, player_move_start, snapped_coord, clicked_piece.name)
            
                            if piece_taken:
                                take_coord = find_empty_take_square(board_state)
                                moving_piece, start_coord, end_coord = begin_move(piece_taken, snapped_coord, take_coord)
                                
                            clicked_piece = None
                            
                            # Check for correct move or end of puzzle
                            correct_move = check_correct_move(move_num, moves, player_move_start, snapped_coord)
                            
                           
                            if (correct_move == False) or (move_num == len(moves) - 1):
                                feedback_text = "Correct" if correct_move else "Incorrect"
                                chess_feedback.text = feedback_text
                                if correct_move:
                                    chess_feedback.color = correct_color
                                else:
                                    chess_feedback.color = incorrect_color
                                    
                                timeout_clock.reset()
                                timeout = True
                                
                            else:
                                clear_pieces(highlight_squares)
                                move_num = move_num + 1
                                enemy_move = True
                                
                        mouse_clock.reset()
                        
                if enemy_move and (moving_piece is None):
                    moving_piece, start_coord, end_coord, highlight_squares = start_enemy_move(moves, move_num, board_state, enemy_pieces)
                
            
            
            # *chess_feedback* updates
            if chess_feedback.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                chess_feedback.frameNStart = frameN  # exact frame index
                chess_feedback.tStart = t  # local t and not account for scr refresh
                chess_feedback.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(chess_feedback, 'tStartRefresh')  # time at next scr refresh
                chess_feedback.setAutoDraw(True)
            
            # *puzzle_timer* updates
            if puzzle_timer.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                puzzle_timer.frameNStart = frameN  # exact frame index
                puzzle_timer.tStart = t  # local t and not account for scr refresh
                puzzle_timer.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(puzzle_timer, 'tStartRefresh')  # time at next scr refresh
                puzzle_timer.setAutoDraw(True)
            
            # *global_timer* updates
            if global_timer.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                global_timer.frameNStart = frameN  # exact frame index
                global_timer.tStart = t  # local t and not account for scr refresh
                global_timer.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(global_timer, 'tStartRefresh')  # time at next scr refresh
                global_timer.setAutoDraw(True)
            
            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in chess_puzzleComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "chess_puzzle" ---
        for thisComponent in chess_puzzleComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store data for chess_trials (TrialHandler)
        # Run 'End Routine' code from move_piece
        
        # Set trial data
        if feedback_text == "Correct":
            thisChess_trial["correct_answer"] = 1
        else:
            thisChess_trial["correct_answer"] = 0
            
        if thisChess_trial["timed_out"] is not 1:
            thisChess_trial["timed_out"] = 0
            
        
        clear_pieces(white_pieces)
        clear_pieces(black_pieces)
        clear_pieces(highlight_squares)
        clear_pieces(valid_move_highlights)
        
        win.flip()
        # the Routine "chess_puzzle" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()
        thisExp.nextEntry()
        
    # completed 1.0 repeats of 'chess_trials'
    
    thisExp.nextEntry()
    
# completed 1.0 repeats of 'chess_levels'


# --- Prepare to start Routine "instructions_two_back" ---
continueRoutine = True
routineForceEnded = False
# update component parameters for each repeat
press_to_continue.keys = []
press_to_continue.rt = []
_press_to_continue_allKeys = []
# keep track of which components have finished
instructions_two_backComponents = [text_2, press_to_continue]
for thisComponent in instructions_two_backComponents:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
frameN = -1

# --- Run Routine "instructions_two_back" ---
while continueRoutine:
    # get current time
    t = routineTimer.getTime()
    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *text_2* updates
    if text_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        text_2.frameNStart = frameN  # exact frame index
        text_2.tStart = t  # local t and not account for scr refresh
        text_2.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(text_2, 'tStartRefresh')  # time at next scr refresh
        text_2.setAutoDraw(True)
    
    # *press_to_continue* updates
    waitOnFlip = False
    if press_to_continue.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        press_to_continue.frameNStart = frameN  # exact frame index
        press_to_continue.tStart = t  # local t and not account for scr refresh
        press_to_continue.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(press_to_continue, 'tStartRefresh')  # time at next scr refresh
        press_to_continue.status = STARTED
        # keyboard checking is just starting
        waitOnFlip = True
        win.callOnFlip(press_to_continue.clock.reset)  # t=0 on next screen flip
        win.callOnFlip(press_to_continue.clearEvents, eventType='keyboard')  # clear events on next screen flip
    if press_to_continue.status == STARTED and not waitOnFlip:
        theseKeys = press_to_continue.getKeys(keyList=['space'], waitRelease=False)
        _press_to_continue_allKeys.extend(theseKeys)
        if len(_press_to_continue_allKeys):
            press_to_continue.keys = _press_to_continue_allKeys[-1].name  # just the last key pressed
            press_to_continue.rt = _press_to_continue_allKeys[-1].rt
            # a response ends the routine
            continueRoutine = False
    
    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        routineForceEnded = True
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in instructions_two_backComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# --- Ending Routine "instructions_two_back" ---
for thisComponent in instructions_two_backComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# the Routine "instructions_two_back" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

# set up handler to look after randomisation of conditions etc
trials_two_back = data.TrialHandler(nReps=5.0, method='sequential', 
    extraInfo=expInfo, originPath=-1,
    trialList=data.importConditions('conditions_twoback.tsv'),
    seed=None, name='trials_two_back')
thisExp.addLoop(trials_two_back)  # add the loop to the experiment
thisTrials_two_back = trials_two_back.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisTrials_two_back.rgb)
if thisTrials_two_back != None:
    for paramName in thisTrials_two_back:
        exec('{} = thisTrials_two_back[paramName]'.format(paramName))

for thisTrials_two_back in trials_two_back:
    currentLoop = trials_two_back
    # abbreviate parameter names if possible (e.g. rgb = thisTrials_two_back.rgb)
    if thisTrials_two_back != None:
        for paramName in thisTrials_two_back:
            exec('{} = thisTrials_two_back[paramName]'.format(paramName))
    
    # --- Prepare to start Routine "two_back" ---
    continueRoutine = True
    routineForceEnded = False
    # update component parameters for each repeat
    letter.setText(thisLetter)
    key_resp.keys = []
    key_resp.rt = []
    _key_resp_allKeys = []
    # keep track of which components have finished
    two_backComponents = [fixation, letter, key_resp]
    for thisComponent in two_backComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "two_back" ---
    while continueRoutine and routineTimer.getTime() < 1.5:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *fixation* updates
        if fixation.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            fixation.frameNStart = frameN  # exact frame index
            fixation.tStart = t  # local t and not account for scr refresh
            fixation.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(fixation, 'tStartRefresh')  # time at next scr refresh
            fixation.setAutoDraw(True)
        if fixation.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > fixation.tStartRefresh + 0.5-frameTolerance:
                # keep track of stop time/frame for later
                fixation.tStop = t  # not accounting for scr refresh
                fixation.frameNStop = frameN  # exact frame index
                fixation.setAutoDraw(False)
        
        # *letter* updates
        if letter.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
            # keep track of start time/frame for later
            letter.frameNStart = frameN  # exact frame index
            letter.tStart = t  # local t and not account for scr refresh
            letter.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(letter, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'letter.started')
            letter.setAutoDraw(True)
        if letter.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > letter.tStartRefresh + 0.5-frameTolerance:
                # keep track of stop time/frame for later
                letter.tStop = t  # not accounting for scr refresh
                letter.frameNStop = frameN  # exact frame index
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'letter.stopped')
                letter.setAutoDraw(False)
        
        # *key_resp* updates
        waitOnFlip = False
        if key_resp.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
            # keep track of start time/frame for later
            key_resp.frameNStart = frameN  # exact frame index
            key_resp.tStart = t  # local t and not account for scr refresh
            key_resp.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'key_resp.started')
            key_resp.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > key_resp.tStartRefresh + 1-frameTolerance:
                # keep track of stop time/frame for later
                key_resp.tStop = t  # not accounting for scr refresh
                key_resp.frameNStop = frameN  # exact frame index
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'key_resp.stopped')
                key_resp.status = FINISHED
        if key_resp.status == STARTED and not waitOnFlip:
            theseKeys = key_resp.getKeys(keyList=['y','n','left','right','space'], waitRelease=False)
            _key_resp_allKeys.extend(theseKeys)
            if len(_key_resp_allKeys):
                key_resp.keys = _key_resp_allKeys[-1].name  # just the last key pressed
                key_resp.rt = _key_resp_allKeys[-1].rt
                # was this correct?
                if (key_resp.keys == str(corrAns)) or (key_resp.keys == corrAns):
                    key_resp.corr = 1
                else:
                    key_resp.corr = 0
        
        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in two_backComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "two_back" ---
    for thisComponent in two_backComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # check responses
    if key_resp.keys in ['', [], None]:  # No response was made
        key_resp.keys = None
        # was no response the correct answer?!
        if str(corrAns).lower() == 'none':
           key_resp.corr = 1;  # correct non-response
        else:
           key_resp.corr = 0;  # failed to respond (incorrectly)
    # store data for trials_two_back (TrialHandler)
    trials_two_back.addData('key_resp.keys',key_resp.keys)
    trials_two_back.addData('key_resp.corr', key_resp.corr)
    if key_resp.keys != None:  # we had a response
        trials_two_back.addData('key_resp.rt', key_resp.rt)
    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
    if routineForceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-1.500000)
    thisExp.nextEntry()
    
# completed 5.0 repeats of 'trials_two_back'


# --- End experiment ---
# Flip one final time so any remaining win.callOnFlip() 
# and win.timeOnFlip() tasks get executed before quitting
win.flip()

# these shouldn't be strictly necessary (should auto-save)
thisExp.saveAsWideText(filename+'.csv', delim='auto')
thisExp.saveAsPickle(filename)
logging.flush()
# make sure everything is closed down
if eyetracker:
    eyetracker.setConnectionState(False)
thisExp.abort()  # or data files will save again on exit
win.close()
core.quit()
