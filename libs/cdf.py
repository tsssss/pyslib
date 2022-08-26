import ctypes
import os
from datetime import datetime
import numpy as np
from spacepy import pycdf   # https://github.com/spacepy/spacepy/blob/master/spacepy/pycdf/
from spacepy.pycdf import const
import cdflib   # https://github.com/MAVENSDC/cdflib

"""
To achieve what my IDL cdf programs can do (https://github.com/tsssss/slib/tree/master/cdf).

Originally I use cdflib, but it doesn't allow read and write at the same time.
Now I use both cdflib and pycdf. It needs to manually install the CDF library (https://spdf.gsfc.nasa.gov/pub/software/cdf/)

The ideal solution is still use the route of cdflib, i.e., to avoid installing the CDF libarary separately. However, I do noticed that cdflib took twice the time of pycdf to load several GB of data.
"""

valid_cdf_type = {
    1:  'CDF_INT1',
    2:  'CDF_INT2',
    4:  'CDF_INT4',
    8:  'CDF_INT8',
    11: 'CDF_UINT1',
    12: 'CDF_UINT2',
    14: 'CDF_UINT4',
    21: 'CDF_REAL4',
    22: 'CDF_REAL8',
    31: 'CDF_EPOCH',
    32: 'CDF_EPOCH16',
    33: 'CDF_TIME_TT2000',
    41: 'CDF_BYTE',
    44: 'CDF_FLOAT',
    45: 'CDF_DOUBLE',
    51: 'CDF_CHAR',
    52: 'CDF_UCHAR',
}
valid_cdf_type_code = list(valid_cdf_type.keys())
valid_cdf_type_str = list(valid_cdf_type.values())

def get_cdf_type_str(code):
    return valid_cdf_type_str[valid_cdf_type_code.index(int(code))]
def get_cdf_type_code(str):
    return valid_cdf_type_code[valid_cdf_type_str.index(str.upper())]


valid_coding = {
    1:  'NETWORK',
    2:  'SUN',
    3:  'VAX',
    4:  'DECSTATION', 
    5:  'SGi',
    6:  'IMBPC',
    7:  'IBMRS',
    8:  'HOST',
    9:  'PPC',
    11: 'HP',
    12: 'NeXT',
    13: 'ALPHAOSF1',
    14: 'ALPHAVMSd',
    15: 'ALPHAVMSg',
    16: 'ALPHAVMSi',
    17: 'ARM_LITTLE',
    18: 'ARM_BIG',
}

valid_checksum = {
    0: 'NO_CHECKSUM',
    1: 'MD5_CHECKSUM',
    2: 'OTHER_CHECKSUM',
}

valid_scope = {
    1: 'GLOBAL_SCOPE',
    2: 'VARIABLE_SCOPE',
}

valid_majority = {
    1: 'ROW_MAJORITY',
    2: 'COLUMN_MAJORITY',
}

valid_rec_vary = {
    True: 'VARY',
    False:'NOVARY',
}

valid_dim_vary = {
    -1: 1,  # VARY
    0:  0,  # NOVARY
}

valid_cdf_format = {
    1: 'SINGLE_FILE',
    2: 'MUTI_FILE',
}

valid_compression = {
    0: 'NO_COMPRESSION',
    1: 'RLE_COMPRESSION',
    2: 'HUFF_COMPRESSION',
    3: 'AHUFF_COMPRESSION',
    5: 'GZIP_COMPRESSION',
}


