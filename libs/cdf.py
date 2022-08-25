import ctypes
import os
from datetime import datetime
import numpy as np
from spacepy import pycdf   # https://github.com/spacepy/spacepy/blob/master/spacepy/pycdf/
from spacepy.pycdf import const
import cdflib   # https://github.com/MAVENSDC/cdflib

"""
To achieve what my IDL cdf programs can do (https://github.com/tsssss/slib/tree/master/cdf).
Originally I use cdflib (https://github.com/MAVENSDC/cdflib), but it doesn't allow read and write at the same time.
Now I use pycdf (https://github.com/spacepy/spacepy/tree/master/spacepy/pycdf). It needs to manually install the CDF library (https://spdf.gsfc.nasa.gov/pub/software/cdf/)
The ideal solution is still use the route of cdflib, i.e., to avoid installing the CDF libarary separately.
"""

valid_cdftype = dict([
    (1, 'CDF_INT1'),
    (2, 'CDF_INT2'),
    (4, 'CDF_INT4'),
    (8, 'CDF_INT8'),
    (11, 'CDF_UINT1'),
    (12, 'CDF_UINT2'),
    (14, 'CDF_UINT4'),
    (21, 'CDF_REAL4'),
    (22, 'CDF_REAL8'),
    (31, 'CDF_EPOCH'),
    (32, 'CDF_EPOCH16'),
    (33, 'CDF_TIME_TT2000'),
    (41, 'CDF_BYTE'),
    (44, 'CDF_FLOAT'),
    (45, 'CDF_DOUBLE'),
    (51, 'CDF_CHAR'),
    (52, 'CDF_UCHAR'),
])


