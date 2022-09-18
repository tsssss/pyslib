import constant
import pytplot
import mission
import slib.manager as smg
import read
from astropy.time import Time
import slib.plot as spl
import matplotlib as mpl


def main():

    time_range = ['2013-06-01','2013-06-02/12:00']
    rbsp_probes = ['a','b']
    resolution = 60

    ae_var = read.omni.ae(time_range)
    spl.plot(ae_var)

    r_vars = list()
    for probe in rbsp_probes:
        r_vars.append(read.rbsp.orbit(time_range, probe, coord='gsm', resolution=resolution))
    

    r_var = r_vars[0]

    pytplot.tplot_names()


if __name__ == '__main__':
    main()