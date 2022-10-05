from turtle import width
import pytplot
import read
import system.plot as spl
import mission
import system.manager as smg
import matplotlib.pyplot as plt
import numpy as np



def main():

    time_range = ['2013-06-01','2013-06-02/12:00']
    time_range = ['2017-03-01','2017-04-01']
    rbsp_probes = ['a','b']
    probe = 'a'
    resolution = 60


    var_vector = read.ml.sw_v(time_range, coord='gsm')
    var_scalar = read.ml.sw_n(time_range)
    var_spec = read.ml.rbsp_en_spec(time_range, probe=probe, species='o')
    energys = smg.get_data(smg.get_setting(var_spec,'energy_var'))
    smg.set_setting(var_spec, {'flux_index':np.linspace(0,len(energys)-1,5)})
    smg.set_setting(var_spec, {'color_table':'jet'})
    energy = 1000
    flux_var = read.ml.rbsp_flux(time_range, probe=probe, energy=energy)

    var_combo = 'ae_dst'
    settings = {
        'display_type': 'combo_scalar',
    }
    smg.set_data(var_combo,
        data=[read.ml.symh(time_range),read.ml.ae(time_range),],
        settings=settings)
    
    var_combo2 = 'ae_dst_vector'
    settings = {
        'display_type': 'combo_vector',
    }
    smg.set_data(var_combo2,
        data=smg.get_data(var_combo),
        settings=settings)
    
    var_scalar_with_color = 'l_on_flux'
    settings = {
        'display_type': 'scalar_with_color',
        'color_table': 'jet',
    }
    lshell_var = read.ml.rbsp_lshell(time_range, probe=probe)
    smg.set_data(var_scalar_with_color,
        data=[lshell_var,flux_var],
        settings=settings)


    fig = spl.Fig((10,6))
    vars = [var_vector,flux_var,var_combo,var_combo2,var_scalar_with_color]
#    vars = [var_vector,var_scalar,flux_var]
    smg.set_setting(var_spec, {'display_type':'flux'})
    fig.plot(vars, xrange=time_range, xstep=10*86400, xminor=10)




    ae_var = read.omni.ae(time_range)
    spl.plot(ae_var)

    r_vars = list()
    for probe in rbsp_probes:
        r_vars.append(read.rbsp.orbit(time_range, probe, coord='gsm', resolution=resolution))
    

    r_var = r_vars[0]

    pytplot.tplot_names()


if __name__ == '__main__':
    main()