import os
import sys
import time
import math
import random
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
from matplotlib import gridspec
'''
This python script is used to estimate ETROC0 TDC INL and DNL
@author: Wei Zhang
@date: May 5, 2019
@address: SMU dallas, TX
'''
#======================================================================#
## plot parameters
lw_grid = 0.5                   # grid linewidth
fig_dpi = 800                   # save figure's resolution
#=============================================================================#
## time to digital converter function
# @param[in] time_interval: time interval
# @param[in] Tfr time of 63 delay cells
# @param[in] Trf time of 63 delay cells
def time_to_digital(time_interval, Tfr_Delay_Cell, Trf_Delay_Cell):
    sum = 0
    digital_code = 0
    for i in range(700):
        Delay_Cell_Time = 0
        if sum <= time_interval:
            digital_code += 1
            if (i/63)%2 == 0:
                if i%2 == 0:
                    Delay_Cell_Time += Tfr_Delay_Cell[i%63]
                else:
                    Delay_Cell_Time += Trf_Delay_Cell[i%63]
            else:
                if i%2 == 0:
                    Delay_Cell_Time += Tfr_Delay_Cell[i%63]
                else:
                    Delay_Cell_Time += Trf_Delay_Cell[i%63]
            sum += Delay_Cell_Time
    return digital_code-1
#=============================================================================#
## digital to time interval converter function
# @param[in] time_interval: time interval
# @param[in] Tfr time of 63 delay cells
# @param[in] Trf time of 63 delay cells
def digital_to_time(digital_code, Tfr_Delay_Cell, Trf_Delay_Cell):
    sum = 0
    Delay_Cell_Time = 0
    for i in range(digital_code):
        if (i/63)%2 == 0:
            if i%2 == 0:
                Delay_Cell_Time += Tfr_Delay_Cell[i%63]
            else:
                Delay_Cell_Time += Trf_Delay_Cell[i%63]
        else:
            if i%2 == 0:
                Delay_Cell_Time += Tfr_Delay_Cell[i%63]
            else:
                Delay_Cell_Time += Trf_Delay_Cell[i%63]
    return Delay_Cell_Time
#=============================================================================#
## Ideal transfer function
def Ideal_Transfer_Function(average_bin_size):
    digital_code = []
    sum = 0
    single_digital_code = 0
    time_interval = np.arange(0, 200, 0.1)
    print(time_interval)
    for j in range(len(time_interval)):
        for i in range(700):
            if sum <= time_interval[j]:
                single_digital_code += 1
                sum += average_bin_size
        digital_code += [single_digital_code - 1]
    return time_interval, digital_code

#=============================================================================#
## TDC INL Calculate
#@param[in] average_bin_size: calibrated average bin size
#@param[in] Tfr_Delay_Cell: small bin size of 63 delay cell
#@param[in] Trf_Delay_Cell: big bin size of 63 delay cells
def TDC_INL_Calculate(Tfr_Delay_Cell, Trf_Delay_Cell,):
    period = len(Tfr_Delay_Cell)+len(Trf_Delay_Cell);
    average_bin_size=(np.sum(Tfr_Delay_Cell)+np.sum(Trf_Delay_Cell))/period
    digital_code_stop = time_to_digital(12500, Tfr_Delay_Cell, Trf_Delay_Cell)
    digital_code = np.arange(digital_code_stop)
#    offset0 = digital_to_time(0, Tfr_Delay_Cell, Trf_Delay_Cell)
#    offset1 = digital_to_time(1, Tfr_Delay_Cell, Trf_Delay_Cell)
#    print("INL test:",offset0,offset1)
    TDC_INL = []
    for i in range(1, len(digital_code)):
        TDC_INL += [abs(digital_to_time(digital_code[i], Tfr_Delay_Cell, Trf_Delay_Cell)/average_bin_size - i)]
    return np.amax(TDC_INL)

#=============================================================================#
## TDC INL Calculate
#@param[in] average_bin_size: calibrated average bin size
#@param[in] Tfr_Delay_Cell: small bin size of 63 delay cell
#@param[in] Trf_Delay_Cell: big bin size of 63 delay cells
#=============================================================================#
## calibration bin size
#@param[in] num: average times
#@param[in] Tfr_Delay_Cell: small bin size of 63 delay cell
#@param[in] Trf_Delay_Cell: big bin size of 63 delay cells
def calibration_bin_size(num, Tfr_Delay_Cell, Trf_Delay_Cell):
    sigma = 200                                                     # normal distribution sigam = 30ps
    rand_data = []
    for i in range(num):
        mu = random.uniform(1, 10) * 1000
        # print mu
        rand_data += [mu] #[np.random.normal(mu, sigma, 1)]               # generate data. Datao's comment: do not need gaussian distribution anymore.
    digital_interval = []
    square_digital_interval = []
    for i in range(num):
        an_interval = time_to_digital(rand_data[i]+3125.0, Tfr_Delay_Cell, Trf_Delay_Cell) - time_to_digital(rand_data[i], Tfr_Delay_Cell, Trf_Delay_Cell)
        digital_interval += [an_interval]
        square_digital_interval += [an_interval*an_interval]
    # print digital_interval
#    square_digital_interval = map(square_number, digital_interval)
    average_bin_size = np.mean(digital_interval) * 3125.0 / np.mean(square_digital_interval)
    return average_bin_size

#=============================================================================#
def TOA_Transfer_Function(Tfr_Delay_Cell, Trf_Delay_Cell):
#    time_stop = digital_to_time(126, Tfr_Delay_Cell, Trf_Delay_Cell)
    time_stop = 12500   #100 ps
    digital_code_stop = time_to_digital(time_stop, Tfr_Delay_Cell, Trf_Delay_Cell)
