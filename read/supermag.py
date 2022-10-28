from time import time
from mission import supermag
import system.manager as smg

# SME.
def sme(
    time_range,
):

    var_request = {
        'files': supermag.load_file(time_range, input_id='aei'),
        'in_vars': ['sme'],
        'out_vars': ['sm_ae'],
        'time_range': time_range,
    }
    var = smg.read_var(var_request)
    settings = {
        'display_type': 'scalar',
        'short_name': 'SME',
    }
    smg.set_setting(var, settings)
    return var


def smu(
    time_range,
):

    var_request = {
        'files': supermag.load_file(time_range, input_id='aei'),
        'in_vars': ['smu'],
        'out_vars': ['sm_au'],
        'time_range': time_range,
    }
    var = smg.read_var(var_request)
    settings = {
        'display_type': 'scalar',
        'short_name': 'SMU',
    }
    smg.set_setting(var, settings)
    return var


def sml(
    time_range,
):

    var_request = {
        'files': supermag.load_file(time_range, input_id='aei'),
        'in_vars': ['sml'],
        'out_vars': ['sm_al'],
        'time_range': time_range,
    }
    var = smg.read_var(var_request)
    settings = {
        'display_type': 'scalar',
        'short_name': 'SML',
    }
    smg.set_setting(var, settings)
    return var


def smo(
    time_range,
):

    var_request = {
        'files': supermag.load_file(time_range, input_id='aei'),
        'in_vars': ['smu','sml'],
        'out_vars': ['sm_au','sm_al'],
        'time_range': time_range,
    }
    vars = smg.read_var(var_request)
    ao = (smg.get_data(vars[0])+smg.get_data(vars[1]))*0.5
    settings = {
        'display_type': 'scalar',
        'short_name': 'SMO',
        'unit': 'nT',
        'time_var': smg.get_time_var(vars[0]),
    }
    var = 'sm_ao'
    smg.set_data('sm_ao', ao, settings=settings)
    smg.set_setting(var, settings)
    return var