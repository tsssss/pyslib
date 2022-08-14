import os
from ssl import VerifyFlags
from .. import rbsp
from .. import utils

def valid_range(id, probe=None):

    valid_ranges = dict()
    
    if id == 'l2%esvy_despun':
        return valid_range('l2%e_hires_uvw', probe=probe)
    if id == 'l2%fbk':
        return valid_range('l2%spec', probe=probe)

    valid_ranges['l2%e_hires_uvw'] = {
        'a': ['2012-09-23','2019-02-23/24:00'],
        'b': ['2012-09-23','2019-07-16/24:00'],
    }
    valid_ranges['l2%vsvy_hires'] = {
        'a': ['2012-09-05','2019-10-14/24:00'],
        'b': ['2012-09-05','2019-07-16/24:00'],
    }
    valid_ranges['l2%spec'] = {
        'a': ['2012-09-05','2019-10-12/24:00'],
        'b': ['2012-09-05','2019-07-14/24:00'],
    }
    valid_ranges['e_spinfit'] = {
        'a': ['2012-09-13','2019-02-23/24:00'],
        'b': ['2012-09-13','2019-07-16/24:00'],
    }
    valid_ranges['l1%esvy'] = {
        'a': ['2012-09-13','2019-10-14/24:00'],
        'b': ['2012-09-13','2019-07-16/24:00'],
    }

    if id not in valid_ranges: raise Exception(f'Unknown id: {id} ...')
    if probe is None: return valid_ranges[id]
    else: return (valid_ranges[id])[probe]


def load_file(
    input_time_range,
    probe,
    input_id,
    version='v*',
    file_times=None,
    local_data_dir=rbsp.local_data_root,
    remote_data_dir=None,
):

    """ Take input time, probe, and id, then find and return the actual files."""

    # Settings.
    if remote_data_dir is None: remote_data_dir = 'https://cdaweb.gsfc.nasa.gov/pub/data/rbsp/'

    # Get the rbsp-general file request.
    rbspx = 'rbsp'+probe
    prefix = 'rbsp'+probe+'_'
    file_request = rbsp.file_request(input_time_range, probe)
    if file_times is not None: file_request['file_times'] = file_times

    # A look up dictionary containing the info of remote and local data locations.
    file_infos = dict()


    # L1 esvy.
    id = 'l1%esvy'
    base_name = prefix+'_l1_esvy_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l1','esvy','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l1','efw','esvy','%Y',base_name),
        'valid_range': utils.prepare_time_range(valid_range(id, probe)),
    }

    # L1 vb1-split.
    id = 'l1%vb1-split'
    base_name = prefix+'efw_l1_vb1-split_%Y%m%dt%H%M%S_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l1','vb1-split','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l1','efw','vb1-split','%Y',base_name),
        'cadence': 15*60,   # sec.
    }

    # L1 mscb1-split.
    id = 'l1%mscb1-split'
    base_name = prefix+'efw_l1_mscb1-split_%Y%m%dt%H%M%S_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l1','mscb1-split','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l1','efw','mscb1-split','%Y',base_name),
        'cadence': 15*60,   # sec.
    }

    # L1 vb1.
    id = 'l1%vb1'
    base_name = prefix+'l1_vb1_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l1','vb1','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l1','efw','vb1','%Y',base_name),
    }

    # L1 vb2.
    id = 'l1%vb2'
    base_name = prefix+'l1_vb2_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l1','vb2','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l1','efw','vb2','%Y',base_name),
    }

    # L1 eb1.
    id = 'l1%eb1'
    base_name = prefix+'l1_eb1_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l1','eb1','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l1','efw','eb1','%Y',base_name),
    }

    # L1 eb2.
    id = 'l1%eb2'
    base_name = prefix+'l1_eb2_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l1','eb2','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l1','efw','eb2','%Y',base_name),
    }

    # L1 mscb1.
    id = 'l1%mscb1'
    base_name = prefix+'l1_mscb1_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l1','mscb1','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l1','efw','mscb1','%Y',base_name),
    }

    # L1 mscb2.
    id = 'l1%mscb2'
    base_name = prefix+'l1_mscb2_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l1','mscb2','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l1','efw','mscb2','%Y',base_name),
    }

    # L1 vsvy.
    id = 'l1%vsvy'
    base_name = prefix+'l1_vsvy_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l1','vsvy','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l1','efw','vsvy','%Y',base_name),
    }

    # L1 esvy.
    id = 'l1%esvy'
    base_name = prefix+'l1_esvy_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l1','esvy','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l1','efw','esvy','%Y',base_name),
    }
    

    # L2 e_hires_uvw.
    id = 'l2%e_hires_uvw'
    base_name = prefix+'efw-l2_e-hires-uvw_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l2','e-highres-uvw','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l2','efw','e-highres-uvw','%Y',base_name),
        'valid_range': utils.prepare_time_range(valid_range(id, probe)),
    }

    # L2 esvy_despun.
    id = 'l2%esvy_despun'
    base_name = prefix+'efw-l2_esvy_despun_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l2','esvy_despun','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l2','efw','esvy_despun','%Y',base_name),
        'valid_range': utils.prepare_time_range(valid_range(id, probe)),
    }

    # L2 vsvy_hires.
    id = 'l2%vsvy_hires'
    base_name = prefix+'efw-l2_vsvy-hires_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l2','vsvy-highres','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l2','efw','vsvy-highres','%Y',base_name),
        'valid_range': utils.prepare_time_range(valid_range(id, probe)),
    }

    # L2 spec.
    id = 'l2%spec'
    base_name = prefix+'efw-l2_spec_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l2','spec','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l2','efw','spec','%Y',base_name),
        'valid_range': utils.prepare_time_range(valid_range(id, probe)),
    }

    # L2 fbk.
    id = 'l2%fbk'
    base_name = prefix+'efw-l2_fbk_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l2','fbk','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l2','efw','fbk','%Y',base_name),
        'valid_range': utils.prepare_time_range(valid_range(id, probe)),
    }

    # L2 e_spinfit_mgse.
    id = 'l2%e_spinfit_mgse'
    base_name = prefix+'efw-l2_e_spinfit_mgse_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l2','e_spinfit_mgse','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l2','efw','e_spinfit_mgse','%Y',base_name),
        'valid_range': utils.prepare_time_range(valid_range('e_spinfit', probe)),
    }

    # L3.
    id = 'l3'
    base_name = prefix+'efw-l3_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,rbspx,'efw','l3','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,rbspx,'l3','efw','%Y',base_name),
        'valid_range': utils.prepare_time_range(valid_range('e_spinfit', probe)),
    }


    # Process the file request, find and download the files.
    assert input_id in file_infos.keys(), f'{input_id} not supported ...'
    file_info = file_infos[input_id]
    for key in file_info:
        file_request[key] = file_info[key]

    files = utils.prepare_files(file_request) 
    return files