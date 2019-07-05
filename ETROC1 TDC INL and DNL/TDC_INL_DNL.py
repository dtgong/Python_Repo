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
def TDC_INL_Calculate(Tfr_Delay_Cell, Trf_Delay_Cell, filename):
    period = len(Tfr_Delay_Cell)+len(Trf_Delay_Cell);
    average_bin_size=(np.sum(Tfr_Delay_Cell)+np.sum(Trf_Delay_Cell))/period

    TDC_INL = []
    digital_code_stop = time_to_digital(12500, Tfr_Delay_Cell, Trf_Delay_Cell)
    digital_code = np.arange(digital_code_stop)
#    offset0 = digital_to_time(0, Tfr_Delay_Cell, Trf_Delay_Cell)
#    offset1 = digital_to_time(1, Tfr_Delay_Cell, Trf_Delay_Cell)
#    print("INL test:",offset0,offset1)

    for i in range(1, len(digital_code)):
        TDC_INL += [digital_to_time(digital_code[i], Tfr_Delay_Cell, Trf_Delay_Cell)/average_bin_size - i]

    plt.plot(digital_code[1:], TDC_INL, color='r',marker='X', linewidth=0.5, markersize=0.8, label='TDC_INL')
    plt.title("TDC INL Estimation", family="Times New Roman", fontsize=12)
    plt.xlabel("Digital Code [bins]", family="Times New Roman", fontsize=10)
    plt.ylabel("TDC INL [LSB]", family="Times New Roman", fontsize=10)
    # plt.ylim(-1,1)
    plt.xticks(family="Times New Roman", fontsize=8)
    plt.yticks(family="Times New Roman", fontsize=8)
    plt.legend(fontsize=8, edgecolor='green')
    plt.grid(linestyle='-.', linewidth=lw_grid)
    plt.savefig("TDC_INL_Estimate_%s.png"%filename, dpi=fig_dpi)
    plt.clf()

#=============================================================================#
## TDC INL Calculate
#@param[in] average_bin_size: calibrated average bin size
#@param[in] Tfr_Delay_Cell: small bin size of 63 delay cell
#@param[in] Trf_Delay_Cell: big bin size of 63 delay cells
def TDC_Error_Calculate(average_bin_size1,average_bin_size2, Tfr_Delay_Cell, Trf_Delay_Cell, filename):

    period = len(Tfr_Delay_Cell)+len(Trf_Delay_Cell);
    ideal_bin_size=(np.sum(Tfr_Delay_Cell)+np.sum(Trf_Delay_Cell))/period

    digital_code_stop = time_to_digital(12500, Tfr_Delay_Cell, Trf_Delay_Cell)
    digital_code = np.arange(digital_code_stop)
    TDC_Error1 = []
    TDC_Error2 = []
    for i in range(1, len(digital_code)):
        code_i = digital_to_time(digital_code[i], Tfr_Delay_Cell, Trf_Delay_Cell)/ideal_bin_size
        TDC_Error1 += [i*average_bin_size1/ideal_bin_size-code_i]
        TDC_Error2 += [i*average_bin_size2/ideal_bin_size-code_i]

    plt.plot(digital_code[1:], TDC_Error1, color='r',marker='.', linewidth=0.5, markersize=0.8, label='TDC_INL(bin size=$\mu+$)')
    plt.plot(digital_code[1:], TDC_Error2, color='b',marker='+', linewidth=0.5, markersize=0.8, label='TDC_INL(bin size=$\mu-$)')

#    plt.plot(digital_code[1:], TDC_Error1, color='r',marker='.', linewidth=0.5, markersize=0.8, label='TDC_INL(bin size=$\mu+\sigma$)')
#    plt.plot(digital_code[1:], TDC_Error2, color='b',marker='+', linewidth=0.5, markersize=0.8, label='TDC_INL(bin size=$\mu-\sigma$)')
    plt.title("TDC Error Estimation", family="Times New Roman", fontsize=12)
    plt.xlabel("Digital Code [bins]", family="Times New Roman", fontsize=10)
    plt.ylabel("TDC Error [LSB]", family="Times New Roman", fontsize=10)
    # plt.ylim(-1,1)
    plt.xticks(family="Times New Roman", fontsize=8)
    plt.yticks(family="Times New Roman", fontsize=8)
    plt.legend(fontsize=8, edgecolor='green')
    plt.grid(linestyle='-.', linewidth=lw_grid)
    plt.savefig("TDC_Error_Estimate_%s.png"%filename, dpi=fig_dpi)
    plt.clf()

