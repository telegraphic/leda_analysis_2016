from leda_cal.analog import *

def interp_cplx(x_new, x_orig, d_orig):
    re = np.interp(x_new, x_orig, np.real(d_orig))
    im = np.interp(x_new, x_orig, np.imag(d_orig))
    d_new = re + 1j * im
    return d_new

def s2p_interp(f_leda, ant_s11_file, lna_s11_file):
    
    ant = AnalogComponent()
    lna = AnalogComponent()
    ant.read_s2p(ant_s11_file)
    lna.read_s2p(lna_s11_file)

    f  = ant.freq * 1e3
    ra = ant.s11
    rl = lna.s11
    
    ra_ = interp_cplx(f_leda, f, ra)
    rl_ = interp_cplx(f_leda, f, rl)
    
    return ra_, rl_
    

f_leda = np.linspace(0, 98.304, 4096)
i0 = closest(f_leda, 30)
i1 = closest(f_leda, 85)
f_leda = f_leda[i0:i1]


##################
## ANT + LNA
##################

a252x_s11 = s2p_interp(f_leda, 'field-data/field-jan-13/vna-ant252-a2-s11-3.s2p',
           'fee-vna/dcp-a2-s11.s2p')

a254x_s11 = s2p_interp(f_leda, 'field-data/field-jan-13/vna-ant254-c2-s11.s2p',
           'fee-vna/dcp-c2-s11.s2p')

a255x_s11 = s2p_interp(f_leda, 'field-data/field-jan-13/vna-ant255-d2-s11.s2p',
           'fee-vna/dcp-d2-s11.s2p')

a252y_s11 = s2p_interp(f_leda, 'field-data/field-jan-13/vna-ant252-a2-s11-3.s2p',
           'fee-vna/dcp-a2-s11.s2p')

a254y_s11 = s2p_interp(f_leda, 'field-data/field-jan-13/vna-ant254-c2-s11.s2p',
           'fee-vna/dcp-c2-s11.s2p')

a255y_s11 = s2p_interp(f_leda, 'field-data/field-jan-13/vna-ant255-d2-s11.s2p',
           'fee-vna/dcp-d2-s11.s2p')



ant_s11_dict = {
    'f'    : f_leda,
    'a252x': {'ra': a252x_s11[0], 'rl': a252x_s11[1]},
    'a252y': {'ra': a252y_s11[0], 'rl': a252y_s11[1]},
    'a254x': {'ra': a254x_s11[0], 'rl': a254x_s11[1]},
    'a254y': {'ra': a254y_s11[0], 'rl': a254y_s11[1]},
    'a255x': {'ra': a255x_s11[0], 'rl': a255x_s11[1]},
    'a255y': {'ra': a255y_s11[0], 'rl': a255y_s11[1]},
    }

hkl.dump(ant_s11_dict, 'cal_data/vna_calibration.hkl')


###########
## BALUN
###########
import skrf as rf

balun = rf.Network()
balun.read_touchstone('component-data/ADT4-6T___Plus25degC.S3P')
ff  = balun.frequency.f / 1e6
s12 = balun.s12.s_db[:, 0,0]
s13 = balun.s13.s_db[:, 0,0]

L = 20*np.log10( 10**(s12/20.0) + 10**(s13/20.0) )

plt.plot(ff, L)
plt.xlim(20, 90)
plt.ylim(-1, -0.5)
plt.xlabel("Frequency [MHz]")
plt.ylabel("Balun loss [dB]")
hkl.dump({'f': ff, 'L' : L}, 'cal_data/balun_loss_single.hkl')

L_interp = np.interp(f_leda, ff, L)

balun_loss_dict = {
    'f'    : f_leda,
    'a252x': L_interp,
    'a252y': L_interp,
    'a254x': L_interp,
    'a254y': L_interp,
    'a255x': L_interp,
    'a255y': L_interp,
    }

hkl.dump(balun_loss_dict, 'cal_data/balun_loss.hkl')