from distutils.command.clean import clean
import imp
import os
from threading import local
from .. import utils

# Default settings.
local_data_root = os.path.join('/Volumes/data','rbsp')
assert os.path.exists(local_data_root), f'{local_data_root} does not exist ...'
assert os.path.isdir(local_data_root), f'{local_data_root} is not a directory ...'

class RBSP():

    # Settings.
    local_data_root = local_data_root
    probes = ['a','b']
    valid_range = {
        'a': ['2012-09-05','2019-10-14/24:00'],
        'b': ['2012-09-05','2019-07-16/24:00'],
    }

    def __init__(self, input_time_range, input_probe):
        probe = input_probe.lower()
        assert probe in self.probes, f'Invalid probe: {probe} ...'
        self.file_request = {
            'time_range': utils.prepare_time_range(input_time_range),
            'valid_range': utils.prepare_time_range(self.valid_range[probe]),
            'probe': probe, 
            'prefix': 'rbsp'+probe+'_',
            'rbspx': 'rbsp'+probe,
            'cadence': 'day',
            'remote_data_dir': 'https://cdaweb.gsfc.nasa.gov/pub/data/rbsp/',
            'local_data_dir': local_data_root,
        }


    # HOPE.
    class HOPE():
        # Settings.
        valid_range = {
            'a': ['2012-10-25','2019-10-14/24:00'],
            'b': ['2012-10-25','2019-07-16/24:00'],
        }
        latest_release = 'rel04'


        def __init__(self, input_time_range, input_probe):
            rbsp = RBSP(input_time_range, input_probe)
            self.file_request = rbsp.file_request
            probe = self.file_request['probe']
            self.file_request['valid_range'] = utils.prepare_time_range(self.valid_range[probe])

            # Validated time range.
            valid_tr = self.file_request['valid_range']
            tr = self.file_request['time_range']
            if tr[0] < valid_tr[0]: tr[0] = valid_tr[0]
            if tr[1] > valid_tr[1]: tr[1] = valid_tr[1]
            self.file_request['validated_time_range'] = tr

        def load_file(self, input_id, release=latest_release, version='v*'):

            file_request = self.file_request
            file_request['id'] = input_id
            rbspx = file_request['rbspx']
            prefix = file_request['prefix']
            remote_data_dir = file_request['remote_data_dir']
            local_data_dir = file_request['local_data_dir']

            if input_id == 'l3%mom':
                # L3 moments.
                base_name = prefix+release+'_ect-hope-mom-l3_%Y%m%d_'+version+'.cdf'
                local_path = os.path.join(rbspx,'hope','level3','mom_'+release,'%Y')
                remote_path = os.path.join(rbspx,'l3','ect','hope','moments',release,'%Y')
            elif input_id == 'l3%pa':
                # L3 pitch angle.
                base_name = prefix+release+'_ect-hope-pa-l3_%Y%m%d_'+version+'.cdf'
                local_path = os.path.join(rbspx,'hope','level3','pa_'+release,'%Y')
                remote_path = os.path.join(rbspx,'l3','ect','hope','pitchangle',release,'%Y')
            elif input_id == 'l2%sector':
                base_name = prefix+release+'_ect-hope-sci-l2_%Y%m%d_'+version+'.cdf'
                local_path = os.path.join(rbspx,'hope','level2','sectors_'+release,'%Y')
                remote_path = os.path.join(rbspx,'l2','ect','hope','sectors',release,'%Y')
            else:
                raise Exception(f'Unknown id: {input_id}')

            file_request['local_pattern'] = os.path.join(local_data_dir,local_path,base_name)
            file_request['remote_pattern'] = os.path.join(remote_data_dir,remote_path,base_name)
            files = utils.prepare_files(file_request) 
            return files



from .hope import hope