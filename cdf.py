import os.path
import cdflib
import re

class read(object):

    def __init__(self, ffn, vars='', prefix=''):
        if not os.path.exists(ffn):
            raise FileNotFoundError

        cdfid = cdflib.cdfread.CDF(ffn)

        # read basic info.
        skeleton = cdfid.cdf_info()
        zvars = skeleton['zVariables']
        rvars = skeleton['rVariables']
        gatts = []
        vatts = []
        for tatt in skeleton['Attributes']:
            tval = list(tatt.values()).pop()
            tkey = list(tatt.keys()).pop()
            if tval == 'Global':
                gatts.append(tkey)
            elif tval == 'Variable':
                vatts.append(tkey)
            else:
                print('Invalid attribute ...')

        # read global attribute.
        self.gatt = cdfid.globalattsget()

        # create header, includes names of zvar/rvar, vatt; and other basic infos.
        self.header = {'zvar': zvars, 'rvar': rvars, 'vatt': vatts}
        keys = skeleton.keys()
        for tkey in ['CDF', 'Version', 'Copyright', 'Encoding', 'Majority', 'Compressed']:
            if tkey in keys: self.header[tkey] = skeleton[tkey]

        self.data = {}
        self.vatt = {}
        if vars == '':
            vars = rvars+zvars
        else:
            if type(vars) == str: vars = [vars]
            if prefix != '':
                for i in range(0,len(vars)):
                    if not vars[i][0:len(prefix)] == prefix:
                        vars[i] = prefix+vars[i]
        for tvar in vars:
            if not tvar in list(self.data.keys()):
                self.data[tvar] = cdfid.varget(tvar)
                self.vatt[tvar] = cdfid.varattsget(tvar)
                # also read dependent variables.
                myvatts = list(self.vatt[tvar].keys())
                pattern = re.compile('DEPEND_*')
                depkeys = list(filter(pattern.match, myvatts))
                for tkey in depkeys:
                    ttvar = self.vatt[tvar][tkey]
                    if not ttvar in list(self.data.keys()):
                        self.data[ttvar] = cdfid.varget(ttvar)
                        self.vatt[ttvar] = cdfid.varattsget(ttvar)

        cdfid.close()
