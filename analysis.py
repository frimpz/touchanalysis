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


def get_dataframe():
    return result


"""
    To send dataframe to some other classs
    """


def get_gender_dataframe():
    return gender_df


"""
    Method creates  the excel file and box plot
    :param excel_rows: all columns that appear in excel file
    monkey : ['Monkey', 'Left-Category', 'Right-Category', 'Category', 'Count', 'Probability', 'lower CI', 'upper CI', 'P-Value']
    gender:  ['gender', 'Left-Category', 'Right-Category', 'Category', 'Count', 'Probability', 'lower CI', 'upper CI', 'P-Value']
    :param item_name: Monkey/gender
    :param items: Monkey list/ gender list
    :param file_name: filename of excel
    :param df_cols : pandas column to limit 
    :param groupby_cols : pandas group by column
    :param bp_group : boxplot groupby
    :return : None
    """


def distribution(excel_rows, item_name,  items, file_name):
    # Using 95% confidence interval
    # (1-0.95)/2
    Z_score = abs(st.norm.ppf(0.025))
    alpha = 1-0.95
    data_files = {}

    # create dataframe
    for item in items:
        if item_name == "Monkey":
            df = (monkey_df[(monkey_df.Monkey == item)])
        elif item_name == "gender":
            df = (gender_df[(gender_df.gender == item)])
        z = BayesianEstimator(model, df)
        cat_cpd = z.estimate_cpd('Category', prior_type="bdeu", equivalent_sample_size=0)  # .to_factor()
        for condition in conditions:
            for category in categories:
                try:
                    count = list(z.state_counts('Category')[condition]
                               .to_dict().values())[0][category]
                    # count = z.state_counts('Category')[condition][category][category]
                    prob = cat_cpd.get_value(
                        **{'Condition': condition, 'Category': category})
                    # print(prob)
                    # p_hat and q_hat set to conservative since we have no previous data #0.5 for each
                    # Since its probability I clip to 0
                    lower_ci = max(prob - Z_score * math.sqrt((0.5*0.5)/df.shape[0]), 0)
                    upper_ci = prob + Z_score * math.sqrt((0.5*0.5)/df.shape[0])
                    if not isNaN(prob) and prob > 0:
                        excel_rows.append([item, condition, category, count, prob, lower_ci, upper_ci, alpha])
                    else:
                        pass
                        # excel_rows.append([item, left, right, cat, count, prob, 0, 0, 0])
                except KeyError:
                        pass
                        # excel_rows.append([item, left, right, cat, count, 0, 0 , 0, 0])

    prob_df = pd.DataFrame.from_records(excel_rows[1:], columns=excel_rows[0])
    writer = pd.ExcelWriter(file_name+".xlsx")
    prob_df.to_excel(writer, sheet_name='Distribution')
    prob_df.sort_values('Probability', ascending=True).drop_duplicates([item_name]).to_excel(writer, sheet_name='prefference')
    writer.save()
    return prob_df





# for monkeys
categories = ['Affiliative', 'Aggressive', 'Cynomolgus', 'Fruit',  'Lab', 'Nature']
conditions = list(set(result['Condition'].tolist()))

model = BayesianModel([('Condition', 'Category')])

excel_rows = [['Monkey', 'Condition', 'Category', 'Count', 'Probability', 'lower CI',
               'upper CI', 'alpha']]
items = monkeys
file_name = "results/monkey"

df_cols = ['Condition', 'Category', 'Count']
groupby_cols = ['Condition', 'Category']
bp_group = ['Category']
item_name = 'Monkey'
# distribution(excel_rows, item_name,  items, file_name)


# for gender
categories = ['Affiliative', 'Aggressive', 'Cynomolgus', 'Fruit',  'Lab', 'Nature']
model = BayesianModel([('Condition', 'Category')])

excel_rows = [['gender', 'Condition', 'Category', 'Count', 'Probability', 'lower CI',
               'upper CI', 'alpha']]
items = genders
file_name = "results/gender"

df_cols = ['gender', 'Condition', 'Category', 'Count']
groupby_cols = ['gender', 'Condition', 'Category']
bp_group = ['gender', 'Category']
item_name = 'gender'
# distribution(excel_rows, item_name,  items, file_name)







