#Jérôme Genzling, McGill University
import pandas as pd
import random

def create_subset(elo_player,participant_id):

    min_flow_elo, max_flow_elo = elo_player-150,elo_player-50
    min_hard_elo, max_hard_elo = elo_player+550,elo_player+650

    puzzles = pd.read_csv('subset_lichess.csv')
    easy_puzzles = pd.read_csv('Final_Easy_set.csv')

    subset_flow = puzzles[(puzzles['Rating'] < max_flow_elo) & (puzzles['Rating'] > min_flow_elo)]
    subset_flow_clean = subset_flow[['PuzzleId', 'FEN', 'Moves', 'Rating']]
    if elo_player >= 2200:
        subset_hard = puzzles[puzzles['Rating'] > 2700]
    else:
        subset_hard = puzzles[(puzzles['Rating'] < max_hard_elo) & (puzzles['Rating'] > min_hard_elo)]
    subset_hard_clean = subset_hard[['PuzzleId', 'FEN', 'Moves', 'Rating']]

    easy_puzzles.to_csv(str(participant_id) + '_easy_set.tsv', sep='\t', index=False)
    subset_flow_clean.to_csv(str(participant_id) + '_flow_set.tsv', sep='\t', index=False)
    subset_hard_clean.to_csv(str(participant_id) + '_hard_set.tsv', sep='\t', index=False)

    return easy_puzzles, subset_flow_clean, subset_hard_clean

def pick_a_puzzle(subset):
    nb_puzzles = len(subset)
    pick = random.randint(1,nb_puzzles)
    puzzle = subset.iloc[pick-1]
    subset = subset.drop(subset.index[[pick-1]])
    print(pick)
    return puzzle,subset