#    digital_code = np.arange(digital_code_stop)
    TOA_digital = []
    TOA_analog =[]
    for i in range(int(time_stop*20)): #0.05 ps step
        digital_code = time_to_digital(i/20.0, Tfr_Delay_Cell, Trf_Delay_Cell)
        TOA_digital += [digital_code]
        TOA_analog += [i/20.0]

    fig, ax = plt.subplots()                                        # Plot TOA transfer function
    ax.plot(TOA_analog, TOA_digital, color='r',marker='X', linewidth=0.2, markersize=0.02, label='TOA Transfer Function')
    plt.title("TOA Transfer Function including mismatch effect", family="Times New Roman", fontsize=12)
    plt.xlabel("TOA time [ps]", family="Times New Roman", fontsize=10)
    plt.ylabel("Digital Code [bins]", family="Times New Roman", fontsize=10)
    plt.xticks(family="Times New Roman", fontsize=8)
    plt.yticks(family="Times New Roman", fontsize=8)
    plt.grid(linestyle='-.', linewidth=lw_grid)
    plt.legend(fontsize=8, edgecolor='green')

    axins = zoomed_inset_axes(ax, 50, loc=7)
    axins.plot(TOA_analog[1000:2500], TOA_digital[1000:2500], color='r',marker='X', linewidth=0.5, markersize=0.8)
    mark_inset(ax, axins, loc1=3, loc2=4, fc="none", ec="0.6")
    plt.xticks(family="Times New Roman", fontsize=7)
    plt.yticks(family="Times New Roman", fontsize=7)
    plt.grid(linestyle='-.', linewidth=lw_grid)

    plt.savefig("TOA_Transfer_Function.png", dpi=fig_dpi, bbox_inches='tight')         # save figure

    plt.clf()

def TOA_bin_size_bar(Tfr_Delay_Cell, Trf_Delay_Cell):
    TOA_binsize = []
    TOA_binnum = []
    for i in range(126):
        TOA_binsize += [Trf_Delay_Cell[i>>1] if (i%2==1) else Tfr_Delay_Cell[i>>1]]
        TOA_binnum += [i]

    fig, ax = plt.subplots()                                        # Plot TOA transfer function
    ax.bar(TOA_binnum, TOA_binsize, color='r', bottom = 0, linewidth=0.2, label='TOA bin size')
    plt.title("Bin size including mismatch effect", family="Times New Roman", fontsize=12)
    plt.xlabel("bin# [bins]", family="Times New Roman", fontsize=10)
    plt.ylabel("bin size [ps]", family="Times New Roman", fontsize=10)
    plt.xticks(family="Times New Roman", fontsize=8)
    plt.yticks(family="Times New Roman", fontsize=8)
    plt.ylim(bottom=16,top=24)
    plt.grid(linestyle='-.', linewidth=lw_grid)
    plt.legend(fontsize=8, edgecolor='green')

    plt.savefig("TOA_bins.png", dpi=fig_dpi, bbox_inches='tight')         # save figure

    plt.clf()


#=============================================================================#
## main function
def main():
    ## the Tfr_mu, Tfr_mu and Tfr_sigma, Tfr_sigma are generated from Monte Carlo simulation
    Tfr_mu = 17.5              # The mu of Tfr is about 18 ps
    Tfr_sigma = 0.149           # The sigma of Tfr is about 0.149 ps

    Trf_mu = 22.5              # The mu of Trf is about 21 ps
    Trf_sigma = 0.2575          # The sigma of Trf is about 0.5 ps

    INL_max_array = []
    for i in range(400):
    # generate 63 delay cell with different Tfr and Trf due to mismatch
        Tfr_Delay_Cell = np.random.normal(Tfr_mu, Tfr_sigma, 63)
        Trf_Delay_Cell = np.random.normal(Trf_mu, Trf_sigma, 63)
        #print(iTfr_delay_cell,Trf_delay_cell)
        actual_bin_size = (np.mean(Tfr_Delay_Cell) + np.mean(Trf_Delay_Cell))/2.0
        INL_max = TDC_INL_Calculate(Tfr_Delay_Cell, Trf_Delay_Cell)
        #print(i, " odd bin = ",np.mean(Tfr_Delay_Cell), " even bin = ",np.mean(Trf_Delay_Cell), " overall mean = ",actual_bin_size, " max INL = ", INL_max)
        print(i, " max INL = ", INL_max)
        INL_max_array += [INL_max]

        hist_bins = np.arange(0, 0.5, 0.005)
        mu = np.mean(INL_max_array)
        sigma = np.std(INL_max_array)
        plt.hist(INL_max_array, bins=hist_bins, density=False, color='r', label="entries=%d\n$\mu=%.5e$\n$\sigma=%.4e$\n"%(len(INL_max_array),mu,sigma))
    #        plt.vlines(mu, 0, 140, colors='b', linewidth= 0.8, linestyles='-.', label='actual bin size = %.4f'%actual_bin_size)
        plt.xlabel("INL", family="Times New Roman", fontsize=10)
        plt.ylabel("Counts", family="Times New Roman", fontsize=10)
#        plt.ylim(0, count_limit)
        plt.xticks(family="Times New Roman", fontsize=8)
        plt.yticks(family="Times New Roman", fontsize=8)
        plt.grid(linestyle='-.', linewidth=lw_grid)
        plt.legend(fontsize=6, edgecolor='green')
        plt.savefig("INL_distribution.png", dpi=fig_dpi, bbox_inches='tight')         # save figure
        plt.clf()

#=============================================================================#
if __name__ == "__main__":
    main()
