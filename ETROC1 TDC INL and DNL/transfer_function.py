import os
import sys
import csv
import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
'''
This script is used to encode the TOA, TOT, and Calibration transfer function of 63 Delay Cells TDC
@author: Wei Zhang
@date: Jan 31, 2019
@address: SMU Dallas, TX
'''
#================================================================================================#
## plot parameters
lw_grid = 0.5                   # grid linewidth
fig_dpi = 800                   # save figure's resolution
#================================================================================================#
## TOARaw_Transfer_Function: Encode TOA Raw data to 10-bit binary code.
#@param[in]: Data: TOA, TOT, and Calibration simulation data.
def TOARaw_Transfer_Function(Data):
    TOA_codeReg = []
    for i in xrange(len(Data)):                                     # fetch TOA Raw data
        if Data[i][3:66].count(1) > 1:
            print Data[i][3:66].index(1), "Wrong"
        else:
            TOARaw = Data[i][3:66].index(1)
        TOACntA = Data[i][68]<<2 | Data[i][67]<<1 | Data[i][66]     # TOA Counter A number
        TOACntB = Data[i][71]<<2 | Data[i][70]<<1 | Data[i][69]     # TOT Counter B number
        if Data[i][0] == 1:                                         # TOARawdata[62] = 1; How to choose CounterA and CounterB
            TOA_Code = ((TOACntB)<<1 | 0) * 63 + TOARaw + 1
        else:                                                       # TOARawdata[62] = 0;
            TOA_Code = (((TOACntA-1)<<1) | 1) * 63 + TOARaw + 1
        # print
        # print Data[i][0:1], TOARaw, TOACntA, TOACntB, TOA_Code
        TOA_codeReg += [TOA_Code]
    print len(TOA_codeReg)
    x = []
    for i in np.arange(0.4, 3.999, 0.001):
        x += [float(i)]
    print len(x)

    fig, ax = plt.subplots()                                        # Plot TOA transfer function
    ax.plot(x, TOA_codeReg, color='r',marker='X', linewidth=0.2, markersize=0.02, label='TOA Transfer Function')
    plt.title("63 Delay Cells TDC TOA Transfer Function Step = 1ps nominal", family="Times New Roman", fontsize=12)
    plt.xlabel("TOA_CK [ns]", family="Times New Roman", fontsize=10)
    plt.ylabel("Digital Code [bins]", family="Times New Roman", fontsize=10)
    plt.xticks(family="Times New Roman", fontsize=8)
    plt.yticks(family="Times New Roman", fontsize=8)
    plt.grid(linestyle='-.', linewidth=lw_grid)
    plt.legend(fontsize=8, edgecolor='green')

    axins = zoomed_inset_axes(ax, 20, loc=7)
    axins.plot(x[1000:1050], TOA_codeReg[1000:1050], color='r',marker='X', linewidth=0.5, markersize=0.8)
    mark_inset(ax, axins, loc1=3, loc2=4, fc="none", ec="0.6")
    plt.xticks(family="Times New Roman", fontsize=7)
    plt.yticks(family="Times New Roman", fontsize=7)
    plt.grid(linestyle='-.', linewidth=lw_grid)

    plt.savefig("TOA_Transfer_Function_1ps_nominal.pdf", dpi=fig_dpi, bbox_inches='tight')         # save figure
    plt.clf()
def main():
    Data
    TOARaw_Transfer_Function(Data)
    CalRaw_Transfer_Function(Data)
#================================================================================================#
if __name__ == '__main__':
    main()
