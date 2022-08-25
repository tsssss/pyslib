# from mission import utils
from asyncore import read
from mission.utils import check_file_existence
import constant
import pytplot
import mission
import slib
import read


def main():

    time_range = ['2013-06-01','2013-06-02/12:00']
    rbsp_probes = ['a','b']
    resolution = 60

    r_vars = list()
    for probe in rbsp_probes:
        r_vars.append(read.rbsp.orbit(time_range, probe, coord='gse', resolution=resolution))

    r_var = r_vars[0]
    data = slib.get_data(r_var)
    settings = slib.get_setting(r_var)
    value = slib.get_setting(r_var, key='UNITS')
    pytplot.tplot_names()


if __name__ == '__main__':
    main()