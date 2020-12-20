import os
import pickle

import pandas as pd
from pgmpy.estimators import ParameterEstimator, ExhaustiveSearch, BDeuScore, K2Score, BicScore, HillClimbSearch, \
    MmhcEstimator, MaximumLikelihoodEstimator, BayesianEstimator
from pgmpy.models import BayesianModel

from utils import read_csv



# No Joint Probability

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

cat_result = result[(result['Category'] != 'Nothing')]
lft_result = result[(result['left_select'] != 'Nothing')]
rgt_result = result[(result['right_select'] != 'Nothing')]


# print(result.head(10))


# print(result.groupby(['Monkey', 'right_select']).size())
result = result.groupby(['gender', 'Category']).size()
writer = pd.ExcelWriter("overall.xlsx")
result.to_excel(writer, sheet_name='Distribution')
writer.save()

# print(result.shape)

# print(result.head(30))

# temp = result[['Monkey', 'gender']].drop_duplicates(subset=['Monkey', 'gender'])
# print(temp[['Monkey', 'gender']])

# score_strategies(ExhaustiveSearch(result, scoring_method=BicScore(data=result)))

# model = BayesianModel([('Left categ', 'Category'), ('Right categ', 'Category', ),
#                        ('Monkey', 'gender'), ('gender', 'Category'),
#                        ('Monkey', 'left_select'), ('Monkey', 'right_select')
#                        ])



# Number 1 get preffered category left/right
def prefference(model, item, item_name, column_names, file_name):

    cat_est = BayesianEstimator(model, cat_result)
    lft_est = BayesianEstimator(model, lft_result)
    rgt_est = BayesianEstimator(model, rgt_result)

    cat_cpd = cat_est.estimate_cpd('Category', prior_type="BDeu", equivalent_sample_size=6).to_factor()
    lft_cpd = lft_est.estimate_cpd('left_select', prior_type="BDeu", equivalent_sample_size=6).to_factor()
    rgt_cpd = rgt_est.estimate_cpd('right_select', prior_type="BDeu", equivalent_sample_size=6).to_factor()

    cat_df = pd.DataFrame()
    lft_df = pd.DataFrame()
    rgt_df = pd.DataFrame()

    cat = {}
    lft = {}
    rgt = {}

    for i in item:
        cat[item_name] = i
        lft[item_name] = i
        rgt[item_name] = i

        cat_max = 0
        lft_max = 0
        rgt_max = 0

        for j in column_names[4:]:

            cat_temp = cat_cpd.get_value(**{'Category': j, item_name: i})
            cat[j] = cat_temp
            if cat_temp > cat_max:
                cat_max = cat_temp
                cat['Preffered_Category'] = j

            lft_temp = lft_cpd.get_value(**{'left_select': j, item_name: i})
            lft[j] = lft_temp
            if lft_temp > lft_max:
                lft_max = lft_temp
                lft['Preffered_Left'] = j

            rgt_temp = rgt_cpd.get_value(**{'right_select': j, item_name: i})
            rgt[j] = rgt_temp
            if rgt_temp > rgt_max:
                rgt_max = rgt_temp
                rgt['Preffered_Right'] = j

        cat_df = cat_df.append(cat, ignore_index=True)
        lft_df = lft_df.append(lft, ignore_index=True)
        rgt_df = rgt_df.append(rgt, ignore_index=True)

    cat_df = cat_df.reindex(columns=column_names[0:2]+column_names[4:])
    lft_df = lft_df.reindex(columns=column_names[0:1]+column_names[2:3]+column_names[4:])
    rgt_df = rgt_df.reindex(columns=column_names[0:1]+column_names[3:])


    writer = pd.ExcelWriter(file_name)
    cat_df.to_excel(writer, sheet_name='Overall Category')
    lft_df.to_excel(writer, sheet_name='Left Category')
    rgt_df.to_excel(writer, sheet_name='Right Category')
    writer.save()
    return


# No Joint probability
# 1 - 3
model = BayesianModel([('Monkey', 'Category'),
                       ('Monkey', 'left_select'),
                       ('Monkey', 'right_select')])
monkeys = list(dic.keys())
# Columns start from 2 to end
column_names = ["Monkey", "Preffered_Category", 'Preffered_Left',
                'Preffered_Right', "Affiliative", "Nature",
                "Fruit", "Cynomolgus", "Lab", "Aggressive"]
# print(column_names[4:])
file_name = "monkey_pref.xlsx"
prefference(model, monkeys, "Monkey", column_names, file_name)

# 4 - 6
model = BayesianModel([('gender', 'Category'),
                       ('gender', 'left_select'),
                       ('gender', 'right_select')])
genders = ['M', 'F']
column_names = ["gender", "Preffered_Category", 'Preffered_Left',
                'Preffered_Right', "Affiliative", "Nature",
                "Fruit", "Cynomolgus", "Lab", "Aggressive"]
file_name = "gender_pref.xlsx"
prefference(model, genders, "gender", column_names, file_name)

