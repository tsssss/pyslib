from pyspedas.cotrans import cotrans_lib
# This is primarily adopted from pyspedas.
# https://github.com/spedas/pyspedas/blob/master/pyspedas/cotrans/cotrans_lib.py
# But I plan to clean up the subroutines a bit (e.g., use quaternions, clean up the Sun related routines.)



def cotran(
    vec0,
    time=None,
    input='',
    output='',
    probe=None,
):
    supported_coords = ['gse','gsm','sm','gei','geo','mag','j2000','rbsp_uvw','rbsp_mgse']

    if input not in supported_coords:
        raise Exception(f'Unknown input coord {input} ...')
    if output not in supported_coords:
        raise Exception(f'Unknown output coord {input} ...')
    if input == output:
        return vec0
    
    p = cotrans_lib.find_path_t1_t2(input, output)
    p = cotrans_lib.shorten_path_t1_t2(p)
    p = cotrans_lib.shorten_path_t1_t2(p)

    vec1 = vec0
    for i in range(len(p)-1):
        routine_name = p[i]+'2'+p[i+1]
        vec1 = globals()[routine_name](vec1, time, probe=probe)
    return vec1


def rbsp_uvw2gse(vec0, uts, probe=None):
    pass

def rbsp_gse2uvw(vec0, uts, probe=None):
    pass

def rbsp_mgse2gse(vec0, uts, probe=None):
    pass

def rbsp_mgse2uvw(vec0, uts, probe=None):
    pass

def gei2gse(vec0, uts, probe=None):
    return cotrans_lib.subgei2gse(uts, vec0)

def gse2gei(vec0, uts, probe=None):
    return cotrans_lib.subgse2gei(uts, vec0)

def gse2gsm(vec0, uts, probe=None):
    return cotrans_lib.subgse2gsm(uts, vec0)

def gsm2gse(vec0, uts, probe=None):
    return cotrans_lib.subgsm2gse(uts, vec0)

def gsm2sm(vec0, uts, probe=None):
    return cotrans_lib.subgsm2sm(uts, vec0)

def sm2gsm(vec0, uts, probe=None):
    return cotrans_lib.subsm2gsm(uts, vec0)

def gei2geo(vec0, uts, probe=None):
    return cotrans_lib.subgei2geo(uts, vec0)

def geo2gei(vec0, uts, probe=None):
    return cotrans_lib.subgeo2gei(uts, vec0)

def geo2mag(vec0, uts, probe=None):
    return cotrans_lib.subgeo2mag(uts, vec0)

def mag2geo(vec0, uts, probe=None):
    return cotrans_lib.submag2geo(uts, vec0)

def gei2j2000(vec0, uts, probe=None):
    return cotrans_lib.subgei2j2000(uts, vec0)

def j20002gei(vec0, uts, probe=None):
    return cotrans_lib.subj20002gei(uts, vec0)