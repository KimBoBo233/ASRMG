import matplotlib.pyplot as plt
import numpy as np


if __name__ == "__main__":


    categories = ['BSA', 'M4C', 'PC', 'SCS', 'TT']
    before = [5, 11, 4, 11, 37]
    after = [8, 22, 4, 15, 36]

    fontsize = 20

    bar_width = 0.2


    x = np.arange(len(categories))


    colors = ['#e5b5a4', '#559da5', '#acc38c']

    plt.figure(dpi=600)


    plt.subplots_adjust(bottom=0.15)

    plt.rcParams['font.sans-serif'] = ['simsun']

    plt.bar(x - 0.5 * bar_width, before, width=bar_width, label='before')
    plt.bar(x + 0.5 * bar_width, after, width=bar_width, label='after')

    plt.xlabel('ms', fontsize=fontsize)
    plt.ylabel('size', fontsize=fontsize)



    plt.xticks(x, categories, fontsize=fontsize)
    plt.yticks(fontsize=fontsize)

    plt.legend(loc="upper left", fontsize=fontsize)

    plt.savefig('Fig12_a.eps', bbox_inches='tight')
    plt.savefig('RQ1_size.png', bbox_inches='tight')

    plt.show()
