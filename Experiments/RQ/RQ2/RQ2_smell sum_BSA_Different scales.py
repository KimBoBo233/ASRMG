import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.tab10.colors)

if __name__ == "__main__":
    size = [5, 6, 7, 8, 9, 10, 11]
    num = [7, 3, 2, 0, 0, 0, 0, ]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
              '#17becf']

    fontsize = 36

    fig, ax = plt.subplots(figsize=(12, 4))

    plt.rcParams['font.sans-serif'] = ['simsun']

    ax.plot(size, num, 'x-', label='num', color=colors[5])
    ax.set_ylabel('num', fontsize=fontsize)
    ax.set_xlabel('size', fontsize=fontsize)

    ax.set_ylim([0, 8])
    ax.tick_params(axis='both', labelsize=fontsize)
    ax.legend(fontsize=fontsize, loc="upper right")


    plt.tight_layout()

    plt.savefig('RQ2_MSA size gs num.png', bbox_inches='tight')
    plt.savefig('Fig16_a.eps', bbox_inches='tight')

    plt.show()
