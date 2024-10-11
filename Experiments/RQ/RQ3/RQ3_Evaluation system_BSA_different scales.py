import matplotlib.pyplot as plt
import numpy
import numpy as np

plt.rcParams['font.sans-serif'] = ['simsun']
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.tab10.colors)

if __name__ == "__main__":
    size = [5, 6, 7, 8, 9, 10, 11]

    SBH = [0.729538303, 0.8730514, 0.894825596, 0.928255295, 0.928890981, 0.9291872, 0.927055086]
    SDH = [0.148611111, 0.148611111, 0.148611111, 0.148611111, 0.125, 0.125, 0.1]
    SDH = numpy.array(SDH) * 6

    SBP = [0.008200177, 0.008082685, 0.008065643, 0.008006477, 0.013300455, 0.013296431, 0.015104535]
    SBP = numpy.array(SBP) * 10
    SDP = [0.072869318, 0.072869318, 0.072869318, 0.072869318, 0.118949776, 0.118949776, 0.116761504]

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
              '#17becf']

    fontsize = 28

    fig, ax = plt.subplots(figsize=(12, 8))

    ax.plot(size, SBH, 'o-', label='SBH', color=colors[0])
    ax.plot(size, SDH, 'o-', label='SDH * 6', color=colors[1])
    ax.set_ylim([0.5, 1])
    ax.set_ylabel('cohesion', fontsize=fontsize)
    ax.set_xlabel('size', fontsize=fontsize)
    ax.tick_params(axis='both', labelsize=fontsize)
    ax.legend(fontsize=fontsize, loc="upper left")
    ax2 = ax.twinx()
    ax2.plot(size, SBP, 'v-', label='SBP * 10 ', color=colors[2])

    ax2.plot(size, SDP, 'v-', label='SDP', color=colors[4])
    ax2.set_ylim([0.05, 0.2])
    ax2.set_ylabel('coupling', fontsize=fontsize)
    ax2.tick_params(axis='both', labelsize=fontsize)
    ax2.legend(fontsize=fontsize, loc="lower right")

    plt.tight_layout()

    plt.savefig('RQ3_BSA different scale.png', bbox_inches='tight')
    # 显示图形
    plt.show()
