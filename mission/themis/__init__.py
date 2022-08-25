import os
import libs.system as system

# Default settings.
local_data_root = os.path.join(system.local_data_root(),'rbsp')
assert os.path.exists(local_data_root), f'{local_data_root} does not exist ...'
assert os.path.isdir(local_data_root), f'{local_data_root} is not a directory ...'

all_probes = ['a','b','c','d','e']
