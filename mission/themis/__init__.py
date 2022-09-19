import os
import system.manager as smg

# Default settings.
local_data_root = os.path.join(smg.local_data_root(),'rbsp')
assert os.path.exists(local_data_root), f'{local_data_root} does not exist ...'
assert os.path.isdir(local_data_root), f'{local_data_root} is not a directory ...'

all_probes = ['a','b','c','d','e']
