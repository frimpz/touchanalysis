import os
import pickle

import pandas as pd
from pgmpy.estimators import ParameterEstimator, ExhaustiveSearch, BDeuScore, K2Score, BicScore, HillClimbSearch, \
    MmhcEstimator, MaximumLikelihoodEstimator, BayesianEstimator
from pgmpy.models import BayesianModel

from plots import create_boxplots
from utils import read_csv

def score_strategies(search_strategy):
    best_model = search_strategy.estimate()
    print(best_model.edges())

    print("\nAll DAGs by Score: ")
    for score, dag in reversed(search_strategy.all_scores()):
        pass
        # print(score, dag.edges())


def orientation(df, pos):
    if df['Category'] == df['Left_categ'] and pos == "left":
        return df['Category']
    elif df['Category'] == df['Right_categ'] and pos == "right":
        return df['Category']
    else:
        return "Nothing"


all_files = os.listdir("cvs/")

cols = {'Left categ': "Left_categ", 'Right categ': "Right_categ"}
frames = []
for i in all_files:
    frames.append(pd.read_csv('cvs/'+i, sep=","))

result = pd.concat(frames, sort=True)
result = result[(result.Monkey != 'Monkey') & (result.Date != 'Date')]

dic = read_csv('mky-gender.csv')

result['Monkey'] = result['Monkey'].astype(str)
result['gender'] = result['Monkey'].map(dic)

result = result.rename(columns=cols)
result = result[['Monkey', 'gender', 'Left_categ', 'Right_categ', 'Category']]
result = result[result['Left_categ'].notna()]
result = result[result['Right_categ'].notna()]
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

result = result[(result['Left_categ'] != '.') & (result['Right_categ'] != '.')]
result.Category = result.Category.fillna('Nothing')


result['left_select'] = result.apply(orientation, pos="left",  axis=1)
result['right_select'] = result.apply(orientation, pos="right",  axis=1)

# cat_result = result[(result['Category'] != 'Nothing')]
cat_result = result
lft_result = result[(result['left_select'] != 'Nothing')]
rgt_result = result[(result['right_select'] != 'Nothing')]


# print(result.head(10))
#
#
# print(result.groupby(['Monkey', 'right_select']).size())
# print(result.groupby(['gender', 'Category']).size())

#
# model = BayesianModel([('Monkey', 'Category')])
# pe = ParameterEstimator(model, result)
# x = pe.state_counts('Category')#['Monkey'].to_list()
# # print(x)
#
# model = BayesianModel([('Monkey', 'Category')])
# pe = ParameterEstimator(model, cat_result)
# y = pe.state_counts('Category')#['Monkey'].to_list()
# print(y)
# cat_result = cat_result[(cat_result['Monkey'].isin(['29928']))]
#E , '29987'
# print(cat_result)

categories = ['Nature', 'Affiliative', 'Aggressive', 'Cynomolgus', 'Fruit',  'Lab']
model = BayesianModel([('Monkey', 'Category'), ('Left_categ', 'Category'), ('Right_categ', 'Category')])
z = BayesianEstimator(model, cat_result)

# with pd.option_context("display.max_rows", 1000, "display.max_columns", 5000):
#     print(z.state_counts('Category'))
cat_cpd = z.estimate_cpd('Category', prior_type="BDeu", equivalent_sample_size=6).to_factor()
print(type(cat_cpd))

monkeys = list(dic.keys())
data_files = {}
for monkey in monkeys:
    for left in categories:
        for right in categories:
            key = left+"-"+right
            if key not in data_files:
                data_files[key] = {}
            data_files[key]['left'] = left
            data_files[key]['right'] = right
            for category in categories:
                cat_temp = cat_cpd.get_value(**{'Monkey': monkey, 'Left_categ': left, 'Right_categ': right, 'Category': category})
                if category in data_files[key]:
                    data_files[key][category].append(cat_temp)
                else:
                    data_files[key][category] = [cat_temp]


graphs = list(data_files.keys())
indicies = [(0, 6), (6, 12), (12, 18), (18, 24), (24, 30), (30, 36)]

for x in indicies:
    print(x[0], x[1])
    for i in graphs[x[0]:x[1]]:
        data = {}
        title = "Boxplot for Monkeys Left Category: "
        for j in data_files[i]:
            if j == 'left':
                title = title + data_files[i][j] + " --- Right Category: "
            elif j == 'right':
                title = title + data_files[i][j] + " "
            else:
                data[j] = data_files[i][j]

    # create_boxplots(data=data, title=title)

