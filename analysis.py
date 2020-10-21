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

cat_result = result[(result['Category'] != 'Nothing')]
lft_result = result[(result['left_select'] != 'Nothing')]
rgt_result = result[(result['right_select'] != 'Nothing')]


print(result.head(10))


print(result.groupby(['Monkey', 'right_select']).size())
print(result.groupby(['gender', 'Category']).size())

print(result.shape)


model = BayesianModel([('Monkey', 'Category'), ('Left_categ', 'Category'), ('Right_categ', 'Category')])
monkeys = list(dic.keys())
# Columns start from 2 to end
column_names = ["Monkey", "Left_categ", "Right_categ", "Preffered_Category", 'Preffered_Left',
                'Preffered_Right', "Affiliative", "Nature", "Fruit", "Cynomolgus", "Lab", "Aggressive"]
file_name = "joint_monkey_pref.xlsx"



item_name ="Monkey"

# Number 1 get preffered category left/right
def monkey_prefference():

    cat_est = BayesianEstimator(model, cat_result)
    # lft_est = BayesianEstimator(model, lft_result)
    # rgt_est = BayesianEstimator(model, rgt_result)

    cat_cpd = cat_est.estimate_cpd('Category', prior_type="BDeu", equivalent_sample_size=6).to_factor()
    # lft_cpd = lft_est.estimate_cpd('left_select', prior_type="BDeu", equivalent_sample_size=6).to_factor()
    # rgt_cpd = rgt_est.estimate_cpd('right_select', prior_type="BDeu", equivalent_sample_size=6).to_factor()

    print(cat_cpd)

    cat_df = pd.DataFrame()
    lft_df = pd.DataFrame()
    rgt_df = pd.DataFrame()

    cat = {}
    lft = {}
    rgt = {}

    monkeys = list(dic.keys())

    for i in monkeys:
        cat[item_name] = i
        lft[item_name] = i
        rgt[item_name] = i

        cat_max = {'max_prob':0}
        lft_max = {'max_prob':0}
        rgt_max = {'max_prob':0}

        for j in column_names[6:]:
            for k in column_names[6:]:
                for l in column_names[6:]:
                    cat_temp = cat_cpd.get_value(**{'Category': l, item_name: i, 'Left_categ':j, 'Right_categ':k})
                    lft_temp = lft_cpd.get_value(**{'left_select': l, item_name: i, 'Left_categ':j, 'Right_categ':k})
                    rgt_temp = rgt_cpd.get_value(**{'right_select': l, item_name: i, 'Left_categ': j, 'Right_categ':k})

                    if l in cat_max:
                        if cat_temp > cat_max[l]:
                            cat_max[l] = cat_temp
                    else:
                        cat_max[l] = cat_temp
                    if cat_temp > cat_max['max_prob']:
                        cat_max['max_prob'] = cat_temp
                        cat['Preffered_Category'] = l
                        cat['Left_categ'] = j
                        cat['Right_categ'] = k


                    if l in lft_max:
                        if cat_temp > lft_max[l]:
                            lft_max[l] = cat_temp
                    else:
                        lft_max[l] = cat_temp
                    if lft_temp > lft_max['max_prob']:
                        lft_max['max_prob'] = lft_temp
                        lft['Preffered_Left'] = l
                        lft['Left_categ'] = j
                        lft['Right_categ'] = k


                    if l in rgt_max:
                        if cat_temp > rgt_max[l]:
                            rgt_max[l] = cat_temp
                    else:
                        rgt_max[l] = cat_temp
                    if rgt_temp > rgt_max['max_prob']:
                        rgt_max['max_prob'] = rgt_temp
                        rgt['Preffered_Right'] = l
                        rgt['Left_categ'] = j
                        rgt['Right_categ'] = k

        cat.update(cat_max)
        lft.update(lft_max)
        rgt.update(rgt_max)

        cat_df = cat_df.append(cat, ignore_index=True)
        lft_df = lft_df.append(lft, ignore_index=True)
        rgt_df = rgt_df.append(rgt, ignore_index=True)

    cat_df = cat_df.reindex(columns=column_names[0:3]+ column_names[3:4] + column_names[6:])
    lft_df = lft_df.reindex(columns=column_names[0:3] + column_names[4:5] + column_names[6:])
    rgt_df = rgt_df.reindex(columns=column_names[0:3] + column_names[5:])

    writer = pd.ExcelWriter("tset.xlsx")
    cat_df.to_excel(writer, sheet_name='Overall Category')
    lft_df.to_excel(writer, sheet_name='Left Category')
    rgt_df.to_excel(writer, sheet_name='Right Category')
    writer.save()





monkey_prefference()