#=============================================================================#
## TDC DNL Calculate
#@param[in] average_bin_size: calibrated average bin size
#@param[in] Tfr_Delay_Cell: small bin size of 63 delay cell
#@param[in] Trf_Delay_Cell: big bin size of 63 delay cells
#def TDC_DNL_Calculate(average_bin_size, Tfr_Delay_Cell, Trf_Delay_Cell,filename):
def TDC_DNL_Calculate(Tfr_Delay_Cell, Trf_Delay_Cell,filename):
    period = len(Tfr_Delay_Cell)+len(Trf_Delay_Cell);
    average_bin_size=(np.sum(Tfr_Delay_Cell)+np.sum(Trf_Delay_Cell))/period
    print("TDC DNL Test:",period,average_bin_size)

    TDC_DNL = []
    digital_code_stop = time_to_digital(12500, Tfr_Delay_Cell, Trf_Delay_Cell)
    digital_code = np.arange(digital_code_stop)
    for i in range(1, len(digital_code)-1):
        TDC_DNL += [(digital_to_time(digital_code[i+1], Tfr_Delay_Cell, Trf_Delay_Cell) - digital_to_time(digital_code[i], Tfr_Delay_Cell, Trf_Delay_Cell))/average_bin_size - 1]

#    plt.plot(digital_code[1:len(digital_code)-1], TDC_DNL, color='r',marker='X', linewidth=0.5, markersize=0.8, label='TDC_DNL')
    plt.plot(digital_code[1:126], TDC_DNL[1:126], color='r',marker='X', linewidth=0.5, markersize=0.8, label='TDC_DNL')
    plt.title("TDC DNL Estimation", family="Times New Roman", fontsize=12)
    plt.xlabel("Digital Code [bins]", family="Times New Roman", fontsize=10)
    plt.ylabel("TDC DNL [LSB]", family="Times New Roman", fontsize=10)
    # plt.ylim(-1,1)
    plt.xticks(family="Times New Roman", fontsize=8)
    plt.yticks(family="Times New Roman", fontsize=8)
    plt.legend(fontsize=8, edgecolor='green')
    plt.grid(linestyle='-.', linewidth=lw_grid)
    plt.savefig("TDC_DNL_Estimate_%s.png"%filename, dpi=fig_dpi)
    plt.clf()
