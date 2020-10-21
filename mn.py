import os
import pickle

import pandas as pd
from pgmpy.estimators import ParameterEstimator, ExhaustiveSearch, BDeuScore, K2Score, BicScore, HillClimbSearch, \
    MmhcEstimator, MaximumLikelihoodEstimator, BayesianEstimator
from pgmpy.models import BayesianModel

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


print(result.groupby(['Monkey', 'Category']).size())

# print(result.head(30))

# temp = result[['Monkey', 'gender']].drop_duplicates(subset=['Monkey', 'gender'])
# print(temp[['Monkey', 'gender']])

# score_strategies(ExhaustiveSearch(result, scoring_method=BicScore(data=result)))

model = BayesianModel([('Monkey', 'Category'), ('Left_categ', 'Category'), ('Right_categ', 'Category'),
                       ('Monkey', 'left_select'), ('Left_categ', 'left_select'), ('Right_categ', 'left_select'),
                       ('Monkey', 'right_select'), ('Left_categ', 'right_select'), ('Right_categ', 'right_select')])

est = BayesianEstimator(model, result)


cat_cpd = est.estimate_cpd('Category', prior_type="BDeu", equivalent_sample_size=0).to_factor()
lft_cpd = est.estimate_cpd('left_select', prior_type="BDeu", equivalent_sample_size=0).to_factor()
rgt_cpd = est.estimate_cpd('right_select', prior_type="BDeu", equivalent_sample_size=0).to_factor()

map = {"Category": "Nature", "Left_categ": "Nature", "Monkey": "35551", "Right_categ": "Nature"}
categories = ["Affiliative", "Nature", "Fruit", "Cynomolgus", "Lab", "Aggressive"]

# Number 1 get preffered category left/right
def monkey_prefference():
    df = pd.DataFrame(columns=("Monkey", "Preffered_Category", "Preffered_Left", "Preffered_Right"))
    monkeys = list(dic.keys())
    mky = {}
    for i in monkeys:
        mky['Monkey'] = i
        mky['Preffered_Category'] = "Nothing"
        mky['Preffered_Left'] = "Nothing"
        mky['Preffered_Right'] = "Nothing"
        cat_max = 0
        lft_max = 0
        rgt_max = 0
        for j in categories:
            for k in categories:
                for l in categories:
                    cat_temp = cat_cpd.get_value(Category=j, Left_categ=k, Monkey=i,
                                                 Right_categ=l)
                    lft_temp = lft_cpd.get_value(left_select=j, Left_categ=k, Monkey=i,
                                                 Right_categ=l)
                    rgt_temp = rgt_cpd.get_value(right_select=j, Left_categ=k, Monkey=i,
                                                 Right_categ=l)
                    if cat_temp > cat_max:
                        cat_max = cat_temp
                        mky['Preffered_Category'] = j

                    if lft_temp > lft_max:
                        lft_max = lft_temp
                        mky['Preffered_Left'] = k

                    if rgt_temp > rgt_max:
                        rgt_max = rgt_temp
                        mky['Preffered_Right'] = l
        df = df.append(mky, ignore_index=True)
    return df

# monkey_prefference(map)

# model.fit(result, estimator=BayesianEstimator, prior_type="BDeu", equivalent_sample_size=6)
# for cpd in model.get_cpds():
#     print(cpd)
#
#
est = BayesianEstimator(model, result)
# print(est.estimate_cpd('Category', prior_type='BDeu', equivalent_sample_size=6))

print(monkey_prefference())

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print("\n", pe.estimate_cpd('Category'))