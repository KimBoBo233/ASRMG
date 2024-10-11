import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":


    categories = ['BSA', 'M4C', 'PC', 'SCS', 'TT']
    before_SBH = [0.703619513990486, 0.302159332156232, 0.653967889109599, 0.564534076726722, 0.679193872808977]
    after_SBH = [0.928255294922212, 0.823186537345393, 0.936108219618382, 0.886613752300839, 0.860629392053884]

    fontsize = 20

    bar_width = 0.2


    x = np.arange(len(categories))


    colors = ['#e5b5a4', '#559da5', '#acc38c']

    plt.figure(dpi=600)

    plt.subplots_adjust(bottom=0.15)

    plt.rcParams['font.sans-serif'] = ['simsun']
    plt.bar(x - 0.5 * bar_width, before_SBH, width=bar_width, label='before_SBH')
    plt.bar(x + 0.5 * bar_width, after_SBH, width=bar_width, label='after_SBH')


    plt.xlabel('ms', fontsize=fontsize)
    plt.ylabel('SBH', fontsize=fontsize)


    plt.xticks(x, categories, fontsize=fontsize)
    plt.yticks(fontsize=fontsize)


    plt.legend(loc="upper left", fontsize=fontsize)

    plt.savefig('Fig13_a.eps', bbox_inches='tight')
    plt.savefig('RQ1_SBH.png', bbox_inches='tight')

    plt.show()
