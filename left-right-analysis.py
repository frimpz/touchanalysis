import os
import pickle

import pandas as pd
from pgmpy.estimators import BayesianEstimator
from pgmpy.models import BayesianModel
from functools import reduce
from plots import create_boxplots
import matplotlib.pyplot as plt
from utils import read_csv


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
    elif df['Category'] == df['Left_categ'] and pos == "both":
        return 'left'
    elif df['Category'] == df['Right_categ'] and pos == "both":
        return 'right'
    else:
        return 'Nothing'


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
result = result[result['Category'].notna()]

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

# Created two new columns left_select and right_select
# Left_Select -> category on the left selected by monkey
# Right Select -> Category on the  right selected by Monkey
# Used to show the monkeys overall preference for left and right categories.
# If monkey did't select we replace with Nothing; later filtered out.
# Uses the function orientation defined above.

# result['left_select'] = result.apply(orientation, pos="left",  axis=1)
# result['right_select'] = result.apply(orientation, pos="right",  axis=1)
result['orientation'] = result.apply(orientation, pos="both",  axis=1)


gender_df = result[['gender', 'Left_categ', 'Right_categ', 'orientation']]
genders = list(set((gender_df.gender)))
categories = ['Affiliative', 'Aggressive', 'Cynomolgus', 'Fruit',  'Lab', 'Nature']
model = BayesianModel([('Left_categ', 'orientation'), ('Right_categ', 'orientation')])


data_files = {}
temp = [['gender', 'Left-Category', 'Right-Category', 'orientation', 'Count', 'Probability']]
for gender in genders:
    df = (gender_df[(gender_df.gender == gender)])
    z = BayesianEstimator(model, df)

    cat_cpd = z.estimate_cpd('orientation', prior_type="bdeu", equivalent_sample_size=6)  # .to_factor()
    for left in categories:
        for right in categories:
            for cat in ['left', 'right']:
                try:
                    count = z.state_counts('orientation')[left][right][cat]
                    prob = cat_cpd.get_value(
                        **{'Left_categ': left, 'Right_categ': right, 'orientation': cat})
                    if not isNaN(prob) and prob > 0:
                        temp.append([gender, left, right, cat, count, prob])
                    else:
                        temp.append([gender, left, right, cat, count, prob])
                except KeyError:
                    pass
                        #temp.append([gender, left, right, cat, count, 0])
#
prob_df = pd.DataFrame.from_records(temp[1:], columns=temp[0])

print(prob_df)

gen_df = prob_df[['gender', 'Left-Category', 'Right-Category', 'orientation', 'Count']].\
    groupby(['gender', 'Left-Category', 'Right-Category', 'orientation'])['Count'].agg(['sum'])# .reset_index()
# boxplot = gen_df.boxplot(rot=45, fontsize=12, figsize=(8, 10))
print(gen_df)
#
group = ['gender', 'orientation']
ax, bp = gen_df.boxplot(rot=90, fontsize=12, figsize=(12, 10), column=['sum'], by=group, return_type="both")[0]
plt.title("Box plot grouped by : " + str(group))
plt.suptitle('')
plt.ylabel("sum")


plt.show()