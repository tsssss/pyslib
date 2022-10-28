from .. import rbsp

# Spacecraft orbit.
def load_file(
    input_time_range,
    probe,
    input_id,
    version='v*',
    file_times=None,
    local_data_dir=rbsp.local_data_root,
    remote_data_dir='https://cdaweb.gsfc.nasa.gov/pub/data/rbsp/',
):

    return rbsp.efw.load_file(input_time_range, probe, 'spice')

