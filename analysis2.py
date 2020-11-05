import os
import pickle

import pandas as pd
from pgmpy.estimators import BayesianEstimator
from pgmpy.models import BayesianModel
from functools import reduce
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
        return 'Nothing'


# define a Custom aggregation
# function for finding total
def total(series):
      return reduce(lambda x, y: x + y, series)


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


# Creates a file that shows a monkeys/gender overall category prefference given the left category and right category.
# Sheet 1 shows the number of times a monkeys/gender chose a picture from some category x,
# given that the picture on the left belongs to category A and the picture on the right
# belongs to category B for each monkeys/gender given the left category and right category

# Sheet 2 shows the joint probability of a monkeys/gender choosing a category
# given that the picture on the left belongs to category A and the picture on the right
# belongs to category B for each monkeys/gender given the left category and right category

# Sheet 3 shows the overall preference of a monkeys/gender.
# Here is where I am quiet unsure. A monkeys/gender can have a very high preference
# for some category depending on the pictures on the left and right.
# I would suggest we use a threshold, instead of the overall preference
# I will discuss with Dr. Baker

# A box plot is created for each pair of left category -- right category combination.
# Say for left: Nature and right : Aggressive, we show the probability shape of
# the distribution for all 6 categories aggressive, Affiliative, Nature, 'Cynomolgus', 'Fruit' and 'Lab'

# The files are typically in monkey and gender directories
# Each directory contains the overall prefference, left prefference and right prefference

def pref(directory=None, filename=None, data_frame=None, item=None):
    # Create directories for the files.
    # I had two sets of box plots, one based on probabilities and another based on counts.
    # As far as I know I prefer the ones based on counts.
    os.makedirs(os.path.join(os.getcwd(), os.path.dirname(directory)), exist_ok=True)
    os.makedirs(os.path.dirname(directory+"/"+"figs2/"), exist_ok=True)
    os.makedirs(os.path.dirname(directory+"/"+"figs/"), exist_ok=True)
    writer = pd.ExcelWriter(directory+"/"+filename)
    categories = ['Affiliative', 'Aggressive', 'Cynomolgus', 'Fruit',  'Lab', 'Nature']
    model = BayesianModel([(item, 'Category'), ('Left_categ', 'Category'), ('Right_categ', 'Category')])
    z = BayesianEstimator(model, data_frame)

    count = [[item, 'Left-Category', 'Right-Category', 'Category', 'Count']]
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
    # create_plots(count_dic, directory+"/"+"figs2/")

    cat_cpd = z.estimate_cpd('Category', prior_type="K2", equivalent_sample_size=0).to_factor()
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
    # print(prob_df[(prob_df.Monkey == '29928')])
    print(prob_df)

    # create boxplots from probabilities
    # create_plots(data_files, directory+"/"+"figs/")

    # Find the preffered category for each monkey given left and right
    pref_df = prob_df.sort_values('Probability', ascending=False).drop_duplicates(['Monkey'])
    pref_df.to_excel(writer, sheet_name='Aggregate Distribution')

    # Assertion used to test validity of the two dictionaries for box plots
    # for i in count_dic:
    #     for j in categories:
    #         tt = {}
    #         xxx = sorted(count_dic[i][j])
    #         yyy = sorted(data_files[i][j])
    #         assert (len(xxx) == len(yyy))
    #         for c in zip(xxx, yyy):
    #             if c[0] in tt:
    #                 assert(c[1] == tt[c[0]], str(c[1])+"--"+str(tt[c[0]]))
    #                 print(c[0], c[1])
    #             else:
    #                 tt[c[0]] = c[1]
    # writer.save()


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

# Get data for overall category, left selected and right selected.
# mon_df = result[['Monkey', 'Left_categ', 'Right_categ', 'Category']]
# 29928, 29987, 34536, 34615
# result = result[(result.Monkey == '29987')]
# mon_df = result[['Monkey', 'Left_categ', 'Right_categ', 'Category']].groupby(['Monkey'])['Monkey'].\
# #     agg(['count']).reset_index()

x = (result[['Monkey', 'Left_categ', 'Right_categ', 'Category']].\
    groupby(['Monkey', 'Left_categ', 'Right_categ', 'Category']).size()/216).reset_index()
# print(x[(x.Monkey == '29928')])

x = (result[['Monkey', 'Left_categ', 'Right_categ', 'Category']].\
    groupby(['Monkey', 'Left_categ', 'Right_categ']).size()/216).reset_index()
# print(x[(x.Monkey == '29928')])

# print(mon_df.head(10))
# gen_df = result[['gender', 'Left_categ', 'Right_categ', 'Category']].groupby(['gender'])['gender'].\
#     agg(['count']).reset_index()
# print(gen_df.head(10))

# lft_result = result[(result['left_select'] != 'Nothing')][['Monkey', 'gender', 'Left_categ', 'Right_categ', 'left_select']]
# rgt_result = result[(result['right_select'] != 'Nothing')][['Monkey', 'gender', 'Left_categ', 'Right_categ', 'right_select']]


# For Overall Preference
pref("try", "monkey_pref.xlsx", result, 'Monkey')

# mon_df.groupby(['Monkey', 'Left_categ', 'Right_categ']).agg('count'))
# print(gen_df.groupby(['gender']).agg(['sum', total]))