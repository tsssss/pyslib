import numpy as np
import datetime
import dateutil.parser
import cdflib

#---Time conversion. All times are in UTC.
# internally save time as (whole ut sec, fractional ut sec up to pica sec accuracy).

# t_epoch, accurate to 1 milli second, in milli sec.
# t_epoch16, accurate to 1 pico second, real part in sec, imagine part in pica sec.
# t_tt2000, accurate to 1 nano second, in nano sec, contains leap second.
# t_ut, accurate to 1 milli second, in sec.
# datetime, accurate to 1 micro second, in object.

class ut(object):
    t0_datetime = datetime.datetime(1970,1,1)

    # real part is the ut second, imaginary part is the fractional second.
    def __init__(self, times, format=''):

        # input can be an array of string or number, or a single string or number.
        if type(times) == str:  # input is a string, change it into a list.
            t_input = [times]
        elif not isinstance(times, (list,np.ndarray)): # input is not a list or nparray.
            t_input = [times]
        else: t_input = times

        # complex 128 includes 2 float 64, which have >14 significant digits.
        self.t_ep16 = np.zeros(len(t_input),dtype=np.complex128)


        # input is a string, parse each.
        if type(t_input[0]) == str:
            t_ut = np.empty(len(t_input))
            for i, ttime in enumerate(t_input):
                if format == '':        # no format code, use parser.
                    t_datetime = dateutil.parser.parse(ttime)
                else:                   # use explicit format codes.
                    t_datetime = datetime.datetime.strptime(ttime, format)
                t_ut[i] = (t_datetime-self.t0_datetime).total_seconds()
            self.t_ep16.real = np.remainder(t_ut, 1)
            self.t_ep16.imag = t_ut - self.t_ep16.real
        elif type(t_input[0]) == datetime.datetime:
            t_ut = np.empty(len(t_input))
            for i, ttime in enumerate(t_input):
                t_ut[i] = (ttime-self.t0_datetime).total_seconds()
            self.t_ep16.real = np.remainder(t_ut, 1)
            self.t_ep16.imag = t_ut - self.t_ep16.real
        else:
            # input should be number, then use numpy array.
            # datetime object is used in some conversions, it's accurate to milli sec.
            if type(t_input) == list:
                t_input = np.array(t_input)

            if format == '': format = 'ut'
            if format in ['ut','utc','unix']:   # ut in sec, accurate to milli sec.
                self.t_ep16.imag = np.remainder(t_input, 1)
                self.t_ep16.real = t_input - self.t_ep16.imag
            elif format == 'epoch':             # epoch is in msec, accurate to milli sec.
                t0 = cdflib.cdfepoch.breakdown_epoch(t_input[0])
                t_datetime = datetime.datetime(*t0)
                t0 = (t_datetime-self.t0_datetime).total_seconds()
                t_ut = t0+(t_input-t_input[0])*1e-3
                self.t_ep16.imag = np.remainder(t_ut, 1)
                self.t_ep16.real = t_ut-self.t_ep16.imag
            elif format == 'epoch16':   # epoch16 is in (sec,pica sec), accurate to pica sec.
                # get the ut sec for the first time.
                t_list = cdflib.cdfepoch.breakdown_epoch16(t_input[0])
                t_datetime = datetime.datetime(*t_list[0:6])
                t0 = (t_datetime-self.t0_datetime).total_seconds()      # ut sec, in sec.
                # decompose ut sec and fractional sec.
                self.t_ep16.real = t0+t_input.real-t_input.real[0]
                self.t_ep16.imag = t_input.imag*1e-12   # convert pica sec to sec.
            elif format == 'tt2000':    # tt2000 is in nano sec, accurate to nano sec.
                # get the ut sec for the first time.
                t_list = cdflib.cdfepoch.breakdown_tt2000(t_input[0])
                t_datetime = datetime.datetime(*t_list[0:6])
                t0_ut = (t_datetime-self.t0_datetime).total_seconds()      # ut sec, in sec.
                # decompose input time into sec and fractional sec in sec.
                t0_t2000 = np.longlong(t_input[0]-t_list[6]*1e6-t_list[7]*1e3-t_list[8])    # the first time without fractional sec.
                t_dt = np.int64(t_input-t0_t2000)       # nano sec relative to the first time.
                dt_dt = np.mod(t_dt, np.int64(1e9))   # the part of fractional sec in nano sec.
                self.t_ep16.real = t0_ut+(t_dt-dt_dt)*1e-9
                self.t_ep16.imag = dt_dt*1e-9


    def __getitem__(self, item):
        return self.t_ep16[item].real+self.t_ep16[item].imag

#    def __add__(self, other):
#        return ut(self.t_ep16.real+self.t_ep16.imag+other)
#    def __sub__(self, other):
#        return ut(self.t_ep16.real+self.t_ep16.imag-other)


    def ut(self):
        return  self.t_ep16.real+self.t_ep16.imag

    def string(self, format='%Y-%m-%d/%H:%M:%S'):
        t_string = []
        ut = self.t_ep16.real+self.t_ep16.imag
        for t_ut in ut:
            t_datetime = datetime.datetime.utcfromtimestamp(t_ut)
            t_string.append(t_datetime.strftime(format))
        return t_string

    def epoch(self):
        ut = self.t_ep16.real+self.t_ep16.imag
        t0 = datetime.datetime.utcfromtimestamp(ut[0])
        t0_epoch = cdflib.cdfepoch.compute_epoch([t0.year,t0.month,t0.day,t0.hour,
            t0.minute,t0.second,t0.microsecond])
        return t0_epoch+(ut-ut[0])*1e6

    def epoch16(self):
        ut = self.t_ep16.real
        t0 = datetime.datetime.utcfromtimestamp(ut[0])
        t0_epoch = cdflib.cdfepoch.compute_epoch([t0.year,t0.month,t0.day,t0.hour,
            t0.minute,t0.second,t0.microsecond])
        t1 = np.array(ut, dtype=complex)
        t1.real = t0_epoch*1e-6+(ut-ut[0])
        t1.imag = self.t_ep16.imag*1e12
        return t1

    def tt2000(self):
        ut = self.t_ep16.real
        t0 = datetime.datetime.utcfromtimestamp(ut[0])
        t0_tt2000 = cdflib.cdfepoch.compute_tt2000([t0.year,t0.month,t0.day,t0.hour,
            t0.minute,t0.second])
        return t0_tt2000+np.int64((ut-ut[0])*1e9)+np.int64(self.t_ep16.imag*1e9)

    def datetime(self):
        t_datetime = []
        ut = self.t_ep16.real+self.t_ep16.imag
        for t_ut in ut:
            t_datetime.append(datetime.datetime.utcfromtimestamp(t_ut))
        return t_datetime


