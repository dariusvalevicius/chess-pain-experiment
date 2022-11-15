#Jérôme Genzling, McGill University
import pandas as pd
import random

elo_player = int(input('Please enter the elo of the player: \n'))

min_flow_elo, max_flow_elo = elo_player-50,elo_player+50
min_hard_elo, max_hard_elo = elo_player+550,elo_player+650

puzzles = pd.read_csv('subset_lichess.csv')

subset_flow = puzzles[(puzzles['Rating'] < max_flow_elo) & (puzzles['Rating'] > min_flow_elo)]
subset_flow_clean = subset_flow[['PuzzleId', 'FEN', 'Moves', 'Rating']]
if elo_player >= 2200:
    subset_hard = puzzles[puzzles['Rating'] > 2700]
else:
    subset_hard = puzzles[(puzzles['Rating'] < max_hard_elo) & (puzzles['Rating'] > min_hard_elo)]
subset_hard_clean = subset_hard[['PuzzleId', 'FEN', 'Moves', 'Rating']]

def pick_a_puzzle(subset):
    nb_puzzles = len(subset)
    pick = random.randint(1,nb_puzzles)
    puzzle = subset.iloc[pick-1]
    subset = subset.drop(subset.index[[pick-1]])
    print(pick)
    return puzzle,subset


