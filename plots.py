import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

"""
    Method creates multiple box plots
    :param data: dictionary of list
    dictionary keys -> labels
    dictionary values for boxplots.
    :return : None
    """


def create_boxplots(data=None, title="", filename=""):
    if data is None:
        data = {'ABC': [1, 2, 3, 8, 10], 'DEF': [2, 4, 6]}

    x_label = data.keys()
    data_to_plot = data.values()

    fig, ax = plt.subplots()
    bp = ax.boxplot(data_to_plot, patch_artist=True)
    ax.set_xticklabels(x_label)

    colors = ['red', 'yellow', 'green', 'blue', 'orange', 'violet']
    index = 0
    # # change outline color, fill color and linewidth of the boxes
    for box in bp['boxes']:
        box.set(facecolor=colors[index])
        index = index+1

    # change color and linewidth of the whiskers
    for whisker in bp['whiskers']:
        whisker.set(color='#7570b3', linewidth=2)
    #
    # # change color and linewidth of the caps
    for cap in bp['caps']:
        cap.set(color='#7570b3', linewidth=2)

    # change color and linewidth of the medians
    for median in bp['medians']:
        median.set(color='#b2df8a', linewidth=2)

    # change the style of fliers and their fill
    for flier in bp['fliers']:
        flier.set(marker='o', color='#e7298a', alpha=0.5)

    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    bx = []
    for i in bp['boxes']:
        bx.append(i)
    ax.legend(bx, list(x_label), loc='upper right')
    ax.title.set_text(title)
    # plt.savefig(filename, dpi=100)
    plt.show()
    plt.clf()


def create_histograms1():

    group1 = [1, 5, 1, 2, 2, 3, 4, 1, 5, 1, 3, 4]
    group2 = [2, 2, 2, 1, 1, 3, 1, 4, 5, 2, 4, 4, 5, 5]
    group3 = [3, 3, 3, 2, 2, 4, 2, 5, 1]

    # Create a stacked histogram here
    plt.hist([group1, group2, group3],
             bins=[1, 2, 3, 4, 5, 6], rwidth=0.8, align="left", stacked=True)

    plt.legend(["Group 1", "Group 2", "Group 3"])
    plt.xticks([1, 2, 3, 4, 5])
    plt.ylabel("Quantity")
    plt.xlabel("Value")
    plt.show()

# create_boxplots()


def create_histograms():
    df = pd.DataFrame({'a': [10, 20, 30, 40, 50], 'b': [15, 25, 30, 25, 35],
                       'c': [35, 40, 29, 39, 49], 'd': [45, 50, 30, 15, 12]},
                        index=['john', 'bob', 'Terry', 'Smith', 'Prince'])
    print(df)
    # matplotlib.style.use('ggplot')

    # exit()

    fig, ax = plt.subplots()
    df[['a', 'c']].plot.bar(stacked=True, width=0.4, position=0.5, colormap="bwr", ax=ax, alpha=0.7)
    df[['b', 'd']].plot.bar(stacked=True, width=0.4, position=-0.5, colormap="RdGy", ax=ax, alpha=0.7)
    plt.legend(loc="upper right")
    plt.show()


# create_histograms()