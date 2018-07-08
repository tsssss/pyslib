import os.path
import utils
import re
import cdf
import numpy as np


# a common block for all cdf reading jobs.
# including search index file, download file, replace fill value with nan.
def read_block(utr0, vars, rempattern, locpattern, rem_index, loc_index, update_index, prefix=''):
    # replace pattern with given time.
    remfns = utils.prepfile(utr0, rempattern)
    locfns = utils.prepfile(utr0, locpattern)

    # prepare each file in the list.
    for i in range(0,len(locfns)):
        remdir = os.path.dirname(remfns[i])
        remidx = os.path.join(remdir, rem_index)
        locdir = os.path.dirname(locfns[i])
        locidx = os.path.join(locdir, loc_index)
        locbfn = os.path.basename(locfns[i])

        if not os.path.exists(locidx) or update_index == True:
            utils.getfile(locidx, rempath=remdir)

        # check local index.
        # filter out the related files.
        with open(locidx) as f: idxfns = f.readlines()
        pattern = re.compile(locbfn)
        thefns = list(filter(pattern.search, idxfns))

        # sort the files and get the one of latest version.
        for j in range(0,len(thefns)):
            tfn = re.search('('+locbfn+')', thefns[j])
            thefns[j] = tfn.group(1)
        thefns = sorted(thefns)
        if len(thefns) == 0:
            print('Cannot find given file in local index ...')
        locfns[i] = os.path.join(locdir,thefns[-1])

        # get the file.
        locfns[i] = utils.getfile(locfns[i], rempath=remdir)

    # read data.
    dat0 = cdf.read(locfns[0], vars=vars, prefix=prefix)
    keys = list(dat0.data.keys())
    for i in range(1,len(locfns)):
        tdat = cdf.read(locfns[i], vars=vars, prefix=prefix)
        for tkey in keys:
            dat0.data[tkey] = np.concatenate((dat0.data[tkey],tdat.data[tkey]), axis=0)

    # replace fillval with nan.
    for tkey in keys:
        try:
            fillval = dat0.vatt[tkey]['FILLVAL']
            idx = np.where(dat0.data[tkey] == fillval)
            if len(idx) > 0: dat0.data[tkey][idx] = np.nan
        except: pass

    return dat0


def omni(utr0, datatype='1min', vars='', version='', update_index=False):
    # utr0 in ut sec. Can be 1 element, or a time range.

    if not os.path.exists(utils.DATA_ROOT_DIR): raise FileNotFoundError
    loc_root = os.path.join(utils.DATA_ROOT_DIR, 'omni')
    loc_index = 'SHA1SUM'
    rem_root = 'https://cdaweb.sci.gsfc.nasa.gov/pub/data/omni/omni_cdaweb'
    rem_index = 'SHA1SUM'

    if datatype == '1min':
        type1 = 'hro_'+datatype
        type2 = 'hro_'+datatype
    elif datatype == '5min':
        type1 = 'hro_'+datatype
        type2 = 'hro_'+datatype

    if version == '': vsn = 'v[0-9]{2}'
    else: vsn = version
    ext = 'cdf'

    # construct the pattern.
    baseptn = 'omni_'+type1+'_%Y%m01_'+vsn+'.'+ext
    rempattern = os.path.join(rem_root, 'omni_cdaweb', type2, '%Y', baseptn)
    locpattern = os.path.join(loc_root, 'omni_cdaweb', type2, '%Y', baseptn)

    # data
    dat0 = read_block(utr0, vars, rempattern, locpattern, rem_index, loc_index, update_index)
    keys = list(dat0.data.keys())

    # treat DEPEND_TIME.
    tvar0s = ['Epoch']
    tvar1s = ['omni_time']
    for i in range(0,len(tvar0s)):
        try:
            time0 = dat0.data[tvar0s[i]]
            time1 = utils.UT(time0, 'epoch')
            time1 = time1.ut()
            dat0.data[tvar1s[i]] = time1
            if len(utr0) == 2:
                utidx = np.where(np.logical_and(time1 >= utr0[0], time1 <= utr0[1]))
                dat0.data[tvar0s[i]] = dat0.data[tvar0s[i]][utidx]
                dat0.data[tvar1s[i]] = dat0.data[tvar1s[i]][utidx]
            for tkey in keys:
                if dat0.vatt[tkey]['DEPEND_0'] == tvar0s[i]:
                    dat0.vatt[tkey]['DEPEND_TIME'] = tvar1s[i]
                    dat0.vatt[tkey]['plot_type'] = 'scalar'
                    if len(utr0) == 2:
                        dat0.data[tkey] = dat0.data[tkey][utidx]    # only cut the 1st dimension, works for (nrec,3), (nrec,m,n), etc.
        except: pass


    return dat0