#=============================================================================#
def square_number(n):
    return n**2
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
    #Tfr_mu = 17.5              # The mu of Tfr is about 18 ps
    #Tfr_sigma = 0.149           # The sigma of Tfr is about 0.149 ps

    #Trf_mu = 22.5              # The mu of Trf is about 21 ps
    #Trf_sigma = 0.2575          # The sigma of Trf is about 0.5 ps

     # generate 63 delay cell with different Tfr and Trf due to mismatch
    #Tfr_delay_cell1 = np.random.normal(Tfr_mu, Tfr_sigma, 63)
    #Trf_delay_cell1 = np.random.normal(Trf_mu, Trf_sigma, 63)

    #print(Tfr_delay_cell1)
    #print(Trf_delay_cell1)
    Tfr_Delay_Cell =[   17.46436979, 17.64514691, 17.22891276, 17.38151871, 17.59673153, 17.57004398,
                        17.30576823, 17.57363873, 17.65842995, 17.43997753, 17.51952802, 17.46632766,
                        17.61067934, 17.58369251, 17.50256034, 17.45383192, 17.47427572, 17.46944105,
                        17.31367605, 17.70785314, 17.47392215, 17.586224  , 17.36662429, 17.41059645,
                        17.62669277, 17.57863361, 17.66402911, 17.08706272, 17.31453971, 17.78817216,
                        17.59732338, 17.66916401, 17.44664358, 17.50196759, 17.5247542 , 17.68764243,
                        17.61065373, 17.40585996, 17.68825923, 17.33416063, 17.68115867, 17.47337644,
                        17.55012399, 17.3642151,  17.73049835, 17.59311348, 17.49405889, 17.60655863,
                        17.34851706, 17.61177728, 17.23297776, 17.71174651, 17.78593393, 17.65107003,
                        17.69499815, 17.5279269,  17.42400105, 17.58324286, 17.47995094, 17.31980335,
                        17.49233167, 17.42837345, 17.48815093]
    Trf_Delay_Cell = [ 22.33028368, 22.32391012, 22.62676912, 22.65544682, 22.28389717, 22.09252298,
                        22.72990323, 22.47767238, 22.79322674, 22.1376733 , 22.7792733 , 22.8485769,
                        22.1439454 , 22.33670027, 22.19205996, 22.50799773, 22.74332537, 22.54486547,
                        22.50806381, 22.56663085, 22.37684813, 22.7192883 , 22.53489484, 22.51359694,
                        22.27706238, 22.43538083, 23.0429733 , 22.58682378, 22.83603497, 22.33199145,
                        22.87539627, 22.61624113, 22.87540568, 22.44722138, 22.50130897, 22.58409035,
                        22.22532164, 22.13092493, 22.38203755, 22.31517601, 22.35168176, 22.47330084,
                        22.9261207 , 22.57664296, 21.97286885, 22.60430571, 22.63458253, 22.74455538,
                        22.89715958, 22.17727303, 22.91210552, 22.14373665, 22.21016469, 22.61183618,
                        22.58516667, 22.31510465, 22.52366018, 22.36789634, 22.60859511, 22.36308051,
                        22.52227886, 22.5148577 , 21.91183464]

    actual_bin_size = (np.mean(Tfr_Delay_Cell) + np.mean(Trf_Delay_Cell))/2.0
    print("odd bin = ",np.mean(Tfr_Delay_Cell), " even bin = ",np.mean(Trf_Delay_Cell), " overall mean = ",actual_bin_size)

    # average_times = [1, 10, 100, 1000, 10000, 100000]
    # for i in xrange(len(average_times)):
    #     average_bin_size = calibration_bin_size(average_times[i], Tfr_Delay_Cell, Trf_Delay_Cell)
    #     print average_times[i], average_bin_size - actual_bin_size
    #     TDC_INL_Calculate(average_bin_size, Tfr_Delay_Cell, Trf_Delay_Cell, average_times[i])

#    TOA_Transfer_Function(Tfr_Delay_Cell, Trf_Delay_Cell)
#    TOA_bin_size_bar(Tfr_Delay_Cell, Trf_Delay_Cell)
    average_times = [1, 10, 100, 1000]
#    average_times = [1]
    average_bin = [[] for k in range(len(average_times))]

    # print average_bin
    for i in range(len(average_times)):
        for j in range(200):
            average_bin_size = calibration_bin_size(average_times[i], Tfr_Delay_Cell, Trf_Delay_Cell)
            average_bin[i] += [average_bin_size]
        print(i,len(average_bin[i]),np.mean(average_bin[i]),np.std(average_bin[i]))
            # print average_times[i], average_bin_size - actual_bin_size
    # print len(average_bin[0]), len(average_bin[1])

