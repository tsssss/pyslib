import os.path
import sread.utils.utils_old as utils_old
import re
import cdf
import numpy as np
import datatype


def read_block(utr0, vars, rempattern, locpattern, rem_index, loc_index, update_index, prefix=''):
    """
    A common block to load data: search index file, download file, replace fill value with nan.
    :param utr0: time or time range in ut (class).
    :param vars: a list of string.
    :param rempattern: pattern for remote url, a string with %x format.
    :param locpattern: pattern for local file.
    :param rem_index: url for remote index, containing info of all files under current folder.
    :param loc_index: url for local index.
    :param update_index: set to update local index.
    :param prefix: optional prefix for var in cdf, e.g., 'tha_'.
    :return: sdata (class).
    """

    # replace pattern with given time.
    remfns = utils_old.prepfile(utr0, rempattern)
    locfns = utils_old.prepfile(utr0, locpattern)

    # prepare each file in the list.
    for i in range(0,len(locfns)):
        remdir = os.path.dirname(remfns[i])
        remidx = os.path.join(remdir, rem_index)
        locdir = os.path.dirname(locfns[i])
        locidx = os.path.join(locdir, loc_index)
        locbfn = os.path.basename(locfns[i])

        if not os.path.exists(locidx) or update_index == True:
            utils_old.getfile(locidx, rempath=remdir)

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
        locfns[i] = utils_old.getfile(locfns[i], rempath=remdir)

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

def var_block(dat0, utvar0, utvar1, var0s, var1s, utr0):
    """
    A common block to: remove unwanted vars, change name of wanted vars,
        add all vars depend on the time var, trim data to utr0.
    :param dat0: sdata (class).
    :param utvar0: time var old.
    :param utvar1: time var new.
    :param var0s: wanted vars old.
    :param var1s: wanted vars new.
    :param utr0: time or time range in ut (class).
    :return: None.
    """

    # remove unwanted vars.
    vars = []
    for key in dat0.data.keys():
        if not key in var0s:
            vars.append(key)
    for var in vars:
        dat0.data.pop(var, None)
        dat0.vatt.pop(var, None)

    # rename wanted vars.
    depvars = []
    for i in range(len(var1s)):
        dat0.data[var1s[i]] = dat0.data.pop(var0s[i])
        dat0.vatt[var1s[i]] = dat0.vatt.pop(var0s[i])
        if var0s[i] != utvar0:  # change dependent to utvar.
            dat0.vatt[var1s[i]]['depend_0'] = utvar1
            depvars.append(var1s[i])

    # change time to ut, add vars depend on it.
    dat0.data[utvar1] = datatype.ut(dat0.data[utvar1], 'unix')
    dat0.vatt[utvar1]['depend_var'] = depvars


    # trim to given time.
    if len(utr0) == 2:
        # trim each time and the variables depend n the time.
        time1 = dat0.data[utvar1]
        utidx = np.where(np.logical_and(time1 >= utr0[0], time1 <= utr0[1]))
        dat0.data[utvar1] = time1[utidx]
        depvars = dat0.vatt[utvar1]['depend_var']
        for var in depvars:
            dat0.data[var] = dat0.data[var][utidx]



def omni(utr0, datatype='1min', vars='', version='', update_index=False):
    # utr0 in ut sec. Can be 1 element, or a time range.

    if not os.path.exists(utils_old.DATA_ROOT_DIR): raise FileNotFoundError
    loc_root = os.path.join(utils_old.DATA_ROOT_DIR, 'omni')
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
            time1 = utils_old.UT(time0, 'epoch')
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


