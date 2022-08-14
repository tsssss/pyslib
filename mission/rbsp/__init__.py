import os
from .. import utils

# Default settings.
local_data_root = os.path.join(utils.diskdir('data'),'rbsp')
if not os.path.exists(local_data_root): local_data_root = os.path.join(utils.homedir(),'data','rbsp')
assert os.path.exists(local_data_root), f'{local_data_root} does not exist ...'
assert os.path.isdir(local_data_root), f'{local_data_root} is not a directory ...'

all_probes = ['a','b']

valid_range = {
    'a': ['2012-09-05','2019-10-14/24:00'],
    'b': ['2012-09-05','2019-07-16/24:00'],
}



def file_request(
    input_time_range,
    probe,
):

    assert probe in all_probes, f'Invalid probe: {probe} ...'

    file_request = dict()
    file_request['time_range'] = utils.prepare_time_range(input_time_range)
    file_request['probe'] = probe
    file_request['valid_range'] = utils.prepare_time_range(valid_range[probe])

    return file_request



from . import hope
from . import efw