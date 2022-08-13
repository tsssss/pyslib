import os
from .. import rbsp
from .. import utils

valid_range = {
    'a': ['2012-10-25','2019-10-14/24:00'],
    'b': ['2012-10-25','2019-07-16/24:00'],
}

def load_file(
    input_time_range,
    probe,
    input_id,
    version='v*',
    release=None,
    file_times=None,
    local_data_dir=rbsp.local_data_root,
    remote_data_dir=None,
):

    """ Take input time, probe, and id, then find and return the actual files."""

    # Settings.
    if remote_data_dir is None: remote_data_dir = 'https://cdaweb.gsfc.nasa.gov/pub/data/rbsp/'
    latest_release = 'rel04'
    if release is None: release = latest_release


    # Get the rbsp-general file request.
    rbspx = 'rbsp'+probe
    prefix = 'rbsp'+probe+'_'
    file_request = rbsp.file_request(input_time_range, probe)
    file_request['valid_range'] = valid_range[probe]
    if file_times is not None: file_request['file_times'] = file_times


    # A look up dictionary containing the info of remote and local data locations.
    file_infos = dict()

    # cdaweb.
    # L3 moments.
    id = 'l3%mom'
    base_name = prefix+release+'_ect-hope-mom-l3_%Y%m%d_'+version+'.cdf'
    local_path = os.path.join(rbspx,'hope','level3','mom_'+release,'%Y')
    remote_path = os.path.join(rbspx,'l3','ect','hope','moments',release,'%Y')
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,local_path,base_name),
        'remote_pattern': os.path.join(remote_data_dir,remote_path,base_name),
    }

    # L3 pitch angle.
    id = 'l3%pa'
    base_name = prefix+release+'_ect-hope-pa-l3_%Y%m%d_'+version+'.cdf'
    local_path = os.path.join(rbspx,'hope','level3','pa_'+release,'%Y')
    remote_path = os.path.join(rbspx,'l3','ect','hope','pitchangle',release,'%Y')
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,local_path,base_name),
        'remote_pattern': os.path.join(remote_data_dir,remote_path,base_name),
    }

    # L2.
    id = 'l2%sector'
    base_name = prefix+release+'_ect-hope-sci-l2_%Y%m%d_'+version+'.cdf'
    local_path = os.path.join(rbspx,'hope','level2','sectors_'+release,'%Y')
    remote_path = os.path.join(rbspx,'l2','ect','hope','sectors',release,'%Y')
    file_infos['l2%sector'] = {
        'local_pattern': os.path.join(local_data_dir,local_path,base_name),
        'remote_pattern': os.path.join(remote_data_dir,remote_path,base_name),
    }

    # Process the file request, find and download the files.
    assert input_id in file_infos.keys(), f'{input_id} not supported ...'
    file_info = file_infos[input_id]
    for key in file_info:
        file_request[key] = file_info[key]

    files = utils.prepare_files(file_request) 
    return files