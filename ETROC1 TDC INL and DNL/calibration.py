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
This python script for calibration process study
@author: Datao Gong
@date: July 3, 2019
@address: SMU dallas, TX
'''

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

def digital_to_time2(digital_code, delayArrayInt):
    return delayArrayInt[digital_code]

def time_to_digital2(time_interval, delayArrayInt):
    low = 0;
    high = len(delayArrayInt)-1;
    digital_code = -1
    if time_interval >= 0 and time_interval <= delayArrayInt[high]:
        #binary search
        while low < high :
            current = (low + high)/2
            print(low,current,high)
            if delayArrayInt[current] >= delayArrayInt[low]:
                low = current
            elif delayArrayInt[current] < delayArrayInt[high]:
                high = current
        digital_code = low
    return digital_code


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

    TDC_bins = int(13000/actual_bin_size) #not more than 13 ns
    delayArrayInt = []
    delayArrayInt +=[0.0]
#    previousDelay = 0
    for i in range(1, TDC_bins):
        if i%2 == 1:
            delayArrayInt += [delayArrayInt[i-1] + Tfr_Delay_Cell[((i-1)%126)>>1]]
        else:
            delayArrayInt += [delayArrayInt[i-1] + Trf_Delay_Cell[((i-1)%126-1)>>1]]
        if i<127:
            if i == 0:
                print(i,delayArrayInt[i])
            else :
                print(i,delayArrayInt[i],delayArrayInt[i] - delayArrayInt[i-1])


    for i in range(127):
        old = digital_to_time(i, Tfr_Delay_Cell, Trf_Delay_Cell)
        new = digital_to_time2(i, delayArrayInt)
        print(i,old,new, old-new)

#=============================================================================#
if __name__ == "__main__":
    main()
