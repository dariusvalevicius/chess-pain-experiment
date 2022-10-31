#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2022.2.4),
    on October 31, 2022, at 12:35
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

# Run 'Before Experiment' code from move_piece
import time

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
        lineWidth=1.0,     colorSpace='rgb',  lineColor=[0, 0, 0], fillColor=[255/256, 87/256, 51/256],
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
    print(target_square)
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
    
    for row in board_state:
        print(row)
    return board_state
        
def clear_pieces(pieces):
    for piece in pieces:
        piece.setAutoDraw(False)
#        piece._unload()

# Could combine this function with evaluate_move():
def check_valid_move(board_state, player_pieces, coord):
    '''See if player move is valid'''
    target_square_content = board_state[coord[1]][coord[0]]
    if coord[0] < 1 or coord[0] > 8 or coord[1] < 1 or coord[1] > 8:
        return False
    elif search_pieces(player_pieces, target_square_content):
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
            
   
   
feedback_text = ''   

# Data for piece codes and x axis labels
piece_codes = ["p", "n", "b", "r", "q", "k", "P", "N", "B", "R", "Q", "K"]

# Time it takes for a piece to move from A to B
# Could instead make it a speed parameter
move_time = 1

## Valid moves per piece
#p_moves = [[0,-1], [0,-2]]
#n_moves = [[-2,1], [-1,2], [1,2], [2,1], [2,-1], [1,-2], [-1,-2], [-2,-1]]
#b_moves = [["-inf","inf"], ["inf","inf"], ["inf","-inf"], ["-inf","-inf"]]
#r_moves = [["-inf",0], [0,"inf"], ["inf",0], [0,"-inf"]]
#q_moves = b_moves + r_moves
#k_moves = [[-1,0], [-1,1], [0,1], [1,1], [1,0], [1,-1], [0,-1], [-1,1]]

#P_moves = [[


# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
# Store info about the experiment session
psychopyVersion = '2022.2.4'
expName = 'chess_experiment'  # from the Builder filename that created this script
expInfo = {
    'participant': f"{randint(0, 999999):06.0f}",
    'session': '001',
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
    originPath='C:\\Users\\dariu\\Documents\\Roy Lab Freelance Work\\Chess Experiment\\chess-pain-experiment\\psychopy\\chess_experiment.py',
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

# --- Initialize components for Routine "instructions_chess_puzzle" ---
chess_instructions_1 = visual.TextStim(win=win, name='chess_instructions_1',
    text='Instructions slide\n\nComplete the chess puzzle',
    font='Open Sans',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
    color=[-1.0000, -1.0000, -1.0000], colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
next_routine_1 = keyboard.Keyboard()

# --- Initialize components for Routine "chess_puzzle" ---
fixation_chess = visual.TextStim(win=win, name='fixation_chess',
    text='+',
    font='Open Sans',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
mouse = event.Mouse(win=win)
x, y = [None, None]
mouse.mouseClock = core.Clock()
chess_board = visual.ImageStim(
    win=win,
    name='chess_board', 
    image='images/board.png', mask=None, anchor='center',
    ori=0.0, pos=(0, 0), size=(1, 1),
    color=[1,1,1], colorSpace='rgb', opacity=None,
    flipHoriz=False, flipVert=False,
    texRes=128.0, interpolate=True, depth=-2.0)
chess_feedback = visual.TextStim(win=win, name='chess_feedback',
    text=feedback_text,
    font='Open Sans',
    pos=(-1.2, 0), height=0.05, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=-4.0);

# --- Initialize components for Routine "feedback" ---
feedback_text_slide = visual.TextStim(win=win, name='feedback_text_slide',
    text=feedback_text,
    font='Open Sans',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);

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

# --- Prepare to start Routine "instructions_chess_puzzle" ---
continueRoutine = True
routineForceEnded = False
# update component parameters for each repeat
next_routine_1.keys = []
next_routine_1.rt = []
_next_routine_1_allKeys = []
# keep track of which components have finished
instructions_chess_puzzleComponents = [chess_instructions_1, next_routine_1]
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
    
    # *chess_instructions_1* updates
    if chess_instructions_1.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        chess_instructions_1.frameNStart = frameN  # exact frame index
        chess_instructions_1.tStart = t  # local t and not account for scr refresh
        chess_instructions_1.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(chess_instructions_1, 'tStartRefresh')  # time at next scr refresh
        # add timestamp to datafile
        thisExp.timestampOnFlip(win, 'chess_instructions_1.started')
        chess_instructions_1.setAutoDraw(True)
    
    # *next_routine_1* updates
    waitOnFlip = False
    if next_routine_1.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        next_routine_1.frameNStart = frameN  # exact frame index
        next_routine_1.tStart = t  # local t and not account for scr refresh
        next_routine_1.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(next_routine_1, 'tStartRefresh')  # time at next scr refresh
        # add timestamp to datafile
        thisExp.timestampOnFlip(win, 'next_routine_1.started')
        next_routine_1.status = STARTED
        # keyboard checking is just starting
        waitOnFlip = True
        win.callOnFlip(next_routine_1.clock.reset)  # t=0 on next screen flip
        win.callOnFlip(next_routine_1.clearEvents, eventType='keyboard')  # clear events on next screen flip
    if next_routine_1.status == STARTED and not waitOnFlip:
        theseKeys = next_routine_1.getKeys(keyList=['space'], waitRelease=False)
        _next_routine_1_allKeys.extend(theseKeys)
        if len(_next_routine_1_allKeys):
            next_routine_1.keys = _next_routine_1_allKeys[-1].name  # just the last key pressed
            next_routine_1.rt = _next_routine_1_allKeys[-1].rt
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
# check responses
if next_routine_1.keys in ['', [], None]:  # No response was made
    next_routine_1.keys = None
thisExp.addData('next_routine_1.keys',next_routine_1.keys)
if next_routine_1.keys != None:  # we had a response
    thisExp.addData('next_routine_1.rt', next_routine_1.rt)
thisExp.nextEntry()
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
    mouse.x = []
    mouse.y = []
    mouse.leftButton = []
    mouse.midButton = []
    mouse.rightButton = []
    mouse.time = []
    mouse.clicked_name = []
    gotValidClick = False  # until a click is received
    # Run 'Begin Routine' code from move_piece
    # Begin Routine
    
    # Initialize board state and piece arrays
    board_state = [['' for i in range(12)] for i in range(9)]
    white_pieces = []
    black_pieces = []
    
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
    
    # Identify player and enemy
    if fen[1] == "b":
        player_pieces = white_pieces
        enemy_pieces = black_pieces
    elif fen[1] == "w":
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
    correct_move = True
    
    
    
    
    
    # keep track of which components have finished
    chess_puzzleComponents = [fixation_chess, mouse, chess_board, chess_feedback]
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
        
        # *fixation_chess* updates
        if fixation_chess.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            fixation_chess.frameNStart = frameN  # exact frame index
            fixation_chess.tStart = t  # local t and not account for scr refresh
            fixation_chess.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(fixation_chess, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'fixation_chess.started')
            fixation_chess.setAutoDraw(True)
        if fixation_chess.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > fixation_chess.tStartRefresh + 0.5-frameTolerance:
                # keep track of stop time/frame for later
                fixation_chess.tStop = t  # not accounting for scr refresh
                fixation_chess.frameNStop = frameN  # exact frame index
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'fixation_chess.stopped')
                fixation_chess.setAutoDraw(False)
        # *mouse* updates
        if mouse.status == NOT_STARTED and t >= 0-frameTolerance:
            # keep track of start time/frame for later
            mouse.frameNStart = frameN  # exact frame index
            mouse.tStart = t  # local t and not account for scr refresh
            mouse.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(mouse, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.addData('mouse.started', t)
            mouse.status = STARTED
            mouse.mouseClock.reset()
            prevButtonState = mouse.getPressed()  # if button is down already this ISN'T a new click
        if mouse.status == STARTED:  # only update if started and not finished!
            buttons = mouse.getPressed()
            if buttons != prevButtonState:  # button state changed?
                prevButtonState = buttons
                if sum(buttons) > 0:  # state changed to a new click
                    # check if the mouse was inside our 'clickable' objects
                    gotValidClick = False
                    try:
                        iter(white_pieces)
                        clickableList = white_pieces
                    except:
                        clickableList = [white_pieces]
                    for obj in clickableList:
                        if obj.contains(mouse):
                            gotValidClick = True
                            mouse.clicked_name.append(obj.name)
                    x, y = mouse.getPos()
                    mouse.x.append(x)
                    mouse.y.append(y)
                    buttons = mouse.getPressed()
                    mouse.leftButton.append(buttons[0])
                    mouse.midButton.append(buttons[1])
                    mouse.rightButton.append(buttons[2])
                    mouse.time.append(mouse.mouseClock.getTime())
        
        # *chess_board* updates
        if chess_board.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
            # keep track of start time/frame for later
            chess_board.frameNStart = frameN  # exact frame index
            chess_board.tStart = t  # local t and not account for scr refresh
            chess_board.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(chess_board, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'chess_board.started')
            chess_board.setAutoDraw(True)
        # Run 'Each Frame' code from move_piece
        # Each Frame
        
        # Code executed if a piece is crrently being
        # moved by the computer
        if moving_piece is not None:
            time_elapsed = move_clock.getTime()
            moving_piece, move_finished = move_piece(time_elapsed, moving_piece, start_coord, end_coord, move_time)
            if move_finished:
                piece_taken = evaluate_move(board_state, enemy_pieces, player_pieces, end_coord)
                
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
        
        # Check for piece selection
        if clicked_piece is None and moving_piece is None:
            for piece in player_pieces:                # for each pic
                if not cooldown and mouse.isPressedIn(piece, buttons=[0]):    # If the picture is currently click
                    clicked_piece = piece
                    player_move_start = pos_to_coord(clicked_piece.pos)
                    mouse_clock.reset()
        # Check for piece placement
        elif clicked_piece is not None:
            clicked_piece.pos = mouse.getPos()
            
            if not cooldown and mouse.isPressedIn(clicked_piece, buttons=[0]):
                snapped_coord = pos_to_coord(mouse.getPos())
                
                # See if move is a redeposit
                redeposit = False
                if snapped_coord == player_move_start:
                    redeposit = True
                
                valid_move = check_valid_move(board_state, player_pieces, snapped_coord)
                
                if redeposit:
                    clicked_piece.pos = coord_to_pos(snapped_coord)
                elif valid_move:
            
                    clicked_piece.pos = coord_to_pos(snapped_coord)
                    piece_taken = evaluate_move(board_state, enemy_pieces, player_pieces, snapped_coord)
                    
                    # Reset clock
                    move_clock.reset()
                    
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
        
                        time.sleep(1)
        
                        continueRoutine = False
                    else:
                        clear_pieces(highlight_squares)
                        move_num = move_num + 1
                        enemy_move = True
                        
                mouse_clock.reset()
                
        if (enemy_move) and (moving_piece is None):
            moving_piece, start_coord, end_coord, highlight_squares = start_enemy_move(moves, move_num, board_state, enemy_pieces)
        
            
        
        
        
        # *chess_feedback* updates
        if chess_feedback.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            chess_feedback.frameNStart = frameN  # exact frame index
            chess_feedback.tStart = t  # local t and not account for scr refresh
            chess_feedback.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(chess_feedback, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'chess_feedback.started')
            chess_feedback.setAutoDraw(True)
        
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
    chess_trials.addData('mouse.x', mouse.x)
    chess_trials.addData('mouse.y', mouse.y)
    chess_trials.addData('mouse.leftButton', mouse.leftButton)
    chess_trials.addData('mouse.midButton', mouse.midButton)
    chess_trials.addData('mouse.rightButton', mouse.rightButton)
    chess_trials.addData('mouse.time', mouse.time)
    chess_trials.addData('mouse.clicked_name', mouse.clicked_name)
    # Run 'End Routine' code from move_piece
    
    clear_pieces(white_pieces)
    clear_pieces(black_pieces)
    clear_pieces(highlight_squares)
    
    win.flip()
    # the Routine "chess_puzzle" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # --- Prepare to start Routine "feedback" ---
    continueRoutine = True
    routineForceEnded = False
    # update component parameters for each repeat
    # keep track of which components have finished
    feedbackComponents = [feedback_text_slide]
    for thisComponent in feedbackComponents:
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
    
    # --- Run Routine "feedback" ---
    while continueRoutine and routineTimer.getTime() < 1.0:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *feedback_text_slide* updates
        if feedback_text_slide.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            feedback_text_slide.frameNStart = frameN  # exact frame index
            feedback_text_slide.tStart = t  # local t and not account for scr refresh
            feedback_text_slide.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(feedback_text_slide, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'feedback_text_slide.started')
            feedback_text_slide.setAutoDraw(True)
        if feedback_text_slide.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > feedback_text_slide.tStartRefresh + 1.0-frameTolerance:
                # keep track of stop time/frame for later
                feedback_text_slide.tStop = t  # not accounting for scr refresh
                feedback_text_slide.frameNStop = frameN  # exact frame index
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'feedback_text_slide.stopped')
                feedback_text_slide.setAutoDraw(False)
        
        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in feedbackComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "feedback" ---
    for thisComponent in feedbackComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
    if routineForceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-1.000000)
    thisExp.nextEntry()
    
# completed 1.0 repeats of 'chess_trials'


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
        # add timestamp to datafile
        thisExp.timestampOnFlip(win, 'text_2.started')
        text_2.setAutoDraw(True)
    
    # *press_to_continue* updates
    waitOnFlip = False
    if press_to_continue.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        press_to_continue.frameNStart = frameN  # exact frame index
        press_to_continue.tStart = t  # local t and not account for scr refresh
        press_to_continue.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(press_to_continue, 'tStartRefresh')  # time at next scr refresh
        # add timestamp to datafile
        thisExp.timestampOnFlip(win, 'press_to_continue.started')
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
# check responses
if press_to_continue.keys in ['', [], None]:  # No response was made
    press_to_continue.keys = None
thisExp.addData('press_to_continue.keys',press_to_continue.keys)
if press_to_continue.keys != None:  # we had a response
    thisExp.addData('press_to_continue.rt', press_to_continue.rt)
thisExp.nextEntry()
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
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'fixation.started')
            fixation.setAutoDraw(True)
        if fixation.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > fixation.tStartRefresh + 0.5-frameTolerance:
                # keep track of stop time/frame for later
                fixation.tStop = t  # not accounting for scr refresh
                fixation.frameNStop = frameN  # exact frame index
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'fixation.stopped')
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