class themis(datatype.sdata):
    def __init__(self, probe):
        self.probe = probe
        self.pre0 = 'th'+probe+'_'
        self.data = {}
        self.vatt = {}

    def bfield(self, utr0):
        """
        Read THEMIS B field in FGM L2 data.
        :param utr0: time or time range in ut (class).
        :return: sdata (class), include ['thx_b_gsm','thx_b_gsm_time','thx_db_gsm','thx_b0_gsm'].
        """

        vars = self.pre0+'fgs_gsm'
        dat0 = self.FGM(utr0, datatype='fgm', level='l2', vars=vars, update_index=False)

        # remove unwanted vars and rename wanted vars.
        utvar0 = self.pre0+'fgs_time'
        utvar1 = self.pre0+'fgs_time'
        var0s = [utvar0, self.pre0+'fgs_gsm']
        var1s = [utvar1, self.pre0+'b_gsm']
        var_block(dat0, utvar0, utvar1, var0s, var1s, utr0)

        # add default settings.
        var = self.pre0+'b_gsm'
        unit = 'nT'
        coord = 'GSM'
        coord_labels = ['x','y','z']
        legend = []
        for i in range(len(coord_labels)):
            legend.append(coord+' $B_'+coord_labels[i]+'$')

        dat0.vatt[var]['display_type'] = 'vector'
        dat0.vatt[var]['unit'] = unit
        dat0.vatt[var]['coord'] = coord
        dat0.vatt[var]['coord_labels'] = coord_labels
        dat0.vatt[var]['colors'] = ['red','green','blue']
        dat0.vatt[var]['ylabel'] = '('+unit+')'
        dat0.vatt[var]['legend'] = legend

        # separate b0 and b.

        self.data.update(dat0.data)
        self.vatt.update(dat0.vatt)

        return self


    def efield(self, utr0):
        """
        Read THEMIS E field in EFI L2 data.
        :param utr0: time or time range in ut (class).
        :return: sdata (class), include ['thx_edot0_gsm','thx_edot0_gsm_time'].
        """

        vars = self.pre0+'efs_dot0_gsm'
        dat0 = self.EFI(utr0, datatype='efi', level='l2', vars=vars, update_index=False)

        # remove unwanted vars, rename wanted vars, add depend vars to time, trim to utr0.
        utvar0 = self.pre0+'efs_dot0_time'
        utvar1 = self.pre0+'efs_time'
        var0s = [utvar0, self.pre0+'efs_dot0_gsm']
        var1s = [utvar1, self.pre0+'edot0_gsm']
        var_block(dat0, utvar0, utvar1, var0s, var1s, utr0)

        # add default settings.
        var = self.pre0+'edot0_gsm'
        unit = 'mV/m'
        coord = 'GSM'
        coord_labels = ['x','y','z']
        legend = []
        for i in range(len(coord_labels)):
            legend.append(coord+' $E_'+coord_labels[i]+'$')

        dat0.vatt[var]['display_type'] = 'vector'
        dat0.vatt[var]['unit'] = unit
        dat0.vatt[var]['coord'] = coord
        dat0.vatt[var]['coord_labels'] = coord_labels
        dat0.vatt[var]['colors'] = ['red','green','blue']
        dat0.vatt[var]['ylabel'] = '('+unit+')'
        dat0.vatt[var]['legend'] = legend

        self.data.update(dat0.data)
        self.vatt.update(dat0.vatt)

        return self

#---reading functions based on instrument.
    def EFI(self, utr0, datatype='efi', level='l2', vars='', version='', update_index=False):
        if not os.path.exists(utils_old.DATA_ROOT_DIR): raise FileNotFoundError
        loc_root = os.path.join(utils_old.DATA_ROOT_DIR, 'themis')
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
        return dat0


    def FGM(self, utr0, datatype='fgm', level='l2', vars='', version='', update_index=False):
        if not os.path.exists(utils_old.DATA_ROOT_DIR): raise FileNotFoundError
        loc_root = os.path.join(utils_old.DATA_ROOT_DIR, 'themis')
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
        return dat0


class rbsp(object):
    def __init__(self, probe):
        if not os.path.exists(utils_old.DATA_ROOT_DIR): raise FileNotFoundError
        self.loc_root = os.path.join(utils_old.DATA_ROOT_DIR, 'rbsp')

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
                time1 = utils_old.UT(time0, 'tt2000')
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


# utr0 = datatype.ut(['2014-08-28/09:30','2014-08-28/11:30'])
# tha = themis('a')
# tha.efield(utr0)