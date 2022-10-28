from mission import omni
import system.manager as smg

# AE.
def ae(
    time_range,
):

#    valid_range = omni.valid_range('ae')
#    time_range = system.validate_time_range(time_range, valid_range)
    var_request = {
        'files': omni.load_file(time_range),
        'in_vars': ['AE_INDEX'],
        'out_vars': ['omni_ae'],
        'time_var': 'Epoch',
        'time_range': time_range,
    }
    var = smg.read_var(var_request)
    settings = {
        'display_type': 'scalar',
        'short_name': 'AE',
    }
    smg.set_setting(var, settings)
    return var



# Dst.
def dst(
    time_range,
):

    var_request = {
        'files': omni.load_file(time_range),
        'in_vars': ['SYM_H'],
        'out_vars': ['omni_dst'],
        'time_var': 'Epoch',
        'time_range': time_range,
    }
    var = smg.read_var(var_request)
    settings = {
        'display_type': 'scalar',
        'short_name': 'Dst',
    }
    smg.set_setting(var, settings)
    return var


# Solar wind B.
def sw_b(
    time_range,
    coord='gsm',
):

    coord_labels = list('xyz')
    var_request = {
        'files': omni.load_file(time_range),
        'in_vars': ['BX_GSE','BY_GSM','BZ_GSM'],
        'out_vars': ['omni_b'+x+'_gsm' for x in coord_labels],
        'time_var': 'Epoch',
        'time_range': time_range,
    }
    vars = smg.read_var(var_request)

    settings = {
        'display_type': 'vector',
        'short_name': 'SW B',
        'coord': 'GSM',
        'coord_labels': coord_labels,
    }
    gsm_var = 'omni_sw_b_gsm'
    smg.merge(vars, output=gsm_var, settings=settings)

    coord_var = 'omni_sw_b_'+coord
    if coord != 'gsm':
        smg.cotran(gsm_var, coord_var, coord_in='gsm', coord_out=coord)

    return coord_var