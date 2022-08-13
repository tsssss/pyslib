import os
from .. import rbsp
from .. import utils

# HOPE.
def hope(
    input_time_range,
    probe,
    input_id,
    local_files=[],
    file_times=None,
    version='v*',
    release=None,
    local_data_dir=rbsp.local_data_root,
):

    # Settings.
    hope_valid_range = {
        'a': ['2012-10-25','2019-10-14/24:00'],
        'b': ['2012-10-25','2019-07-16/24:00'],
    }


    # Check inputs.
    assert probe in rbsp.all_probes
    rbspx = 'rbsp'+probe
    prefix = 'rbsp'+probe+'_'
    time_range = utils.prepare_time_range(input_time_range)

    latest_release = 'rel04'
    if release is None:
        release = latest_release

    # A look up dictionary containing the info of remote and local data locations.
    file_requests = dict()

    # cdaweb.
    # L3 moments.
    id = 'l3%mom'
    valid_range = hope_valid_range[probe]
    base_name = prefix+release+'_ect-hope-mom-l3_%Y%m%d_'+version+'.cdf'
    local_path = os.path.join(rbspx,'hope','level3','mom_'+release,'%Y')
    remote_path = os.path.join(rbspx,'l3','ect','hope','moments',release,'%Y')
    remote_data_dir = 'https://cdaweb.gsfc.nasa.gov/pub/data/rbsp/'
    file_requests[id] = {
        'valid_range': valid_range,
        'local_pattern': os.path.join(local_data_dir,local_path,base_name),
        'remote_pattern': os.path.join(remote_data_dir,remote_path,base_name),
    }

    # L3 pitch angle.
    id = 'l3%pa'
    valid_range = hope_valid_range[probe]
    base_name = prefix+release+'_ect-hope-pa-l3_%Y%m%d_'+version+'.cdf'
    local_path = os.path.join(rbspx,'hope','level3','pa_'+release,'%Y')
    remote_path = os.path.join(rbspx,'l3','ect','hope','pitchangle',release,'%Y')
    remote_data_dir = 'https://cdaweb.gsfc.nasa.gov/pub/data/rbsp/'
    file_requests[id] = {
        'valid_range': valid_range,
        'local_pattern': os.path.join(local_data_dir,local_path,base_name),
        'remote_pattern': os.path.join(remote_data_dir,remote_path,base_name),
    }

    # L2.
    id = 'l2%sector'
    valid_range = hope_valid_range[probe]
    base_name = prefix+release+'_ect-hope-sci-l2_%Y%m%d_'+version+'.cdf'
    local_path = os.path.join(rbspx,'hope','level2','sectors_'+release,'%Y')
    remote_path = os.path.join(rbspx,'l2','ect','hope','sectors',release,'%Y')
    remote_data_dir = 'https://cdaweb.gsfc.nasa.gov/pub/data/rbsp/'
    file_requests['l2%sector'] = {
        'valid_range': valid_range,
        'local_pattern': os.path.join(local_data_dir,local_path,base_name),
        'remote_pattern': os.path.join(remote_data_dir,remote_path,base_name),
    }

    # Process the file request, find and download the files.
    assert input_id in file_requests.keys(), f'{input_id} not supported ...'
    request = file_requests[id]
    request['local_files'] = local_files
    request['file_times'] = file_times
    request['time_range'] = time_range
    files = utils.prepare_files(request) 
    return files