class themis(object):
    def __init__(self, probe):
        self.probe = probe
        self.pre0 = 'th'+probe+'_'
        self.data = {}
        self.vatt = {}

    def efi(self, utr0, datatype='efi', level='l2', vars='', version='', update_index=False):
        if not os.path.exists(utils.DATA_ROOT_DIR): raise FileNotFoundError
        loc_root = os.path.join(utils.DATA_ROOT_DIR, 'themis')
        loc_index = 'SHA1SUM'
        rem_root = 'https://cdaweb.sci.gsfc.nasa.gov/pub/data/themis'
        rem_index = 'SHA1SUM'

        type1 = datatype
        type2 = datatype

        if version == '': vsn = 'v[0-9]{2}'
        else: vsn = version
        ext = 'cdf'

        # construct the pattern.
        baseptn = 'th'+self.probe+'_'+level+'_'+type1+'_%Y%m%d_'+vsn+'.'+ext
        rempattern = os.path.join(rem_root, 'th'+self.probe, level, type2, '%Y', baseptn)
        locpattern = os.path.join(loc_root, 'th'+self.probe, level, type2, '%Y', baseptn)

        # data
        pre0 = 'th'+self.probe+'_'
        dat0 = read_block(utr0, vars, rempattern, locpattern, rem_index, loc_index, update_index, prefix=pre0)
        keys = list(dat0.data.keys())

        # treat DEPEND_TIME.
        vars = ['efs_dot0_gsm']    # TODO add all vars.
        for i in range(0,len(vars)): vars[i] = pre0+vars[i]
        for tvar in vars:
            if tvar in keys:
                dat0.vatt[tvar]['plot_type'] = 'vector'


        # trim to given time.
        if len(utr0) == 2:
            # find all times.
            timevars = []
            for tkey in keys:
                try:
                    ttimevar = dat0.vatt[tkey]['DEPEND_TIME']
                    if not ttimevar in timevars:
                        timevars.append(ttimevar)
                except: pass
            # trim each time and the variables depend n the time.
            for ttimevar in timevars:
                time1 = dat0.data[ttimevar]
                utidx = np.where(np.logical_and(time1 >= utr0[0], time1 <= utr0[1]))
                dat0.data[ttimevar] = time1[utidx]
                for tkey in keys:
                    try:
                        if dat0.vatt[tkey]['DEPEND_TIME'] == ttimevar:
                            dat0.data[tkey] = dat0.data[tkey][utidx]
                    except: pass

        # merge to data, assume no name conflict.
        self.data = {**self.data, **dat0.data}
        self.vatt = {**self.vatt, **dat0.vatt}


    def fgm(self, utr0, datatype='fgm', level='l2', vars='', version='', update_index=False):
        if not os.path.exists(utils.DATA_ROOT_DIR): raise FileNotFoundError
        loc_root = os.path.join(utils.DATA_ROOT_DIR, 'themis')
        loc_index = 'SHA1SUM'
        rem_root = 'https://cdaweb.sci.gsfc.nasa.gov/pub/data/themis'
        rem_index = 'SHA1SUM'

        type1 = datatype
        type2 = datatype

        if version == '': vsn = 'v[0-9]{2}'
        else: vsn = version
        ext = 'cdf'

        # construct the pattern.
        baseptn = 'th'+self.probe+'_'+level+'_'+type1+'_%Y%m%d_'+vsn+'.'+ext
        rempattern = os.path.join(rem_root, 'th'+self.probe, level, type2, '%Y', baseptn)
        locpattern = os.path.join(loc_root, 'th'+self.probe, level, type2, '%Y', baseptn)

        # data
        pre0 = 'th'+self.probe+'_'
        dat0 = read_block(utr0, vars, rempattern, locpattern, rem_index, loc_index, update_index, prefix=pre0)
        keys = list(dat0.data.keys())

        # treat DEPEND_TIME.
        vars = ['fgs_gsm']    # TODO add all vars.
        for i in range(0,len(vars)): vars[i] = pre0+vars[i]
        for tvar in vars:
            if tvar in keys:
                dat0.vatt[tvar]['plot_type'] = 'vector'


        # trim to given time.
        if len(utr0) == 2:
            # find all times.
            timevars = []
            for tkey in keys:
                try:
                    ttimevar = dat0.vatt[tkey]['DEPEND_TIME']
                    if not ttimevar in timevars:
                        timevars.append(ttimevar)
                except: pass
            # trim each time and the variables depend n the time.
            for ttimevar in timevars:
                time1 = dat0.data[ttimevar]
                utidx = np.where(np.logical_and(time1 >= utr0[0], time1 <= utr0[1]))
                dat0.data[ttimevar] = time1[utidx]
                for tkey in keys:
                    try:
                        if dat0.vatt[tkey]['DEPEND_TIME'] == ttimevar:
                            dat0.data[tkey] = dat0.data[tkey][utidx]
                    except: pass

        # merge to data, assume no name conflict.
        self.data = {**self.data, **dat0.data}
        self.vatt = {**self.vatt, **dat0.vatt}


