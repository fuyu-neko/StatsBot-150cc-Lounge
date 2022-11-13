import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd

async def create_plot(mmrhistory, season=''):
    if season == 4:
        ranks = [0, 4000, 5500, 7000, 8500, 10000, 11500, 13000, 14500]
        colors_between = [0]
    elif season == 5:
        ranks = [0, 2000, 4000, 6000, 8000, 10000, 11000, 13000, 14000]
        colors_between = [1000, 3000, 5000, 7000, 9000, 12000]
    elif season == 6 or season == 7:
        ranks = [0, 2000, 4000, 6000, 8000, 10000, 12000, 14000, 15000]
        colors_between = [1000, 3000, 5000, 7000, 9000, 11000, 13000]
    else:
        ranks = [0, 2000, 4000, 6000, 8000, 10000, 11000, 13000, 14000]
        colors_between = [1000, 3000, 5000, 7000, 9000, 12000]
        
    colors = ['#817876', '#E67E22', '#7D8396', '#F1C40F', '#3FABB8',
              '#286CD3', '#9CCBD6', '#0E0B0B', '#A3022C']

    xs = np.arange(len(mmrhistory))
    plt.rcParams.update(plt.rcParamsDefault)
    plt.style.use('lounge_style.mplstyle')
    lines = plt.plot(mmrhistory)
    plt.setp(lines, 'color', 'snow', 'linewidth', 1.0)
    xmin, xmax, ymin, ymax = plt.axis()
    plt.ylabel("MMR")
    plt.grid(True, 'both', 'both', color='snow', linestyle=':')

    for i in range(len(ranks)):
        if ranks[i] > ymax:
            continue
        maxfill = ymax
        if i + 1 < len(ranks):
            if ranks[i] < ymin and ranks[i + 1] < ymin:
                continue
            if ranks[i + 1] < ymax:
                maxfill = ranks[i + 1]
        if ranks[i] < ymin:
            minfill = ymin
        else:
            minfill = ranks[i]
        plt.fill_between(xs, minfill, maxfill, color=colors[i])
        if season >= 5:
            divide =  [i for i in colors_between if minfill <= i <= maxfill]
            plt.hlines(divide, xmin, xmax, colors='snow', linestyle='solid', linewidth=1)
    plt.fill_between(xs, ymin, mmrhistory, facecolor='#212121', alpha=0.4)
    b = BytesIO()
    plt.savefig(b, format='png', bbox_inches='tight')
    b.seek(0)
    plt.clf()
    plt.close()
    return b

async def create_overall_histogram(mmr_list, season):
    plt.rcParams.update(plt.rcParamsDefault)
    plt.style.use('lounge_style.mplstyle')

    plt.rcParams["figure.figsize"] = (18, 9)
    plt.title(f"MMR Distribution (Events Played > 0)", loc="left", fontsize=12)
    plt.xlabel("MMR", fontsize=10)
    plt.ylabel("Players", fontsize=10)
    plt.grid(True)
    plt.tick_params(labelsize = 10)

    n, bins, patches = plt.hist(mmr_list, alpha=0.5, bins=160, range=(0, 16000), histtype="bar", rwidth = 0.5) #(8) ヒストグラムの描画
    y_max = int(max(n)) + 1
    plt.yticks(np.arange(0, y_max, 20))

    if season >= 6:
        for i in range(142):
            if 0 <= i < 20:
                color = '#817876'
            elif 20 <= i < 40:
                color = '#C65911'
            elif 40 <= i < 60:
                color = '#D9D9D9'
            elif 60 <= i < 80:
                color = '#FFD966'
            elif 80 <= i < 100:
                color = '#3FABB8'
            elif 100 <= i < 120:
                color = '#286CD3'
            elif 120 <= i < 140:
                color = '#BDD7EE'
            elif 140 <= i < 150:
                color = '#D9E1F2'
            elif 150 <= i:
                color = '#A3022C'
            patches[i].set_facecolor('%s' % color)

    elif season == 5:
        for i in range(142):
            if 0 <= i < 20:
                color = '#817876'
            elif 20 <= i < 40:
                color = '#C65911'
            elif 40 <= i < 60:
                color = '#D9D9D9'
            elif 60 <= i < 80:
                color = '#FFD966'
            elif 80 <= i < 100:
                color = '#3FABB8'
            elif 100 <= i < 110:
                color = '#286CD3'
            elif 110 <= i < 130:
                color = '#BDD7EE'
            elif 130 <= i < 140:
                color = '#D9E1F2'
            elif 140 <= i:
                color = '#A3022C'
            patches[i].set_facecolor('%s' % color)
    elif season == 4:
        for i in range(142):
            if 0 <= i < 20:
                color = '#817876'
            elif 20 <= i < 40:
                color = '#C65911'
            elif 40 <= i < 5:
                color = '#D9D9D9'
            elif 5 <= i < 70:
                color = '#FFD966'
            elif 70 <= i < 85:
                color = '#3FABB8'
            elif 85 <= i < 100:
                color = '#286CD3'
            elif 100 <= i < 115:
                color = '#BDD7EE'
            elif 115 <= i < 130:
                color = '#D9E1F2'
            elif 145 <= i:
                color = '#A3022C'
            patches[i].set_facecolor('%s' % color)
    b = BytesIO()
    plt.savefig(b, format='png', bbox_inches='tight')
    b.seek(0)
    plt.clf()
    plt.close()
    
    return n, b

async def create_score_plot(scores, ave, check_scores, check_sma, num_SMA):
    x_lsit = list(range(1, len(scores)+1))
    plt.rcParams.update(plt.rcParamsDefault)
    plt.figure(facecolor="azure", edgecolor="coral", linewidth=2)

    if check_scores == "Yes":
        p1 = plt.plot(x_lsit, scores, marker="o", markersize=4, label='Scores', color='#1f77b4')

    if check_sma == "Yes":
        SMA = pd.Series(scores).rolling(num_SMA).mean()
        p2 = plt.plot(x_lsit, SMA, marker="o", markersize=3, label='SMA', color='#ff7f0e')

    plt.ylabel("Scores")
    plt.grid(True)

    p3 = plt.axhline(y=ave, color='#e41a1c', label='Average Score')
    plt.legend(loc=2)

    b = BytesIO()
    plt.savefig(b, format='png', bbox_inches='tight')
    b.seek(0)
    plt.clf()
    plt.close()
    return b