#    digital_interval=[]
#    for i in range(200):
#      digital_interval += [3125/average_bin[0][i]]
#    print("digital_interval",digital_interval)
#    plt.hist(digital_interval, bins=[154.5, 155.5, 156.5, 157.5, 158.5], density=False, color='r', label="Calibration digital code")
#    plt.title("Calibration Code Histogram", family="Times New Roman", fontsize=12)
#    plt.xlabel("Digital Code [bin]", family="Times New Roman", fontsize=10)
#    plt.ylabel("Counts", family="Times New Roman", fontsize=10)
#    plt.xticks(family="Times New Roman", fontsize=8)
#    plt.yticks(family="Times New Roman", fontsize=8)
#    plt.grid(linestyle='-.', linewidth=lw_grid)
#    plt.legend(fontsize=6, edgecolor='green')
#    plt.savefig("Calibration_digital_code_histogram.png", dpi=fig_dpi, bbox_inches='tight')         # save figure
#    plt.clf()



    hist_bins = np.arange(19.8, 20.2, 0.0025)
    print(hist_bins)
    TDC_DNL_Calculate(Tfr_Delay_Cell, Trf_Delay_Cell,"1a")
    TDC_INL_Calculate(Tfr_Delay_Cell, Trf_Delay_Cell, "update")

    for i in range(len(average_times)):
        mu, sigma = norm.fit(average_bin[i])
        print(mu, sigma)
        if i == 0:
            TDC_Error_Calculate(3125/156.0,3125/157.0,Tfr_Delay_Cell, Trf_Delay_Cell, average_times[i])
        else:
            TDC_Error_Calculate(mu+sigma,mu-sigma,Tfr_Delay_Cell, Trf_Delay_Cell, average_times[i])
        # plt.subplot(gs[0])
        print("bins:",hist_bins)
        plt.hist(average_bin[i], bins=hist_bins, density=False, color='r', label="entries=%d\n$\mu=%.5e$\n$\sigma=%.4e$\n"%(len(average_bin[i]),mu,sigma))
        bottom,top = plt.ylim()
        plt.vlines(actual_bin_size, bottom, top, colors='g', linewidth= 0.8, linestyles='-.', label='actual bin size = %.4f'%actual_bin_size)
#        plt.vlines(mu, 0, 140, colors='b', linewidth= 0.8, linestyles='-.', label='actual bin size = %.4f'%actual_bin_size)
        plt.xlabel("Calibration Bin Size", family="Times New Roman", fontsize=10)
        plt.ylabel("Counts", family="Times New Roman", fontsize=10)
#        plt.ylim(0, count_limit)
        plt.xticks(family="Times New Roman", fontsize=8)
        plt.yticks(family="Times New Roman", fontsize=8)
        plt.grid(linestyle='-.', linewidth=lw_grid)
        plt.legend(fontsize=6, edgecolor='green')
        plt.savefig("Calibration_Bin_Size_histogram_%d.png"%average_times[i], dpi=fig_dpi, bbox_inches='tight')         # save figure
        plt.clf()



    # time_interval1 = []
    # digital_code1 = []
    # time_range = np.arange(0,200,0.1)
    # for i in xrange(len(time_range)):
    #     digital_code1 += [time_to_digital(time_range[i], Tfr_Delay_Cell, Trf_Delay_Cell)]
    # time_interval1 = time_range
    # time_interval, digital_code = Ideal_Transfer_Function(average_bin_size)
    #
    # plt.plot(time_interval1, digital_code1, color='b',marker='X', linewidth=0.2, markersize=0.02, label='Actual Transfer Function')
    # plt.plot(time_interval, digital_code, color='r',marker='X', linewidth=0.2, markersize=0.02, label='Ideal Transfer Function')
    # plt.title("TDC INL Estimate", family="Times New Roman", fontsize=12)
    # plt.xlabel("Time interval [ps]", family="Times New Roman", fontsize=10)
    # plt.ylabel("Digital code", family="Times New Roman", fontsize=10)
    # plt.xticks(family="Times New Roman", fontsize=8)
    # plt.yticks(family="Times New Roman", fontsize=8)
    # plt.legend(fontsize=8, edgecolor='green')
    # plt.grid(linestyle='-.', linewidth=lw_grid)
    # plt.savefig("TDC_Transfer.pdf", dpi=fig_dpi)
    # plt.clf()
    #
    # TDC_INL_Calculate(average_bin_size, Tfr_Delay_Cell, Trf_Delay_Cell)
    # TDC_DNL_Calculate(average_bin_size, Tfr_Delay_Cell, Trf_Delay_Cell)
    # print "Ok!"
#=============================================================================#
if __name__ == "__main__":
    main()