class cdf():
    filename = None
    _pycdf = None
    _cdflib = None
    
    def __init__(self, filename):
        self.filename = filename
        if os.path.exists(filename):
            self._pycdf = pycdf.CDF(filename, create=False, readonly=False)
        else:
            self._pycdf = pycdf.CDF(filename, create=True)
        
        _libpath, _library = pycdf.Library._find_lib()
        self.lib = pycdf.Library(_libpath, _library)
        self._cdflib = cdflib.CDF(filename)
        self.cdf_info = self._cdflib.cdf_info()


    def __del__(self):
        self._pycdf.close()

    def gatts(self):
        return list(self._pycdf.attrs.keys())

    def vatts(self):
        _vatts = list()
        atts = self.cdf_info['Attributes']
        for att in atts:
            for a in att:
                if att[a] == 'Variable':
                    _vatts.append(a)
        return _vatts


    def read_setting(self, var=None):
        if var is None:
            return dict(self._pycdf.attrs)
        else:
            return self.read_var_att(var)

    def vars(self):
        return list(self._pycdf.keys())

    def has_var(self, var):
        return var in self.vars()

    def read_var(self, var='', range=[], step=1):
        if not self.has_var(var):
            raise Exception(f'{var} is not found ...')

        # pycdf converts time to datetime.
        # This is way too smart... 
        var_info = self.read_var_info(var)

        # Work on range.
        maxrec = var_info['maxrec']
        nrange = len(range)
        if len(range) > 2:
            raise Exception(f'Invalid range: {range} ...')
        _range = range.copy()
        if nrange == 1:
            _range.append(_range[0]+1)
        elif nrange == 0:
            _range = [0,maxrec]
        else:
            _range.sort()
        _range = np.clip(_range, 0, maxrec)


        # Read data.
        data_type = var_info['cdf_type']
        if data_type in ['CDF_EPOCH','CDF_EPOCH16','CDF_TT2000']:
            data = self._cdflib.varget(var, startrec=_range[0], endrec=_range[1])
            return data[::step]
        else:
            data = self._pycdf[var][_range[0]:_range[1]:step]
            return data[...]



        # The IDL version has a functionality to shrink unnecessary dimensions.
        # So far I don't know if this is done already in pycdf.
        # Thus, let's do the simple thing to return as-is.

        





    def read_var_att(self, var=''):
        if not self.has_var(var):
            raise Exception(f'{var} is not found ...')
        return dict(self._pycdf[var].attrs)

    def read_var_info(self, var=''):
        if not self.has_var(var):
            raise Exception(f'{var} is not found ...')

        the_cdf = cdflib.CDF(self.filename)
        var_info = the_cdf.varinq(var)
        dim_vary = var_info['Dim_Vary']
