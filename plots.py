import matplotlib.pyplot as plt
import numpy as np

"""
    Method creates multiple box plots
    :param data: dictionary of list
    dictionary keys -> labels
    dictionary values for boxplots.
    :return : None
    """


def create_boxplots(data=None, title=""):
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
    ax.legend([bp["boxes"][0], bp["boxes"][1]], ['A', 'B'], loc='upper right')
    ax.title.set_text(title)
    plt.show()


# create_boxplots()
#
#
# color = list(np.random.choice(range(256), size=3))
# print(color)