import os
import math
import pandas as pd
from pgmpy.estimators import BayesianEstimator
from pgmpy.models import BayesianModel
from functools import reduce
import matplotlib.pyplot as plt
from utils import read_csv
import scipy.stats as st


def score_strategies(search_strategy):
    best_model = search_strategy.estimate()
    print(best_model.edges())

    print("\nAll DAGs by Score: ")
    for score, dag in reversed(search_strategy.all_scores()):
        pass
        # print(score, dag.edges())


def isNaN(num):
    return num != num


def orientation(df, pos):
    if df['Category'] == df['Left_categ'] and pos == "left":
        return df['Category']
    elif df['Category'] == df['Right_categ'] and pos == "right":
        return df['Category']
    else:
        return 'Nothing'


def swap(df, pos):
    if df['Left_categ'] < df['Right_categ'] and pos == "left":
        return df['Left_categ']
    elif df['Left_categ'] > df['Right_categ'] and pos == "left":
        return df['Right_categ']
    elif df['Left_categ'] < df['Right_categ'] and pos == "right":
        return df['Right_categ']
    elif df['Left_categ'] > df['Right_categ'] and pos == "right":
        return df['Left_categ']


# define a Custom aggregation
# function for finding total
def total(series):
      return reduce(lambda x, y: x + y, series)


# get all the files and data in one data frame
all_files = os.listdir("cvs/")
cols = {'Left categ': "Left_categ", 'Right categ': "Right_categ"}
frames = []
for i in all_files:
    frames.append(pd.read_csv('cvs/'+i, sep=","))
result = pd.concat(frames, sort=True)

# removes row seperators -> headings
result = result[(result.Monkey != 'Monkey') & (result.Date != 'Date')]

# read the gender of each monkey
dic = read_csv('mky-gender.csv')

# IDs of monkeys converted to string.
result['Monkey'] = result['Monkey'].astype(str)

# added a gender column for the dataframe
result['gender'] = result['Monkey'].map(dic)

# Renamed dataframe columns to remove white spaces
# remove NaN from Category -> This where monkey made no choice
# Some rows had the values shifted to the right, so I had to \
# fill the appropriate columns using the prefix of the picture.
# ps: the prefix of the picture gives an indication of its category.
# Did this for Left Category and Right Category
result = result.rename(columns=cols)
result = result[['Monkey', 'gender', 'Left_categ', 'Right_categ', 'Category']]
# result = result[result['Category'].notna()]

result.loc[result['Left_categ'].str.startswith("AFF"), 'Left_categ'] = "Affiliative"
result.loc[result['Left_categ'].str.startswith("NAT"), 'Left_categ'] = "Nature"
result.loc[result['Left_categ'].str.startswith("FRT"), 'Left_categ'] = "Fruit"
result.loc[result['Left_categ'].str.startswith("CYN"), 'Left_categ'] = "Cynomolgus"
result.loc[result['Left_categ'].str.startswith("LAB"), 'Left_categ'] = "Lab"
result.loc[result['Left_categ'].str.startswith("AGG"), 'Left_categ'] = "Aggressive"

result.loc[result['Right_categ'].str.startswith("AFF"), 'Right_categ'] = "Affiliative"
result.loc[result['Right_categ'].str.startswith("NAT"), 'Right_categ'] = "Nature"
result.loc[result['Right_categ'].str.startswith("FRT"), 'Right_categ'] = "Fruit"
result.loc[result['Right_categ'].str.startswith("CYN"), 'Right_categ'] = "Cynomolgus"
result.loc[result['Right_categ'].str.startswith("LAB"), 'Right_categ'] = "Lab"
result.loc[result['Right_categ'].str.startswith("AGG"), 'Right_categ'] = "Aggressive"

print(result)
exit()

result['Condition_One'] = result.apply(swap, pos="left",  axis=1)
result['Condition_Two'] = result.apply(swap, pos="right",  axis=1)

# Concatenate left and right
result['Condition'] = result[['Condition_One', 'Condition_Two']].apply(lambda x: '_'.join(x), axis=1)

# result = result.drop(columns=['Left_categ', 'Right_categ', 'Condition_One', 'Condition_Two'])
result = result[['Monkey', 'gender', 'Condition', 'Category']]


monkey_df = result[['Monkey', 'Condition', 'Category']]
monkeys = list(set(monkey_df.Monkey))


gender_df = result[['gender', 'Condition', 'Category']]
genders = list(set(gender_df.gender))


