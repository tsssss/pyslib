import system.manager as smg
import numpy as np
import mission

rbsp_species_info = {'e':'e-', 'o':'O+', 'p':'H+', 'he':'He+'}

def symh(time_range):

    symh_var = 'omni_symh'
    var = omni_var(time_range, 'symh')
    if var != symh_var: smg.rename(var, symh_var)
    settings = {
        'display_type': 'scalar',
        'short_name': 'SymH',
        'unit': 'nT',
    }
    smg.set_setting(symh_var, settings)
    return symh_var


def symd(time_range):

    symd_var = 'omni_symd'
    var = omni_var(time_range, 'symd')
    if var != symd_var: smg.rename(var, symd_var)
    settings = {
        'display_type': 'scalar',
        'short_name': 'SymD',
        'unit': 'nT',
    }
    smg.set_setting(symd_var, settings)
    return symd_var


def asyh(time_range):
    asyh_var = 'omni_asyh'
    var = omni_var(time_range, 'asyh')
    if var != asyh_var: smg.rename(var, asyh_var)
    settings = {
        'display_type': 'scalar',
        'short_name': 'AsymH',
        'unit': 'nT',
    }
    smg.set_setting(asyh_var, settings)
    return asyh_var


def asyd(time_range):
    asyd_var = 'omni_asyd'
    var = omni_var(time_range, 'asyd')
    if var != asyd_var: smg.rename(var, asyd_var)
    settings = {
        'display_type': 'scalar',
        'short_name': 'AsymD',
        'unit': 'nT',
    }
    smg.set_setting(asyd_var, settings)
    return asyd_var


def au(time_range):

    omni_var(time_range, 'au')
    au_var = 'omni_au'
    settings = {
        'display_type': 'scalar',
        'short_name': 'AU',
        'unit': 'nT',
    }
    smg.set_setting(au_var, settings=settings)
    return au_var

def al(time_range):

    omni_var(time_range, 'al')
    al_var = 'omni_al'
    settings = {
        'display_type': 'scalar',
        'short_name': 'AL',
        'unit': 'nT',
    }
    smg.set_setting(al_var, settings=settings)
    return al_var


def ae(time_range):

    au_var = au(time_range)
    al_var = al(time_range)
    ae_var = 'omni_ae'
    ae = smg.get_data(au_var)-smg.get_data(al_var)
    settings = {
        'display_type': 'scalar',
        'short_name': 'AE',
        'unit': 'nT',
        'time_var': smg.get_time_var(au_var),
    }
    smg.set_data(ae_var, ae, settings=settings)
    return ae_var


def ao(time_range):

    au_var = au(time_range)
    al_var = al(time_range)
    ao_var = 'omni_ao'
    ao = (smg.get_data(au_var)+smg.get_data(al_var))*0.5
    settings = {
        'display_type': 'scalar',
        'short_name': 'AO',
        'unit': 'nT',
        'time_var': smg.get_time_var(au_var),
    }
    smg.set_data(ao_var, ao, settings=settings)
    return ao_var





def sw_b(time_range, coord='gse'):
    gse_var = omni_var(time_range, 'sw_b_gse')
    coord_var = 'omni_sw_b_'+coord.lower()

    if coord != 'gse':
        smg.cotran(gse_var, coord_var, coord_in='gse', coord_out=coord)

    settings = {
        'display_type': 'vector',
        'short_name': 'SW B',
        'unit': 'nT',
        'coord': coord.upper(),
        'coord_labels': [x for x in 'xyz'],
    }
    smg.set_setting(coord_var, settings)
    
    return coord_var


def sw_v(time_range, coord='gse'):
    gse_var = omni_var(time_range, 'sw_v_gse')
    coord_var = 'omni_sw_v_'+coord.lower()

    if coord != 'gse':
        smg.cotran(gse_var, coord_var, coord_in='gse', coord_out=coord)

    settings = {
        'display_type': 'vector',
        'short_name': 'SW V',
        'unit': 'km/s',
        'coord': coord.upper(),
        'coord_labels': [x for x in 'xyz'],
    }
    smg.set_setting(coord_var, settings)
    
    return coord_var


def f107(time_range):
    var = omni_var(time_range, 'f107')

    settings = {
        'display_type': 'scalar',
        'short_name': 'F10.7',
        'unit': '$10^{-22}$J/s-m${}^2$-Hz',
    }
    smg.set_setting(var, settings=settings)
    return var

def pc_index(time_range):
    var = omni_var(time_range, 'pc_index')

    settings = {
        'display_type': 'scalar',
        'short_name': 'PC index',
        'unit': '#',
    }
    smg.set_setting(var, settings=settings)
    return var


def sw_t(time_range):
    var = omni_var(time_range, 'sw_t')

    settings = {
        'display_type': 'scalar',
        'short_name': 'SW T',
        'unit': 'eV',
        'ylog': True,
    }
    smg.set_setting(var, settings=settings)
    return var


def sw_n(time_range):
    var = omni_var(time_range, 'sw_n')

    settings = {
        'display_type': 'scalar',
        'short_name': 'SW N$_H$',
        'unit': 'cm$^3$',
        'ylog': True,
    }
    smg.set_setting(var, settings=settings)
    return var


def sw_p(time_range):
    var = omni_var(time_range, 'sw_p')

    settings = {
        'display_type': 'scalar',
        'short_name': 'SW P$_{dyn}$',
        'unit': 'nPa',
        'ylog': True,
    }
    smg.set_setting(var, settings=settings)
    return var



