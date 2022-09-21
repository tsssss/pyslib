import pytplot
import read
import system.plot as spl
import mission
import system.manager as smg


def main():

    time_range = ['2013-06-01','2013-06-02/12:00']
    rbsp_probes = ['a','b']
    resolution = 60

#    vec_var = read.ml.sw_v(time_range, coord='gsm')
#    var = 'omni_sw_vmag'
#    var = smg.magnitude(vec_var, output=var)
    var = read.ml.rbsp_mlt(time_range)
    spl.plot(var)

    probe = rbsp_probes[0]
    files = mission.ml.rbsp.hope_en_spec(time_range, probe=probe)
    for file in files: print(file)
    files = mission.ml.omni.param(time_range)
    for file in files: print(file)

    spec_var = read.ml.rbsp_en_spec(time_range, probe=probe, species='o')

    energy = 1000
    flux_var = read.ml.rbsp_flux(spec_var, energy=energy)
    spl.plot(flux_var)


    ae_var = read.omni.ae(time_range)
    spl.plot(ae_var)

    r_vars = list()
    for probe in rbsp_probes:
        r_vars.append(read.rbsp.orbit(time_range, probe, coord='gsm', resolution=resolution))
    

    r_var = r_vars[0]

    pytplot.tplot_names()


if __name__ == '__main__':
    main()