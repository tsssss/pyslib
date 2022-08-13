import os

# Default settings.
local_data_root = os.path.join('/Volumes/data','rbsp')
assert os.path.exists(local_data_root), f'{local_data_root} does not exist ...'
assert os.path.isdir(local_data_root), f'{local_data_root} is not a directory ...'

all_probes = ['a','b']

valid_range = {
    'a': ['2012-09-05','2019-10-14/24:00'],
    'b': ['2012-09-05','2019-07-16/24:00'],
}

# def valid_range(id, probe):
#     assert id in valid_range
#     assert probe in all_probes
#     time_range = time_double(valid_range[id][probe])
#     if len(time_range) == 1:
#         time_range.append(time.time())
#     return time_range