class rbsp(object):
    def __init__(self, probe):
        if not os.path.exists(utils.DATA_ROOT_DIR): raise FileNotFoundError
        self.loc_root = os.path.join(utils.DATA_ROOT_DIR, 'rbsp')

        self.probe = probe
        self.data = {}
        self.vatt = {}

    def efw(self, utr0, datatype='efw', level='l3', version='', update_index=False, vars=''):
        loc_root = self.loc_root
        loc_index = 'SHA1SUM'
        rem_root = 'https://cdaweb.sci.gsfc.nasa.gov/pub/data/rbsp'
        rem_index = 'SHA1SUM'

        type1 = datatype
        type2 = datatype

        if version == '':
            vsn = 'v[0-9]{2}'
        else:
            vsn = version
        ext = 'cdf'

        # construct the pattern.
        baseptn = 'rbsp'+self.probe+'_'+type1+'-'+level+'_%Y%m%d_'+vsn+'.'+ext
        rempattern = os.path.join(rem_root, 'rbsp'+self.probe, type2, '%Y', baseptn)
        locpattern = os.path.join(loc_root, 'rbsp'+self.probe, type2, '%Y', baseptn)

        # data
        dat0 = read_block(utr0, vars, rempattern, locpattern, rem_index, loc_index, update_index)
        keys = list(dat0.data.keys())

    def emfisis(self, utr0, datatype='4sec', level='l3', version='', update_index=False, coord='gsm', vars=''):
        loc_root = self.loc_root
        loc_index = 'SHA1SUM'
        rem_root = 'https://cdaweb.sci.gsfc.nasa.gov/pub/data/rbsp'
        rem_index = 'SHA1SUM'

        type1 = datatype
        type2 = datatype

        if version == '': vsn = 'v[0-9.]{5}'
        else: vsn = version
        ext = 'cdf'

        # construct the pattern.
        baseptn = 'rbsp-'+self.probe+'_magnetometer_'+type1+'-'+coord+'_emfisis-'+level+'_%Y%m%d_'+vsn+'.'+ext
        rempattern = os.path.join(rem_root, 'rbsp'+self.probe, level, 'emfisis', 'magnetometer', type2, coord, '%Y', baseptn)
        locpattern = os.path.join(loc_root, 'rbsp'+self.probe, 'emfisis', level, type2, coord, '%Y', baseptn)

        # data
        dat0 = read_block(utr0, vars, rempattern, locpattern, rem_index, loc_index, update_index)
        keys = list(dat0.data.keys())

        # treat DEPEND_TIME.
        tvar0s = ['Epoch']
        tvar1s = ['rbsp'+self.probe+'_emfisis_'+datatype+'_time']
        for i in range(0,len(tvar0s)):
            try:
                time0 = dat0.data[tvar0s[i]]
                time1 = utils.UT(time0, 'tt2000')
                time1 = time1.ut()
                dat0.data[tvar1s[i]] = time1
                for tkey in keys:
                    if dat0.vatt[tkey]['DEPEND_0'] == tvar0s[i]:
                        dat0.vatt[tkey]['DEPEND_TIME'] = tvar1s[i]
            except: pass

        vars = ['Mag']    # TODO add all vars.
        for tvar in vars:
            if tvar in keys:
                dat0.vatt[tvar]['plot_type'] = 'vector'

        # trim to given time.
        if len(utr0) == 2:
            # find all times.
            timevars = []
            for tkey in keys:
                try:
                    ttimevar = dat0.vatt[tkey]['DEPEND_TIME']
                    if not ttimevar in timevars:
                        timevars.append(ttimevar)
                except: pass
            # trim each time and the variables depend n the time.
            for ttimevar in timevars:
                time1 = dat0.data[ttimevar]
                utidx = np.where(np.logical_and(time1 >= utr0[0], time1 <= utr0[1]))
                dat0.data[ttimevar] = time1[utidx]
                for tkey in keys:
                    try:
                        if dat0.vatt[tkey]['DEPEND_TIME'] == ttimevar:
                            dat0.data[tkey] = dat0.data[tkey][utidx]
                    except: pass

        # merge to data, assume no name conflict.
        self.data = {**self.data, **dat0.data}
        self.vatt = {**self.vatt, **dat0.vatt}