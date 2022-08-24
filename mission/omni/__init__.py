import os
import libs.system as system

# Default settings.
local_data_root = os.path.join(system.diskdir('data'),'omni')
if not os.path.exists(local_data_root): local_data_root = os.path.join(system.homedir(),'data','omni')
assert os.path.exists(local_data_root), f'{local_data_root} does not exist ...'

assert os.path.isdir(local_data_root), f'{local_data_root} is not a directory ...'


def file_request(
    input_time_range,
):

    file_request = dict()
    file_request['time_range'] = system.prepare_time_range(input_time_range)
    file_request['cadence'] = 'month'

    return file_request


from . import omni