import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['simsun']
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.tab10.colors)

if __name__ == "__main__":
    size = [5, 6, 7, 8, 9, 10, 11]
    SDH = [0.148611111, 0.148611111, 0.148611111, 0.148611111, 0.125, 0.125, 0.1]

    SDP = [0.072869318, 0.072869318, 0.072869318, 0.072869318, 0.118949776, 0.118949776, 0.116761504]

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
              '#17becf']


    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_title("BookStoreApp ", fontsize=20)


    ax.plot(size, SDH, 'o-', label='SDH', color=colors[0])

    ax.plot(size, SDP, 'o-', label='SDP', color=colors[1])
    ax.set_ylabel('value', fontsize=20)
    ax.set_xlabel('size', fontsize=20)
    ax.set_ylim([0.05, 0.2])
    ax.tick_params(axis='both', labelsize=20)
    ax.legend(fontsize=20, loc="upper left")

    plt.tight_layout()

    plt.savefig('RQ2_BSA SDH_SDP.png', bbox_inches='tight')

    plt.show()
