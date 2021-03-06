#!/usr/bin/env python
"""
# 06_plot_rfi.py

Plots the RFI flags

"""
import seaborn as sns
import tables as tb
from leda_cal.skymodel import *
from leda_cal.leda_cal import *
from leda_cal.dpflgr import *

from scipy.stats import kurtosis

sns.set_style('ticks')
sns.set_context("paper",font_scale=1.5)

def quicklook(filename):
    h5 = tb.open_file(filename)

    T_ant = apply_calibration(h5)
    f_leda = T_ant['f']
    
    ant_ids = ['252A']
    pol_id  = 'y'
      
    print("Plotting...")
    fig, axes = plt.subplots(figsize=(12, 6), nrows=1, ncols=1)
    #plt.suptitle(h5.filename)
    
    lst_stamps = T_ant['lst']
    utc_stamps = T_ant['utc']
    xlims = (f_leda[0], f_leda[-1])
    #ylims = mdates.date2num((T_ant['utc'][0], T_ant['utc'][-1]))
    #hfmt = mdates.DateFormatter('%m/%d %H:%M')
    ylims = (T_ant['lst'][0], T_ant['lst'][-1])
    T_flagged = T_ant[ant_ids[0]]
    #T_flagged = np.fft.fft(T_flagged, axis=0)
    #T_flagged -= T_flagged.mean(axis=0)
    #T_flagged = 10*np.log10(np.abs(np.fft.ifft(T_flagged)))

    T_flagged = rfi_flag(T_flagged, thr_f=0.2, thr_t=0.2, rho=1.5,
             bp_window_f=16, bp_window_t=16, 
             max_frac_f=0.5, max_frac_t=0.5)

    im = plt.imshow(T_flagged, # / np.median(xx, axis=0), 
               cmap='magma_r', aspect='auto',
               interpolation='nearest',
               #clim=(1000, 10000),
               extent=(xlims[0], xlims[1], ylims[1], ylims[0])
               )
    plt.title(ant_ids[0])
    plt.xlabel("Frequency [MHz]")

    plt.ylabel("LST [hr]")
    plt.colorbar()
    plt.savefig("figures/rfi-flagged.pdf")
    plt.show()
    
    plt.figure()
    #plt.plot(f_leda, np.sum(T_flagged.mask, axis=0).astype('float') / T_flagged.mask.shape[0], label='total')
    day = T_flagged[0:2000].mask
    night = T_flagged[2250:2750].mask
    plt.plot(f_leda, np.sum(night, axis=0).astype('float') / night.shape[0], label='night')
    plt.plot([0])
    plt.plot(f_leda, np.sum(day, axis=0).astype('float') / day.shape[0], label='day')
    plt.xlim(40, 85)
    plt.ylim(-0.025, 0.25)
    
    plt.xlabel("Frequency [MHz]")
    plt.ylabel("Flagged fraction")
    plt.minorticks_on()
    plt.legend(frameon=True, loc=2)
    plt.tight_layout()
    plt.savefig("figures/rfi-fraction.pdf")
    plt.show()
    
    plt.figure()
    plt.plot(f_leda, kurtosis(T_flagged, axis=0))
    plt.ylabel("Kurtosis")
    plt.xlabel("Frequency [MHz]")
    plt.xlim(40, 85)
    plt.ylim(-50, 1600)
    plt.minorticks_on()
    plt.show()
    
    plt.figure()
    

if __name__ == "__main__":
    
    import sys
    try:
        filename = sys.argv[1]
    except:
        print "USAGE: ./quicklook.py filename_of_hdf5_observation"
        exit()
    
    quicklook(filename)
