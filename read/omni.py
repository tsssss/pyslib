from mission import omni
import libs.system as system
import constant

# AE.
def ae(
    time_range,
):

#    valid_range = omni.valid_range('ae')
#    time_range = system.validate_time_range(time_range, valid_range)
    var_request = {
        'local_files': omni.load_file(time_range),
        'in_vars': ['AE_INDEX'],
        'out_vars': ['omni_ae'],
    }
    return system.read_var(var_request)


# Dst.
def dst(
    time_range,
):

    var_request = {
        'local_files': omni.load_file(time_range),
        'in_vars': ['SYM_H'],
        'out_vars': ['omni_dst'],
    }
    return system.read_var(var_request)

# Solar wind B.
def sw_b(
    time_range,
    coord='gsm',
):

    var_request = {
        'local_files': omni.load_file(time_range),
        'in_vars': ['BX_GSE','BY_GSM','BZ_GSM'],
        'out_vars': ['b'+x+'_gsm' for x in constant.xyz],
    }
    vars = system.read_var(var_request)