class cdf():
    filename = None
    pycdf = None
    
    def __init__(self, filename):
        self.filename = filename
        if os.path.exists(filename):
            self.pycdf = pycdf.CDF(filename, create=False, readonly=False)
        else:
            self.pycdf = pycdf.CDF(filename, create=True)
        
        _libpath, _library = pycdf.Library._find_lib()
        self.lib = pycdf.Library(_libpath, _library)

    def __del__(self):
        self.pycdf.close()

    def gatts(self):
        return list(self.pycdf.attrs.keys())

    def vatts(self):
        _vatts = list()
        for var in self.vars():
            vatts = self.read_var_att(var).keys()
            for vatt in vatts:
                if vatt not in _vatts: _vatts.append(vatt)
        return _vatts

    def read_setting(self, var=None):
        if var is None:
            return dict(self.pycdf.attrs)
        else:
            return self.read_var_att(var)

    def vars(self):
        return list(self.pycdf.keys())

    def has_var(self, var):
        return var in self.vars()

    def _transpose_data(self, data):
        dim = data.shape
        if len(dim) < 2: return data
        dim_order = np.roll(np.flip(np.arange(len(dim))),1)
        return np.transpose(data, dim_order)

    def read_var(self, var='', range=[], step=1):
        if not self.has_var(var):
            raise Exception(f'{var} is not found ...')
        # The IDL version has a functionality to shrink unnecessary dimensions.
        # So far I don't know if this is done already in pycdf.
        # Thus, let's do the simple thing to return as-is.
        nrange = len(range)
        if nrange == 0:
            data = self.pycdf[var]
        elif nrange > 2:
            raise Exception(f'Invalid range: {range} ...')
        else:
            data = self.pycdf[var]
            dim = data.shape
            nrec = dim[0]
            _range = range.copy()
            if nrange == 1: _range.append(_range[0]+1)

            _range.sort()
            if _range[0] < 0: _range[0] = 0
            if _range[1] > nrec: _range[1] = nrec
            if _range[1] < _range[0]:
                raise Exception(f'Invalid range: {range} ...')

            data = self.pycdf[var][_range[0]:_range[1]:step]
        return data[...]


    def read_var_att(self, var=''):
        if not self.has_var(var):
            raise Exception(f'{var} is not found ...')
        return dict(self.pycdf[var].attrs)

    def read_var_info(self, var=''):
        if not self.has_var(var):
            raise Exception(f'{var} is not found ...')

        the_cdf = cdflib.CDF(self.filename)
        var_info = the_cdf.varinq(var)
        dimvary = var_info['Dim_Vary']
        dimvary = [int(x != 0) for x in dimvary]
        
        return {
            'name': var_info['Variable'],
            'cdftype': valid_cdftype[var_info['Data_Type']],
            'nelem': var_info['Num_Elements'],
            'iszvar': True,
            'recvary': var_info['Rec_Vary'],
            'maxrec': var_info['Last_Rec'],
            'dims': var_info['Dim_Sizes'],
            'dimvary': dimvary,
        }
        


    def del_var(self, var=''):
        if not self.has_var(var):
            return
        del self.pycdf[var]

    def del_setting(self, key, var=None):
        if var is None:
            self.pycdf.attrs.pop(key, None)
        else:
            self.pycdf[var].attrs.pop(key, None)

    def rename_setting(self, key, to='', var=None):
        if var is None:
            val = self.pycdf.attrs.pop(key, None)
            if val is not None: self.pycdf.attrs[to] = val
        else:
            val = self.pycdf[var].attrs.pop(key, None)
            if val is not None: self.pycdf[var].attrs[to] = val

    def save_setting(self, var=None, settings=None):
        if var is None:
            self.pycdf.attrs.update(settings)
        else:
            if self.has_var(var):
                self.pycdf[var].attrs.update(settings)

    
    def save_data(self, var, value=None, settings=None):
        """
        Save data to an existing var.
        """

        if value is None:
            raise Exception('No input data ...')

        if not self.has_var(var):
            raise Exception(f'{var} is not found ...')
        
        self.pycdf[var][...] = value

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
            self.pycdf.new(var, data=value, type=data_type,
            recVary=rec_vary, n_elements=numelem)
        else:
            dim_vary = np.ones(len(dimensions))
            self.pycdf.new(var, data=value, type=data_type,
            recVary=rec_vary, n_elements=numelem,
            dims=dimensions, dimVarys=dim_vary)
    

        if settings is not None:
            self.save_setting(var, settings=settings)

    def rename_var(self, var, to=''):
        if not self.has_var(var):
            raise Exception(f'{var} is not found ...')
        self.pycdf[var].rename(to)

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
        
        valid_coding = dict([
            (const.NETWORK_ENCODING.value, 'NETWORK'),
            (const.SUN_ENCODING.value, 'SUN'),
            (const.VAX_ENCODING.value, 'VAX'),
            (const.DECSTATION_ENCODING.value, 'DECSTATION'), 
            (const.SGi_ENCODING.value, 'SGi'),
            (const.IBMPC_ENCODING.value, 'IMBPC'),
            (const.IBMRS_ENCODING.value, 'IBMRS'),
            (const.HOST_ENCODING.value, 'HOST'),
            (const.PPC_ENCODING.value, 'PPC'),
            (const.HP_ENCODING.value, 'HP'),
            (const.NeXT_ENCODING.value, 'NeXT'),
            (const.ALPHAOSF1_DECODING.value, 'ALPHAOSF1'),
            (const.ALPHAVMSd_ENCODING.value, 'ALPHAVMSd'),
            (const.ALPHAVMSg_ENCODING.value, 'ALPHAVMSg'),
            (const.ALPHAVMSi_ENCODING.value, 'ALPHAVMSi')
        ])
        encoding_str = valid_coding[encoding]+'_ENCODING'
        decoding_str = valid_coding[decoding]+'_DECODING'


        # CDF Format.
        cdfformat = ctypes.c_long(0)
        self.lib.call(const.GET_, const.CDF_FORMAT_, ctypes.byref(cdfformat))
        valid_cdfformat = dict([
            (const.SINGLE_FILE.value, 'SINGLE_FILE'),
            (const.MULTI_FILE.value, 'MULTI_FILE'),
        ])
        cdfformat = cdfformat.value
        cdfformat_str = valid_cdfformat[cdfformat]

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
            'cdfformat': cdfformat_str, 
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
        out_str.append(format.format('FORMAT')+skeleton["header"]["cdfformat"])
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
            if var_info['recvary']: recvary = 'VARY'
            else: recvary = 'NOVARY'
            dim_str = ','.join([str(x) for x in var_info['dims']])
            dimvary_str = ','.join([str(x) for x in var_info['dimvary']])
            if dim_str == '': dim_str = '0'
            if dimvary_str == '': dimvary_str = '0'

            out_str.append(f'{iter:>4} {var}')
            newline()
            out_str.append('!    CDF Type      # Elem    Max Rec     Rec Vary     Dimensions     Dim Vary')
            out_str.append('!    --------      ------    -------     --------     ----------     --------')
            out_str.append(f'     {var_info["cdftype"]:<14}{var_info["nelem"]:<10}{var_info["maxrec"]:<12}{recvary:<13}{dim_str:<15}{dimvary_str}')
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
