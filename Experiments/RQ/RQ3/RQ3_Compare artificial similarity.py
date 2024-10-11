import matplotlib.pyplot as plt
import numpy as np
from matplotlib import ticker


if __name__ == "__main__":

    categories = ['BSA-8', 'M4C-22', 'PC-4', 'SCS-15', 'TT-36', 'TT-41']
    simi = [1, 0.9511026898797798, 1, 0.9922299922299922, 1, 0.954566054063902]

    fontsize = 16

    bar_width = 0.3


    x = np.arange(len(categories))


    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
              '#17becf']


    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.15)


    plt.rcParams['font.sans-serif'] = ['simsun']

    ax.bar(categories, simi, width=bar_width, label='dependability', color=colors[1])
    ax.set_xlabel('system and size', fontsize=fontsize)
    ax.set_ylabel('value', fontsize=fontsize)



    ax.tick_params(axis='both', labelsize=fontsize)

    ax.set_ylim([0.8, 1])



    def format_func(value, tick_number):
        return "{:.2f}".format(value)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_func))


    ax.legend(loc="upper right", fontsize=fontsize)


    plt.savefig('RQ3_compare.png', bbox_inches='tight')
    plt.savefig('Fig18.eps', bbox_inches='tight')

    plt.show()
