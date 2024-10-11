import matplotlib.pyplot as plt
import numpy as np
from matplotlib import ticker


if __name__ == "__main__":

    categories = ['BSA', 'M4C', 'PC', 'SCS', 'TT']
    no = [0.008011, 0.010416, 0.00598111, 0.004478, 0.047418]
    have = [0.008006, 0.010426, 0.00598111, 0.004502, 0.047421]

    fontsize = 20

    bar_width = 0.2


    x = np.arange(len(categories))


    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
              '#17becf']


    fig, ax = plt.subplots()
    plt.xticks(x, categories, fontsize=fontsize)

    plt.subplots_adjust(bottom=0.15)
    plt.rcParams['font.sans-serif'] = ['simsun']

    plt.bar(x - 0.5 * bar_width, no, width=bar_width, label='无')
    plt.bar(x + 0.5 * bar_width, have, width=bar_width, label='有')
    ax.set_xlabel('ms', fontsize=18)
    ax.set_ylabel('value', fontsize=fontsize)

    ax.set_ylim([0,0.05])
    ax.tick_params(axis='both', labelsize=fontsize)
    ax.legend(loc="upper left", fontsize=fontsize)


    plt.savefig('RQ4_SBP.png', bbox_inches='tight')
    plt.savefig('Fig20_b.eps', bbox_inches='tight')

    plt.show()
