# https://docs.google.com/document/d/1IowqAokeJqQWhjJ__TcQn5hbDqoK5irUVmvb441-90Q/edit
from numpy import sqrt


caps = {1: 60, 2: 120, 3: 180, 4: 240, 6: 300}
scalingFactors = {1: 9500, 2: 5500, 3: 5100, 4: 4800, 6: 4650}
offsets = {1: 2746.116, 2: 1589.856, 3: 1474.230, 4: 1387.511, 6: 1344.151}


def my_round(val, digit=0):
    p = 10 ** digit
    return (val * p * 2 + 1) // 2 / p

def calc(W_MMR, L_MMR, fortmat_type):
    cap = caps[fortmat_type]
    scalingFactor = scalingFactors[fortmat_type]
    offset = offsets[fortmat_type]
    return cap / (1 + 11 ** (-(L_MMR - W_MMR - offset) / scalingFactor))

def calc_tie(W_MMR, L_MMR, fortmat_type):
    cap = caps[fortmat_type]
    scalingFactor = scalingFactors[fortmat_type]
    offset = offsets[fortmat_type]
    if W_MMR >= L_MMR:
        delta = -(cap / (1 + 11 ** (- ((sqrt((W_MMR - L_MMR) ** 2) -offset) / scalingFactor))) - (cap/3))
    else:
        delta = cap / (1 + 11 ** (- ((sqrt((W_MMR - L_MMR) ** 2) -offset) / scalingFactor))) - (cap/3)
    return delta

def MMR_calclation(format_type, MMR_ave, rank_list):
    expected_mmrdeltas = []

    # calc 1st palce
    sum = 0
    for i in range(int(12/format_type - 1)):
        if rank_list[0] == rank_list[i + 1]: # if tie
            sum += calc_tie(MMR_ave[0], MMR_ave[i + 1], format_type)
        else:
            sum += calc(MMR_ave[0], MMR_ave[i + 1], format_type)
    expected_mmrdeltas.append(int(my_round(sum, 0)))

    #calc 2nd- places
    for i in range(1, int(12/format_type) - 1):
        win = False
        sum = 0
        for i2 in range(int(12 / format_type)):
            My_mmr = MMR_ave[i]
            opponent_mmr = MMR_ave[i2]
            if rank_list[i] == rank_list[i2]:
                if i != i2:
                    sum += calc_tie(My_mmr, opponent_mmr, format_type)
                elif i == i2:
                    win = True
                else:
                    return
            else:
                if i != i2 and win == True:
                    sum += calc(My_mmr, opponent_mmr, format_type)
                elif i != i2 and win == False:
                    sum -= calc(opponent_mmr, My_mmr, format_type)
                elif i == i2:
                    win = True
                else:
                    return
        expected_mmrdeltas.append(int(my_round(sum, 0)))

    # calc for last place
    sum = 0
    for i in range(int(12/format_type - 1)):
        if rank_list[int(12/format_type - 1)] == rank_list[i]:
            sum -= calc_tie(MMR_ave[i], MMR_ave[int(12/format_type - 1)],format_type)
        else:
            sum -= calc(MMR_ave[i], MMR_ave[int(12/format_type - 1)],format_type)
    expected_mmrdeltas.append(int(my_round(sum, 0)))

    return expected_mmrdeltas

def MMR_calclation2(format_type, MMR_ave, set_team): # チーム指定時, set_teamは入力値の-1
    expected_mmrdeltas = []
    try:
        My_mmr = MMR_ave.pop(set_team)
    except IndexError:
        return False

    # calc 1st palce
    sum = 0
    for i in range(int(12/format_type) - 1):
        sum += calc(My_mmr, MMR_ave[i], format_type)
    expected_mmrdeltas.append(int(my_round(sum, 0)))

    #calc 2nd- places
    for i in range(1, int(12/format_type) - 1):
        for i2 in range(2): #max, min
            win = False
            sum = 0
            if i2 == 0: # max
                MMR_ave1 = sorted(MMR_ave, reverse=True)
            elif i2 == 1: # min
                MMR_ave1 = sorted(MMR_ave)
            
            for i3 in range(int(12 / format_type)):
                if win == False and i != i3:
                    sum -= calc(MMR_ave1[i3], My_mmr, format_type)
                elif win == True and i != i3:
                    sum += calc(My_mmr, MMR_ave1[i3 - 1], format_type)
                elif i == i3:
                    win = True
                else:
                    return
            expected_mmrdeltas.append(int(my_round(sum, 0)))

    # calc for last plce
    sum = 0
    for i in range(int(12/format_type - 1)):
        sum -= calc(MMR_ave[i], My_mmr, format_type)
    expected_mmrdeltas.append(int(my_round(sum, 0)))

    return expected_mmrdeltas