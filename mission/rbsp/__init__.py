import os
import system.manager as smg

# Default settings.
local_data_root = os.path.join(smg.local_data_root(),'rbsp')
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
    file_request['time_range'] = smg.prepare_time_range(input_time_range)
    file_request['probe'] = probe
    file_request['valid_range'] = smg.prepare_time_range(valid_range[probe])

    return file_request



from . import efw
from . import emfisis
from . import hope
from . import mageis
from . import ssc