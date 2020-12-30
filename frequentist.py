import os
import pickle
from analysis import get_dataframe
import pandas as pd


def prob(df, pos):
    if df['Category'] == df['Left_categ'] and pos == "left":
        return df['Category']
    elif df['Category'] == df['Right_categ'] and pos == "right":
        return df['Category']
    else:
        return 'Nothing'


result = get_dataframe()


# probability of gender selecting some category
ovrll_df = result[['gender', 'Category']]
total = ovrll_df.shape[0]
ovrll_df = ovrll_df.groupby(['gender', 'Category']).size().reset_index(name='Counts')
ovrll_df['Probability'] = [x/total for x in ovrll_df['Counts']]
# print(gender_df)


# probability of gender selecting some category given some condition
cond_df = result[['gender', 'Condition', 'Category']]
total = cond_df.shape[0]
cond_df = cond_df.groupby(['gender', 'Condition', 'Category']).size().reset_index(name='Counts')
cond_df['Probability'] = [x/total for x in cond_df['Counts']]
# print(gender_df)

writer = pd.ExcelWriter('results/category'+".xlsx")
ovrll_df.to_excel(writer, sheet_name='Overall')
cond_df.to_excel(writer, sheet_name='Condition')
writer.save()