#        dim_vary = [int(x != 0) for x in dim_vary]
        dim_vary = [valid_dim_vary[x] for x in dim_vary]
        
        return {
            'name': var_info['Variable'],
            'cdf_type': get_cdf_type_str(var_info['Data_Type']),
            'nelem': var_info['Num_Elements'],
            'iszvar': True,
            'rec_vary': var_info['Rec_Vary'],
            'maxrec': var_info['Last_Rec'],
            'dims': var_info['Dim_Sizes'],
            'dim_vary': dim_vary,
        }
        


    def del_var(self, var=''):
        if not self.has_var(var):
            return
        del self._pycdf[var]

    def del_setting(self, key, var=None):
        if var is None:
            self._pycdf.attrs.pop(key, None)
        else:
            self._pycdf[var].attrs.pop(key, None)

    def rename_setting(self, key, to='', var=None):
        if var is None:
            val = self._pycdf.attrs.pop(key, None)
            if val is not None: self._pycdf.attrs[to] = val
        else:
            val = self._pycdf[var].attrs.pop(key, None)
            if val is not None: self._pycdf[var].attrs[to] = val

    def save_setting(self, var=None, settings=None):
        if var is None:
            self._pycdf.attrs.update(settings)
        else:
            if self.has_var(var):
                self._pycdf[var].attrs.update(settings)

    
    def save_data(self, var, value=None, settings=None):
        """
        Save data to an existing var.
        """

        if value is None:
            raise Exception('No input data ...')

        if not self.has_var(var):
            raise Exception(f'{var} is not found ...')
        
        self._pycdf[var][...] = value

        if settings is not None:
            self.save_setting(var, settings=settings)

    
    def save_var(
        self,
        var,
        value=None,
        data_type=None,
        settings=None,
        save_as_one=False,
    ):
        """
        Save data and create a var.
        """

        if value is None:
            raise Exception('No input data ...')

        if self.has_var(var): self.del_var(var)

        data_dims = value.shape
        data_ndim = len(data_dims)

        numelem = 1
        if type(value[0]) == 'str': numelem = max(len(value))

        # Figure out if record varies.
        rec_vary = True
        if data_ndim == 1: rec_vary = False
        if data_dims[0] == 1: rec_vary = False
        if save_as_one: rec_vary = False

        # Figure out dimension.
        if rec_vary:
            if data_ndim > 1: dimensions = data_dims[1:]
            else: dimensions = []
        else:
            dimensions = data_dims


        if len(dimensions) == 0:
            self._pycdf.new(var, data=value, type=data_type,
            recVary=rec_vary, n_elements=numelem)
        else:
            dim_vary = np.ones(len(dimensions))
            self._pycdf.new(var, data=value, type=data_type,
            recVary=rec_vary, n_elements=numelem,
            dims=dimensions, dimVarys=dim_vary)
    

        if settings is not None:
            self.save_setting(var, settings=settings)

    def rename_var(self, var, to=''):
        if not self.has_var(var):
            raise Exception(f'{var} is not found ...')
        self._pycdf[var].rename(to)

    def read_skeleton(self):
        skeleton = dict()

        the_cdf = cdflib.CDF(self.filename)
        cdf_info = the_cdf.cdf_info()

        # Version string.
        version = ctypes.c_long(0)
        self.lib.call(const.GET_, const.CDF_VERSION_, ctypes.byref(version))
        version = version.value
        release = ctypes.c_long(0)
        self.lib.call(const.GET_, const.CDF_RELEASE_, ctypes.byref(release))
        release = release.value
        increment = ctypes.c_long(0)
        self.lib.call(const.GET_, const.CDF_INCREMENT_, ctypes.byref(increment))
        increment = increment.value
        version_str = f'{version}.{release}.{increment}'

        # Row or column majority.
        majority = ctypes.c_long(0)
        self.lib.call(const.GET_, const.CDF_MAJORITY_, ctypes.byref(majority))
        majority = majority.value
        valid_majority = dict([
            (const.ROW_MAJOR.value, 'ROW_MAJOR'),
            (const.COLUMN_MAJOR.value, 'COLUMN_MAJOR'),
        ])
        majority_str = valid_majority[majority]

        # Copyright.
        copyright_len = const.CDF_COPYRIGHT_LEN
        copyright = ctypes.create_string_buffer(copyright_len)
        self.lib.call(const.GET_, const.CDF_COPYRIGHT_, ctypes.byref(copyright))
        copyright = copyright.value.decode()

        # Encoding and decoding.
        encoding = ctypes.c_long(0)
        self.lib.call(const.GET_, const.CDF_ENCODING_, ctypes.byref(encoding))
        encoding = encoding.value

        decoding = ctypes.c_long(0)
        self.lib.call(const.CONFIRM_, const.CDF_DECODING_, ctypes.byref(decoding))
        decoding = decoding.value
        
        encoding_str = valid_coding[encoding]+'_ENCODING'
        decoding_str = valid_coding[decoding]+'_DECODING'


        # CDF Format.
        cdf_format = ctypes.c_long(0)
        self.lib.call(const.GET_, const.CDF_FORMAT_, ctypes.byref(cdf_format))
        cdf_format = cdf_format.value
        cdf_format_str = valid_cdf_format[cdf_format]

        # nzvar.
        nzvar = len(cdf_info['zVariables'])
        nrvar = len(cdf_info['rVariables'])

        ngatt = ctypes.c_long(0)
        self.lib.call(const.GET_, const.CDF_NUMgATTRS_, ctypes.byref(ngatt))
        ngatt = ngatt.value

        nvatt = ctypes.c_long(0)
        self.lib.call(const.GET_, const.CDF_NUMvATTRS_, ctypes.byref(nvatt))
        nvatt = nvatt.value

        # Header.
        skeleton['header'] = {
            'copyright': copyright,
            'cdf_format': cdf_format_str, 
            'decoding': decoding_str,
            'encoding': encoding_str,
            'filename': self.filename,
            'majority': majority_str,
            'version': version_str,
            'nzvar': nzvar,
            'nrvar': nrvar,
            'ngatt': ngatt,
            'nvatt': nvatt,
        }
        skeleton['name'] = skeleton['header']['filename']

        # Global attributes.
        skeleton['setting'] = self.read_setting()

        # Variables.
        vars = dict()

        # This part is not well tested.
        for var in cdf_info['rVariables']:
            vars[var] = self.read_var_info(var)
            vars[var]['setting'] = the_cdf.varattsget(var)

        for var in cdf_info['zVariables']:
            vars[var] = self.read_var_info(var)
            vars[var]['setting'] = the_cdf.varattsget(var)
        skeleton['vars'] = vars

        return skeleton

    def print_skeleton(self, filename=None):

        skeleton = self.read_skeleton()
        out_str = list()
        newline = lambda : out_str.append(os.linesep)

        # Header.
        out_str.append(f'! Skeleton table for {skeleton["name"]}')
        out_str.append(f'! Generated: {datetime.now()}')
        out_str.append(f'! CDF version: {skeleton["header"]["version"]}')
        newline()
        out_str.append('#header')
        format = '{0:<16}'
        out_str.append(format.format('CDF NAME:')+skeleton["header"]["filename"])
        out_str.append(format.format('DATA ENCODING:')+skeleton["header"]["encoding"])
        out_str.append(format.format('DATA DECODING:')+skeleton["header"]["decoding"])
        out_str.append(format.format('MAJORITY:')+skeleton["header"]["majority"])
        out_str.append(format.format('FORMAT')+skeleton["header"]["cdf_format"])
        out_str.append('!    R.Vars    Z.Vars    G.Atts    V.Atts')
        out_str.append('!    ------    ------    ------    ------')
        out_str.append(f'     {skeleton["header"]["nrvar"]:<10}{skeleton["header"]["nzvar"]:<10}{skeleton["header"]["ngatt"]:<10}{skeleton["header"]["nvatt"]:<10}')

        # Global attribute.
        newline()
        out_str.append('#GLOBALattributes')
        newline()
        gatt = skeleton['setting']
        for key, iter in zip(gatt.keys(),np.arange(skeleton['header']['ngatt'])):
            out_str.append(f'{iter:>4} {key}: {gatt[key]}')

        # Variables.
        newline()
        out_str.append('#Variables')
        newline()

        vars = self.vars()
        for var, iter in zip(vars, np.arange(len(vars))):
            var_info = skeleton['vars'][var]
            rec_vary = valid_rec_vary[var_info['rec_vary']]
            dim_str = ','.join([str(x) for x in var_info['dims']])
            dimvary_str = ','.join([str(x) for x in var_info['dim_vary']])
            if dim_str == '': dim_str = '0'
            if dimvary_str == '': dimvary_str = '0'

            out_str.append(f'{iter:>4} {var}')
            newline()
            out_str.append('!    CDF Type      # Elem    Max Rec     Rec Vary     Dimensions     Dim Vary')
            out_str.append('!    --------      ------    -------     --------     ----------     --------')
            out_str.append(f'     {var_info["cdf_type"]:<14}{var_info["nelem"]:<10}{var_info["maxrec"]:<12}{rec_vary:<13}{dim_str:<15}{dimvary_str}')
            newline()

            # Variable attribute.
            vatt = var_info['setting']
            for key in vatt:
                out_str.append(f'     {key:<34}{vatt[key]}')
            newline()



        if filename is not None:
            with open(filename, 'w') as f:
                for s in out_str:
                    if s != os.linesep: s+= os.linesep
                    f.write(s)
        else:
            for s in out_str:
                print(s)


