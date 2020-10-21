import pandas as pd

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(result.head(20))
#
# s = result['Monkey']
# for i in set(s):
#     print(i)
# print(result.shape)
# print(len(set(s)))
#
# with open("monkeys.txt", 'w') as f:
#     for s in list(set(s)):
#         f.write(str(s) + '\n')


def read_csv(filename):
    dic = {}
    with open(filename) as f:
        lines = f.read().splitlines()
        for line in lines:
            x = line.split(",")
            dic[str(x[0])] = x[1]
    return dic
