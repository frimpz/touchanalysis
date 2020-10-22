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

cat_result = result[(result['Category'] != 'Nothing')]
# cat_result = result
lft_result = result[(result['left_select'] != 'Nothing')]
rgt_result = result[(result['right_select'] != 'Nothing')]

# print(result.head(10))
# print(result.groupby(['Monkey', 'right_select']).size())
# print(result.groupby(['gender', 'Category']).size())


def create_plots(data_files, folder):
    graphs = list(data_files.keys())
    indicies = [(0, 6), (6, 12), (12, 18), (18, 24), (24, 30), (30, 36)]
    for x in indicies:
        for i in graphs[x[0]:x[1]]:
            data = {}
            for j in data_files[i]:
                if j == 'left':
                    left = data_files[i][j]
                elif j == 'right':
                    right = data_files[i][j]
                else:
                    data[j] = data_files[i][j]

            title = "Boxplot for Monkeys Left Category: " + left + " --- Right Category: " + right + " "
            create_boxplots(data=data, title=title, filename=folder + left + "-" + right + ".jpg")


# Creates a file that shows a monkeys overall category prefference given the left category and right category.
# Sheet 1 shows the number of times a monkey chose a picture from some category x,
# given that the picture on the left belongs to category A and the picture on the right
# belongs to category B for each monkey given the left category and right category

# Sheet 2 shows the joint probability of a monkey choosing a category
# given that the picture on the left belongs to category A and the picture on the right
# belongs to category B for each monkey given the left category and right category

# Sheet 3 shows the overall preference of a monkey.
# Here is where I am quiet unsure. A monkey can have a very high preference
# for some category depending on the pictures on the left and right.
# I would suggest we use a threshold, instead of the overall preference
# I will discuss with Dr. Baker

# A box plot is created for each pair of left category -- right category combination.
# Say for left: Nature and right : Aggressive, we show the probability shape of
# the distribution for all 6 categories aggressive, Affiliative, Nature, 'Cynomolgus', 'Fruit' and 'Lab'

# The file is typically named: monkey_pref.xlsx and plots are in figs directory

def monkey_pref(filename="monkey_pref.xlsx", data_frame=cat_result):
    writer = pd.ExcelWriter(filename)
    categories = ['Nature', 'Affiliative', 'Aggressive', 'Cynomolgus', 'Fruit',  'Lab']
    model = BayesianModel([('Monkey', 'Category'), ('Left_categ', 'Category'), ('Right_categ', 'Category')])
    z = BayesianEstimator(model, data_frame)

    count = [['Monkey', 'Left-Category', 'Right-Category', 'Category', 'Count']]
    count_dic = {}
    for i in z.state_counts('Category'):
        tmp = z.state_counts('Category')[i].to_dict()
        for j in tmp:
            count.append([i[1], i[0], i[2], j, tmp[j]])
            key = i[0]+"-"+i[2]
            if key not in count_dic:
                count_dic[key] = {}
            count_dic[key]['left'] = i[0]
            count_dic[key]['right'] = i[2]

            if j in count_dic[key]:
                count_dic[key][j].append(tmp[j])
            else:
                count_dic[key][j] = [tmp[j]]

    counts_df = pd.DataFrame.from_records(count[1:], columns=count[0])
    counts_df.to_excel(writer, sheet_name='Counts of Occurrence')

    # create box plots from occurrence
    create_plots(count_dic, "figs2/")

    cat_cpd = z.estimate_cpd('Category', prior_type="BDeu", equivalent_sample_size=6).to_factor()
    monkeys = list(dic.keys())
    data_files = {}
    prob = [['Monkey', 'Left-Category', 'Right-Category', 'Category', 'Probability']]
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
                    prob.append([monkey, left, right, category, cat_temp])
    prob_df = pd.DataFrame.from_records(prob[1:], columns=prob[0])
    prob_df.to_excel(writer, sheet_name='Conditional Prob Dist')

    # create boxplots from probabilities
    create_plots(data_files, "figs/")

    # Find the preffered category for each monkey given left and right
    pref_df = prob_df.sort_values('Probability', ascending=False).drop_duplicates(['Monkey'])
    pref_df.to_excel(writer, sheet_name='Aggregate Distribution')
    writer.save()


monkey_pref("monkey_pref.xlsx", cat_result)
