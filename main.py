import constant
import pytplot
import mission
import slib
import read
from astropy.time import Time


def main():

    time_range = ['2013-06-01','2013-06-02/12:00']
    rbsp_probes = ['a','b']
    resolution = 60

    t = Time(['2013-06-01 01:00','2013-06-01 02:00'], format='iso')
    tr = Time(['2013-06-01 00:00','2013-06-01 01:30'], format='iso')


    r_vars = list()
    for probe in rbsp_probes:
        r_vars.append(read.rbsp.orbit(time_range, probe, coord='gse', resolution=resolution))

    r_var = r_vars[0]
    data = slib.get_data(r_var)
    time = slib.get_time(r_var)
    settings = slib.get_setting(r_var)
    value = slib.get_setting(r_var, key='UNITS')
    time_var = slib.get_time_var(r_var)
    pytplot.tplot_names()


if __name__ == '__main__':
    main()