## Test shows that both pycdf and cdflib start to use a lot of memory when loading variables.
## pycdf takes about half the time of cdflib to load several GB of data.
#
#import time
#
#def test_cdf():
#    file = '/Users/shengtian/rbspa_efw_l2_spec_20180927_v02.cdf'
#    file = '/Users/shengtian/rbspa_l1_vb1_20140802_v02.cdf'
##    with open(file, 'w+b'):
##        print(f'{file} opened ...')
#
#    cdfid = cdf(file)
#    print(cdfid.vatts())
#    cdfid.print_skeleton()
#
#    test_vars = ['epoch','vb1']
#
#    cdfid = cdf(file)
#    for var in test_vars:
#        tic = time.perf_counter()
#        data = cdfid.read_var(var, step=1000000)
#        toc = time.perf_counter()
#        print(f'{toc-tic:0.4f} seconds for loading {var}')
#        print(data.shape)
#
#    cdfid = cdflib.CDF(file)
#    cdf_info = cdfid.cdf_info()
#    for var in test_vars:
#        tic = time.perf_counter()
#        data = cdfid.varget(var)
#        toc = time.perf_counter()
#        print(f'{toc-tic:0.4f} seconds for loading {var}')
#
#
#if __name__ == '__main__':
#    test_cdf()