'''
This Script is used to show monkeys that have a special
prefference or avoid some prefference
'''

import matplotlib.pyplot as plt
import numpy as np
from analysis import get_dataframe
import pandas as pd

df = get_dataframe()

mky_len = len(set(df['Monkey'].tolist()))
categories = list(set(df['Category']))


totals__yy = df.groupby(['Monkey', 'Category']).size().to_frame('Size')\
    .reset_index()#[['Monkey', 'Size']].set_index('Monkey')

totals = df.groupby(['Monkey', 'Condition', 'Category']).size().to_frame('Size')\
    .reset_index()#.set_index('Monkey')#[['Monkey', 'Size']].set_index('Monkey')

a_df = pd.DataFrame()
for i in categories:
    xxx = totals.loc[totals['Condition'].str.contains(i)].groupby(['Monkey']).sum().reset_index()
    xxx['pre'] = i
    a_df = a_df.append(xxx)
#
totals = pd.merge(totals__yy, a_df, how='inner', left_on=['Monkey', 'Category']\
                  , right_on=['Monkey', 'pre']).drop(columns=['pre'])

totals['std_norm'] = totals.apply(lambda row: row.Size_x/row.Size_y, axis=1)

totals.boxplot(column=['std_norm'], by=['Category'])
plt.xlabel('Category')
plt.ylabel('Standardized Count')
plt.title("Box plot showing Monkey Preferences")
plt.suptitle('')
plt.savefig("results/outliers" + ".png", dpi=100)
# plt.show()


dic = {}
for i in categories:
    data = totals[totals['Category'] == i]
    data_list = list(data['std_norm'])
    keys = list(set(data['Monkey']))

    q_1 = np.percentile(data_list, 25)
    q_3 = np.percentile(data_list, 75)
    iqr = q_3 - q_1

    lower_boundary = q_1 - (1.5 * iqr)
    upper_boundary = q_3 + (1.5 * iqr)

    for j in keys:
        val = data.loc[(data['Monkey'] == j) & (data['Category'] == i)]['std_norm'].values[0]

        if val > upper_boundary:
            dic[(j, i)] = 'upper'
        elif val < lower_boundary:
            dic[(j, i)] = 'lower'
        else:
            dic[(j, i)] = 'normal'


totals['Outliers'] = totals.set_index(['Monkey', 'Category']).index.map(dic)
totals = totals.rename(columns={'Size_x': 'Selected', 'Size_y': 'Overall'})
print(totals.sort_values('Outliers'))
totals.sort_values('Outliers').to_excel('results/outliers.xlsx')