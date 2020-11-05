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


gender_df = result[['gender', 'Left_categ', 'Right_categ', 'Category']]

genders = list(set((gender_df.gender)))


categories = ['Affiliative', 'Aggressive', 'Cynomolgus', 'Fruit',  'Lab', 'Nature']
model = BayesianModel([('Left_categ', 'Category'), ('Right_categ', 'Category')])


data_files = {}
temp = [['gender', 'Left-Category', 'Right-Category', 'Category', 'Count', 'Probability']]
for gender in genders:
    df = (gender_df[(gender_df.gender == gender)])
    z = BayesianEstimator(model, df)

    cat_cpd = z.estimate_cpd('Category', prior_type="bdeu", equivalent_sample_size=6)  # .to_factor()
    for left in categories:
        for right in categories:
            for cat in categories:
                try:
                    count = z.state_counts('Category')[left][right][cat]
                    prob = cat_cpd.get_value(
                        **{'Left_categ': left, 'Right_categ': right, 'Category': cat})
                    if not isNaN(prob) and prob > 0:
                        temp.append([gender, left, right, cat, count, prob])
                    else:
                        temp.append([gender, left, right, cat, count, prob])
                except KeyError:
                    pass
                        #temp.append([gender, left, right, cat, count, 0])
#
prob_df = pd.DataFrame.from_records(temp[1:], columns=temp[0])

gen_df = prob_df[['gender', 'Left-Category', 'Right-Category', 'Category', 'Count']].\
    groupby(['gender', 'Left-Category', 'Right-Category', 'Category'])['Count'].agg(['sum'])# .reset_index()
# boxplot = gen_df.boxplot(rot=45, fontsize=12, figsize=(8, 10))
print(gen_df)

#
group = ['gender', 'Category']
ax, bp = gen_df.boxplot(rot=90, fontsize=12, figsize=(12, 10), column=['sum'], by=group, return_type="both")[0]
plt.title("Box plot grouped by : " + str(group))
plt.suptitle('')
plt.ylabel("sum")
#
#
group = ['gender', 'Left-Category', 'Category']
ax, bp = gen_df.boxplot(rot=90, fontsize=12, figsize=(24, 12), column=['sum'], by=group, return_type="both")[0]
plt.title("Box plot grouped by : " + str(group))
plt.suptitle('')
plt.ylabel("sum")
#
#
group = ['gender', 'Right-Category', 'Category']
ax, bp = gen_df.boxplot(rot=90, fontsize=12, figsize=(24, 12), column=['sum'], by=group, return_type="both")[0]
plt.title("Box plot grouped by : " + str(group))
plt.suptitle('')
plt.ylabel("sum")
#
plt.show()



writer = pd.ExcelWriter("results/gender.xlsx")
prob_df.to_excel(writer, sheet_name='Distributuion')
prob_df.sort_values('Probability', ascending=False).\
    drop_duplicates(['gender']).to_excel(writer, sheet_name='prefference')
writer.save()
#
#
#
# # Next I show boxplot grouped by sex
#
