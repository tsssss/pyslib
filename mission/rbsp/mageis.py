import os
from mission import rbsp
import system.manager as smg

valid_range = {
    'a': ['2012-09-07','2019-10-14/24:00'],
    'b': ['2012-09-06','2019-07-16/24:00'],
}
latest_release = 'rel04'

def load_file(
    input_time_range,
    probe,
    input_id,
    version='v*',
    release=latest_release,
    file_times=None,
    local_data_dir=rbsp.local_data_root,
    remote_data_dir='https://cdaweb.gsfc.nasa.gov/pub/data/rbsp/',
):

    # Get the rbsp-general file request.
    rbspx = 'rbsp'+probe
    prefix = 'rbsp'+probe+'_'
    file_request = rbsp.file_request(input_time_range, probe)
    if file_times is not None: file_request['file_times'] = file_times
    file_request['valid_range'] = smg.prepare_time_range(valid_range[probe])


    # A look up dictionary containing the info of remote and local data locations.
    file_infos = dict()
    id = 'l2%sector'
    base_name = prefix+release+'_ect-mageis-l2_%Y%m%d_'+version+'.cdf'
    local_path = os.path.join(rbspx,'mageis','level2','sectors_'+release,'%Y')
    remote_path = os.path.join(rbspx,'l2','ect','mageis','sectors',release,'%Y')
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,local_path,base_name),
        'remote_pattern': os.path.join(remote_data_dir,remote_path,base_name),
    }

    # Process the file request, find and download the files.
    assert input_id in file_infos.keys(), f'{input_id} not supported ...'
    file_info = file_infos[input_id]
    for key in file_info:
        file_request[key] = file_info[key]

    files = smg.prepare_files(file_request) 
    return files