def omni_var(
    input_time_range,
    var=None,
):

    time_range = smg.prepare_time_range(input_time_range)
    files = mission.ml.omni.param(time_range)

    prefix = 'omni_'
    if type(var) is str: in_vars = [var]
    else: in_vars = var
    x = lambda a: a if prefix in a else prefix+a
    in_vars = [x(var) for var in in_vars]

    var_request = {
        'files': files,
        'in_vars': in_vars,
        'time_range': time_range,
    }
    return smg.read_var(var_request)




def rbsp_mlt(
    time_range,
    probe='a',
):

    var = rbsp_orbit_var(time_range, probe, 'mlt')
    settings = {
        'display_type': 'scalar',
        'short_name': 'MLT',
        'unit': 'h',
        'yrange': [0,24],
    }
    smg.set_setting(var, settings)
    return var


def rbsp_mlat(
    time_range,
    probe='a',
):

    var = rbsp_orbit_var(time_range, probe, 'mlat')
    settings = {
        'display_type': 'scalar',
        'short_name': 'MLat',
        'unit': 'deg',
    }
    smg.set_setting(var, settings)
    return var


def rbsp_lshell(
    time_range,
    probe='a',
):

    var = rbsp_orbit_var(time_range, probe, 'lshell')
    settings = {
        'display_type': 'scalar',
        'short_name': 'L',
        'unit': '#',
    }
    smg.set_setting(var, settings)
    return var


def rbsp_dis(
    time_range,
    probe='a',
    r_var=None,
):

    if r_var is None:
        r_var = rbsp_r(time_range, probe)

    prefix = 'rbsp'+probe+'_'
    dis_var = prefix+'dis'
    return smg.magnitude(r_var, output=dis_var)

def rbsp_r(
    time_range,
    probe='a',
    coord='sm',
):

    coord_default = 'sm'
    prefix = 'rbsp'+probe+'_'
    default_var = rbsp_orbit_var(time_range, probe, 'r_'+coord_default)
    coord_var = prefix+'r_'+coord.lower()

    if coord != coord_default:
        smg.cotran(default_var, coord_var, coord_in=coord_default, coord_out=coord)

    settings = {
        'display_type': 'vector',
        'short_name': 'R',
        'unit': 'Re',
        'coord': coord.upper(),
        'coord_labels': [x for x in 'xyz'],
    }
    smg.set_setting(coord_var, settings)
    return coord_var




def rbsp_orbit_var(
    input_time_range,
    probe='a',
    var=None,
):

    time_range = smg.prepare_time_range(input_time_range)
    files = mission.ml.rbsp.orbit_var(time_range)

    prefix = 'rbsp'+probe+'_'

    if type(var) is str: in_vars = [var]
    else: in_vars = var
    x = lambda a: a if prefix in a else prefix+a
    in_vars = [x(var) for var in in_vars]

    var_request = {
        'files': files,
        'in_vars': in_vars,
        'time_range': time_range,
    }
    return smg.read_var(var_request)


def rbsp_flux(
    time_range,
    probe=None,
    spec_var=None,
    energy=None,
    species=None,
    output=None,
):

    assert energy is not None
    energy_str = str(np.int64(np.round(energy)))

    if spec_var is None:
        spec_var = rbsp_en_spec(time_range, probe, species=species)
    assert smg.has_var(spec_var)
    flux_var = output
    if flux_var == None: flux_var = spec_var+'_'+energy_str+'eV'

    # Filter on energy.
    spec_settings = smg.get_setting(spec_var)
    flux_unit = spec_settings['unit']
    energy_var = spec_settings['energy_var']
    energy_unit = 'eV'
    energy_bins = smg.get_data(energy_var)

    energy_index = np.abs(energy_bins-energy).argmin()
    spec = smg.get_data(spec_var)
    time_var = smg.get_time_var(spec_var)
    species_str = spec_settings['species_str']
    settings = {
        'display_type': 'scalar',
        'short_name': f'{species_str} flux\n{energy_str} {energy_unit}',
        'species': spec_settings['species'],
        'species_str': species_str,
        'ylog': True,
        'unit': flux_unit,
        'energy': energy_bins[energy_index],
        'energy_str': energy_str,
        'depend_vars': time_var,
        'time_var': time_var,
    }

    smg.set_data(flux_var, spec[:,energy_index], settings=settings)

    return flux_var


def rbsp_en_spec(
    input_time_range,
    probe='a',
    species='p',
):

    prefix = 'rbsp'+probe+'_'
    spec_var = prefix+'hope_flux_'+species

    time_range = smg.prepare_time_range(input_time_range)
    files = mission.ml.rbsp.hope_en_spec(time_range, probe=probe)

    step = 1

    var_request = {
        'files': files,
        'in_vars': [spec_var],
        'time_range': time_range,
        'step': step,
    }
    var = smg.read_var(var_request)
    var_settings = smg.get_setting(var)
    energy_var = var_settings['DEPEND_1']
    energy_settings = smg.get_setting(energy_var)
    settings = {
        'display_type': 'spec',
        'zlog': True,
        'ylog': True,
        'unit': '#/s-cm$^{-2}$-sr-keV',
        'energy_var': energy_var,
        'energy_unit': energy_settings['UNITS'],
        'species': species,
        'species_str': rbsp_species_info[species],
    }
    smg.set_setting(var, settings=settings)

    data = smg.get_data(var)
    fill_value = 0.01
    data[data < fill_value] = np.nan
    smg.update_data(var, data)

    return var
