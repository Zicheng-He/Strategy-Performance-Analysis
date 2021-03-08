# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 22:27:53 2020

@author: 63438
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import itertools
import seaborn as sns

sns.set_palette("GnBu")

df = pd.read_csv(r"./data_Performance_track_records_out.csv",
                 index_col = 'DateTime')
df_whole = df.iloc[:,2:]
df_whole.index = pd.to_datetime(df_whole.index,format='%m/%d/%Y %H:%M').date

### Compute performance stat
## Reutrn related
# Cumulative Return
cumulative_return = df_whole.cumsum()
fig = plt.figure(figsize=[15, 16])
ax1 = fig.add_subplot(221)
ax1.plot(cumulative_return)
ax1.set_title("Cumulative Return",fontsize=20)

# Annualized Return
ax2 = fig.add_subplot(222)
Annualized_return = cumulative_return.iloc[-1,:].apply(lambda x:x * 252 / len(df_whole))
Annualized_return.plot(kind='bar',ax=ax2,rot=45)
ax2.set_title("Annualized Return",fontsize=20)
ax2.set_ylim(0.025,0.065)

# Annualized Volatility
ax3 = fig.add_subplot(223)
Annualized_vol = df_whole.std() * np.sqrt(252)
Annualized_vol.plot(kind='bar',ax=ax3,rot=45)
ax3.set_title("Annualized Volatility",fontsize=20)
ax3.set_ylim(0.05,0.065)

# Info ratio -- Here is defined as Return/vol
ax4 = fig.add_subplot(224)
Information_ratio = Annualized_return / Annualized_vol
Information_ratio.plot(kind='bar',ax=ax4,rot=45)
ax4.set_title("Information Ratio",fontsize=20)
ax4.set_ylim(0.5,1.1)
plt.tight_layout(pad=3,h_pad=1,w_pad=0.5)
plt.subplots_adjust(hspace=0.25)
## Drawdown - related        
running_max = np.maximum.accumulate(cumulative_return - 1)
running_max[running_max < 0] = 0
drawdown = (cumulative_return - 1) - running_max 

## plot DD curve
fig2 = plt.figure()
drawdown.plot()
for strat in drawdown.columns:
    plt.fill_between(drawdown.index,drawdown[strat],color='grey',alpha=0.2)
plt.title("Drawdown Curve",fontsize=20)
plt.tight_layout()
    
fig3 = plt.figure()
(cumulative_return - 1).plot()
for strat in drawdown.columns:
    plt.fill_between(drawdown.index,drawdown[strat],color='grey',alpha=0.2)
plt.title("Cumulative Return & Drawdown",fontsize=20)
plt.legend(loc='upper left')
plt.tight_layout()
    
# Largest 3 DD    
dd_dic = dict.fromkeys(df_whole.columns,[])
for colname, col in drawdown.items():
    drawdown_count = []
    tmp = []
    day_fall = 0
    day_recover = 0
    for i in range(len(col)):
        if col[i] < 0:
            tmp.append(col[i])
        if (col[i] == 0) or (i == (len(col) - 1)):
            if (len(tmp) != 0):
                day_fall = tmp.index(min(tmp)) + 1
                day_recover = len(tmp) + 1 - day_fall
                drawdown_count.append([min(tmp),day_fall,day_recover])
            tmp.clear()
    drawdown_count.sort(key=lambda x:x[0])
    dd_dic[colname] = list(itertools.chain.from_iterable(drawdown_count[:3])) ## make it falt
    
Mdd = pd.DataFrame(dd_dic).T
Mdd.columns = ['MDD','drough1','recover1','2DD','drough2','recover2','3DD','drough3','recover3']

### Other ratio
# win, lose ratio
win_ratio = df_whole[df_whole > 0].count() / len(df_whole)
lose_ratio = df_whole[df_whole < 0].count() / len(df_whole)

# median daily return, average daily return
median_return = df_whole.median()
average_return = df_whole.mean()


### Sort by IR
fig = plt.figure()
IR_sort = Information_ratio.sort_values()
IR_sort.plot(kind="bar",rot=0)
plt.ylim(0.5,1.1)

# pick 5 strategies
strat_chose = list(IR_sort.index[[0,6,12,18,23]])
df_chose = df_whole[strat_chose]

sns.set_palette(reversed(sns.color_palette("GnBu",5)),5)
fig4 = plt.figure(figsize=[15, 16])
plt.subplots_adjust(hspace =0.3)
ax1 = fig4.add_subplot(221)
ax1.plot(cumulative_return[strat_chose] - 1)
plt.legend(strat_chose)
ax1.set_title("Cumulative Return",fontsize=20)

# Annualized Return & Vol
ax2 = fig4.add_subplot(222)
Ret_Vol = pd.concat([pd.DataFrame(Annualized_return[strat_chose]).T,pd.DataFrame(Annualized_vol[strat_chose]).T])
Ret_Vol.index = ['Annualized Return','Annualized Volatility']
Ret_Vol.T.plot(kind='bar',ax=ax2,rot=0)
ax2.set_title("Annualized Return & Volatility",fontsize=20)
ax2.set_ylim(0.025,0.065)

# MDD
ax3 = fig4.add_subplot(223)
(-Mdd['MDD'][strat_chose]).plot(kind='bar',ax=ax3,rot=0)
ax3.set_title("Maximum Drawdown",fontsize=20)
ax3.set_ylim(0.03)

# Info ratio -- Here is defined as Return/vol, Also Return/MDD
ax4 = fig4.add_subplot(224)
Return_over_MDD = Annualized_return[strat_chose] / pd.DataFrame(-Mdd['MDD'][strat_chose]).T
IR_MDD = pd.concat([Return_over_MDD,pd.DataFrame(Information_ratio[strat_chose]).T])
IR_MDD.index = (["Return/MDD","IR"])
IR_MDD.T.plot.bar(ax=ax4,rot=0)
ax4.set_title("Return/MDD & Information Ratio",fontsize=20)
ax4.set_ylim(0.35,1.3)
plt.tight_layout(pad=3,h_pad=1,w_pad=0.5)
plt.subplots_adjust(hspace=0.25)

## plot DD curve
fig5 = plt.figure()
plt.plot(cumulative_return[strat_chose] - 1)
for strat in drawdown[strat_chose].columns:
    plt.fill_between(drawdown.index,drawdown[strat],color='grey',alpha=0.2)
plt.legend(strat_chose)    
plt.title("Cumulative Return & Drawdown",fontsize=20)
plt.tight_layout()

## MDD "speed"
fig6 = plt.figure()
Mdd['DD/drough'] = -Mdd['MDD']/Mdd['drough1']
Mdd['DD/recover'] = -Mdd['MDD']/Mdd['recover1']
Mdd.loc[strat_chose,['DD/drough','DD/recover']].plot(kind='bar',rot=0)
plt.title("Maximum Drawdown/drough & MDD/recover",fontsize=20)
plt.tight_layout()

# win, lose ratio
win_ratio_chose = df_chose[df_chose > 0].count() / len(df_chose)
lose_ratio_chose = df_chose[df_chose < 0].count() / len(df_chose)

# median daily return, average daily return
median_return_chose = df_chose.median()
average_return_chose = df_chose.mean()

