"""
# useful.py

Useful and miscellaneous utilities / fits / formulas etc that I use all the time.
"""

import numpy as np
import pylab as plt
from scipy.signal import wiener
from numpy import fft

def smooth(list, degree=5):
    """ Apply a Gaussian smoothing function """
    window = degree * 2 - 1
    weight = np.array([1. / np.exp(16. * i * i / window / window) for i in np.arange(-degree + 1, degree)])
    extended = np.r_[[list[0]] * (degree - 1), list, [list[-1]] * degree]
    smoothed = np.convolve(weight / weight.sum(), extended, mode='same')
    return smoothed[degree - 1:-degree]

def rebin(d, n_x, n_y=None):
    """ Rebin data
    :param d: data
    :param n_x: number of bins in x dir to rebin into one
    :param n_y: number of bins in y dir to rebin into one
    :return: rebinned data
    """

    if d.ndim == 2:
        d = d[:int(d.shape[0] / n_x) * n_x, :int(d.shape[1] / n_y) * n_y]
        d = d.reshape((d.shape[0] / n_x, n_x, d.shape[1] / n_y, n_y))
        d = d.mean(axis=3)
        d = d.mean(axis=1)
    elif d.ndim == 1:
        d = d[:int(d.shape[0] / n_x) * n_x]
        d = d.reshape((d.shape[0] / n_x, n_x))
        d = d.mean(axis=1)
    else:
        raise RuntimeError("Only NDIM <= 2 supported")
    return d

def fit_poly(x, y, n=5, log=True, print_fit=False):
    """ Fit a polynomial to x, y data 
    
    x (np.array): x-axis of data (e.g. frequency)
    y (np.array): y-axis of data (e.g temperature)
    n (int): number of terms in polynomial (defaults to 5)
    """
    
    x, y = np.ma.array(x), np.ma.array(y)
    
    x_g = x
    x = np.ma.array(x, mask=y.mask).compressed()
    y = y.compressed()
    if log:
        yl = np.log10(y)
    else:
        yl = y
    
    fit = np.polyfit(x, yl, n)
    if print_fit:
        print fit
    p = np.poly1d(fit)
    
    if log:
        return 10**(p(x_g))
    else:
        return p(x_g)

def fourier_fit(x, n_predict, n_harmonics):
    """ Fit a Fourier series to data
    
    Args:
        x: data to fit
        n_predict: next N data points to predict
        n_harmonics: number of harmonics to compute
    
    Notes:
    From github gist https://gist.github.com/tartakynov/83f3cd8f44208a1856ce
    """
    n = x.size
    n_harm = n_harmonics            # number of harmonics in model
    t = np.arange(0, n)
    p = np.polyfit(t, x, 1)         # find linear trend in x
    x_notrend = x - p[0] * t        # detrended x
    x_freqdom = fft.fft(x_notrend)  # detrended x in frequency domain
    f = fft.fftfreq(n)              # frequencies
    indexes = range(n)
    # sort indexes by frequency, lower -> higher
    indexes.sort(key = lambda i: np.absolute(f[i]))
 
    t = np.arange(0, n + n_predict)
    restored_sig = np.zeros(t.size)
    for i in indexes[:1 + n_harm * 2]:
        ampli = np.absolute(x_freqdom[i]) / n   # amplitude
        phase = np.angle(x_freqdom[i])          # phase
        restored_sig += ampli * np.cos(2 * np.pi * f[i] * t + phase)
    return (restored_sig + p[0] * t)

def poly_fit(x, y, n=5, log=True, print_fit=False):
    return fit_poly(x, y, n, log, print_fit)

def db(x): 
    """ Convert linear to dB """
    return 10*np.log10(x)

def lin(x):
    """ Convert dB to linear """
    return 10.0**(x / 10.0)

def closest(xarr, val):
    """ Return the index of the closest in xarr to value val """
    idx_closest = np.argmin(np.abs(xarr - val))
    return idx_closest

def trim(x, y, x_start, x_stop):
    """ Trim length of vectors x and y to given bounds
    
    Args:
        x (np.array): array of x values (e.g. freq)
        y (np.array): array of y values
        x_start (float): Minimum x value (start of trim)
        x_stop (float): Maximum x value (end of trim)
    """
    i0 = closest(x, x_start)
    i1 = closest(x, x_stop)
    
    x = x[i0:i1]
    y = y[i0:i1]
    
    return x, y

def plt_lab(x="Frequency [MHz]", y="Temperature [K]"):
    """ Add default plot labels and a legend """
    plt.xlabel(x)
    plt.ylabel(y)
    plt.legend()

def plot_waterfall(d, freqs, lsts, t_unit='hr', f_unit='MHz',
                   raster=True):
    """ Plot imshow with LST and frequency on axis
    :param d: data
    :param freqs: frequency array
    :param lsts: LST array
    :param n_fticks: Number of ticks on freq axis
    :param n_lticks: NUmber of ticks on LST axis
    """

    plt.imshow(d, aspect='auto', interpolation='none',
               rasterized=raster,
               extent=(freqs[0], freqs[-1], lsts[0], lsts[-1]))
    plt.xlabel("Frequency [%s]" % f_unit)
    plt.ylabel("Time [%s]" % t_unit)