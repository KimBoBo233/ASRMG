import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.tab10.colors)

if __name__ == "__main__":
    size = [5, 6, 7, 8, 9, 10, 11]
    INTRA_BH = [0.260945927, 0.579007207, 0.640655547, 0.642379145, 0.659509359, 0.782209575, 0.732823424]
    INTER_BP = [0.008333785, 0.008202721, 0.008212537, 0.008205426, 0.036421032, 0.036463405, 0.045624102]
    SBH = [0.729538303, 0.8730514, 0.894825596, 0.928255295, 0.928890981, 0.9291872, 0.927055086]
    SBP = [0.008200177, 0.008082685, 0.008065643, 0.008006477, 0.013300455, 0.013296431, 0.015104535]

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
              '#17becf']

    fontsize = 30

    fig, ax = plt.subplots(figsize=(12, 8))

    ax.plot(size, INTRA_BH, 'o-', label='INTRA_BH', color=colors[0])

    ax.plot(size, SBH, 'o-', label='SBH', color=colors[1])
    ax2 = ax.twinx()

    ax2.plot(size, INTER_BP, 'v-', label='INTER_BP', color=colors[2])

    ax2.plot(size, SBP, 'v-', label='SBP', color=colors[4])


    plt.rcParams['font.sans-serif'] = ['Times New Roman']
    ax.set_ylabel('cohesion metrics', fontsize=fontsize)
    ax.set_xlabel('scale', fontsize=fontsize)
    ax2.set_ylabel('coupling metrics', fontsize=fontsize)

    ax.set_ylim([0.1, 1])
    ax.tick_params(axis='both', labelsize=fontsize)
    ax.legend(fontsize=fontsize, loc="upper left")
    ax2.set_ylim([0, 0.08])
    ax2.legend(fontsize=fontsize, loc="lower right")
    ax2.tick_params(axis='both', labelsize=fontsize)

    plt.tight_layout()

    plt.savefig('RQ2_MSA SBH_SBP.png', bbox_inches='tight')
    plt.savefig('Fig15_a.png', bbox_inches='tight')

    plt.show()
