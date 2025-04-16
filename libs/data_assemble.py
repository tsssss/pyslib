# @Author : Donglai
# @Time   : 11/8/2020 6:48 PM
# @Email  : dma96@atmos.ucla.edu donglaima96@gmail.com
import pickle

import numpy as np
import pandas as pd

import utils_DM


def data_assemble(selfmade_dir='/Volumes/data/donglai/selfmade/',
                  omni_dir='/Volumes/data/donglai/omni/',

                  startmin=-14400,
                  endmin=0,
                  lagstep=120,
                  res='5min',
                  avgflag=True,
                  instrument_name = 'rept',
                  probe = ['a','b'],
                  varname=['AE_INDEX', 'SYM_H', 'Pressure', 'flow_speed', 'BZ_GSM'],
                  position_name = ['Lm_eq_OP77Q_intxt','ED_MLAT_OP77Q_intxt','ED_MLT_OP77Q_intxt','ED_R_OP77Q_intxt'],
                  channel = 0,
                  sincos = True,
                  fl32 = True,):
    unix_file = selfmade_dir + 'unix_time_' + res
    with open(unix_file, 'rb') as f:
        unix_time = pickle.load(f)

    tdate = utils_DM.unix2datetime(unix_time)
    lag_frame_time = pd.DataFrame(data={'tdate':tdate,'unix_time':unix_time})
    item_per_num = int((endmin-startmin)/lagstep)
    lag_matrix_all = np.zeros((len(lag_frame_time),len(varname)*item_per_num))
    lag_name = []
    for i,name in zip(range(len(varname)),varname):
        item_frame = make_item_matrix(selfmade_dir=selfmade_dir,omni_dir = omni_dir,
                                      item_name=name,startmin=startmin,endmin=endmin,
                                      lagstep=lagstep,res=res,avgflag=True)
        #get value
        lag_name+=list(item_frame.columns)
        if fl32:
            
            lag_matrix_all[:,i*item_per_num:(i+1)*item_per_num] =np.float32(item_frame.values)
            print(name,' finished using float32')
        else:
            lag_matrix_all[:,i*item_per_num:(i+1)*item_per_num] =item_frame.values
            print(name,' finished using float64')
    #lag_frame = pd.DataFrame(lag_matrix_all,columns=lag_name)
    #lag_frame = pd.concat([lag_frame_time,lag_frame],axis=1)

    # Save data matrix as unix_time,mindex,pdata,flux

    if len(probe) == 2:
        unix_total = np.append(unix_time,unix_time)
    else:
        unix_total = unix_time


    pmatrix,pnames = get_position_data(selfmade_dir = selfmade_dir,instrument_name = instrument_name,probe = probe,
                      position_name = position_name,channel = channel,
                      res = res,sincos = sincos)
    if fl32:
        total_matrix = np.zeros((len(unix_total),1 + pmatrix.shape[1]+len(varname)*item_per_num),dtype = np.float32)
    else:
        total_matrix = np.zeros((len(unix_total),1 + pmatrix.shape[1]+len(varname)*item_per_num))
    column_names = [None]*(1 + pmatrix.shape[1]+len(varname)*item_per_num)
    total_matrix[:,0] = unix_total
    column_names[0] = 'unix_time'
    total_matrix[:,1:pmatrix.shape[1]] = pmatrix[:,:-1]
    column_names[1:pmatrix.shape[1]] = pnames[:-1]

    # save lag matrix
    total_matrix[:len(unix_time),pmatrix.shape[1]:-1] = lag_matrix_all
    column_names[pmatrix.shape[1]:-1] = lag_name
    if len(probe) == 2:
        total_matrix[len(unix_time):, pmatrix.shape[1]:-1] = lag_matrix_all

    # save flux
    total_matrix[:,-1] = pmatrix[:,-1]
    column_names[-1] = pnames[-1]

    return total_matrix,column_names






def make_item_matrix(selfmade_dir='/Volumes/data/donglai/selfmade/', omni_dir='/Volumes/data/donglai/omni/',
                     item_name=None, startmin=-14400, endmin=0, lagstep=120, res='5min', avgflag=True):
    """
    If avgflag is True, return avg value for example
    for end min = 0, retrun to the avg value in time -120 :0
    """

    # Get fix time

    unix_file = selfmade_dir + 'unix_time_' + res
    with open(unix_file, 'rb') as f:
        unix_time = pickle.load(f)
    tdate = utils_DM.unix2datetime(unix_time)
    frame = pd.DataFrame(data={'date': tdate, 'unix_time': unix_time})

    # Get omni_data
    omni_file = omni_dir + 'omni_' + res + '_' + item_name + '_gap_filled'
    omni_frame = pd.read_pickle(omni_file)
    omni_t = omni_frame['tdata'].values
    omni_data = omni_frame['data'].values
    if res == '5min':
        time_resolution = 5
    elif res =='1min':
        time_resolution = 1
    else:
        raise ValueError('Only support 1min and 5min for now')
    unix_time_extra = np.arange(unix_time[0] + startmin * 60, unix_time[0], int(time_resolution * 60))
    t_extra = utils_DM.unix2datetime(unix_time_extra)
    unix_time_extend = np.append(unix_time_extra, unix_time)
    t_extend = np.append(t_extra, tdate)
    
    omni_interp = np.interp(unix_time_extend, omni_t, omni_data, left=np.nan, right=np.nan)

    interp_frame = pd.DataFrame(data={'tdate_extend': t_extend,
                                      'unix_extend': unix_time_extend,
                                      'omni': omni_interp})

    lagnum = int(lagstep / time_resolution)
    ################ Key point

    interp_omni = (pd.Series(omni_interp).rolling(lagnum).mean()).values
    ##########################
    interp_frame['omni_interp'] = interp_omni
    for i in range(int((endmin -startmin) / lagstep)):
        omni_i = interp_omni[(int((endmin-startmin) / time_resolution) - (1 + i * lagnum)):int(endmin / time_resolution) -(1 + i * lagnum)]
        name_t = item_name+ '_t_' + str(i)
        frame[name_t] = omni_i

    item_assem_frame = frame.iloc[:,2:]
    # return frame
    return item_assem_frame

def get_position_data(selfmade_dir = '/Volumes/data/donglai/selfmade/',instrument_name = 'rept',probe = ['a','b'],
                      position_name = ['Lm_eq_OP77Q_intxt','ED_MLAT_OP77Q_intxt','ED_MLT_OP77Q_intxt','ED_R_OP77Q_intxt'],channel = 0,
                      res = '5min',sincos = False):
    """
    Read position data
    """

    if len(probe) == 2:
        print('Now dealing with 2 probe, first will deal with a, then deal with b, and it will be like:')
        print('time, R,MLT,MLAT,..flux')
        print('...(a data)...')
        print('...(b data)...')

    if not isinstance(probe, list):
        probe = [probe]

    unix_file = selfmade_dir + 'unix_time_' + res
    with open(unix_file, 'rb') as f:
        unix_time = pickle.load(f)

    tdate = utils_DM.unix2datetime(unix_time)
    frame = pd.DataFrame(data={'tdate': tdate, 'unix_time': unix_time})
    if not sincos:
        total_matrix = np.zeros((len(probe)*len(unix_time),len(position_name)+1))
    else:
        total_matrix = np.zeros((len(probe)*len(unix_time),len(position_name)+2))

    for p in probe:
        print('Dealing with probe',p)
        print('The time resolution is ', res)
        print('The instrument is ', instrument_name)
        print('The position names are ', position_name)
        print('The channel is ', channel)
        print('using sincos is', sincos)




        for pname in position_name:
            file_name = 'rbsp'+ p + '_' +pname + '_' + res
            file = selfmade_dir + file_name
            with open(file,'rb') as f:
                pdata = pickle.load(f)
            if not sincos:
                frame[pname] = pdata
            else:
                if 'MLT' in pname:# change MLT to sinMLT and cosMLT
                    frame[pname+'_sin'] = np.sin(np.deg2rad(pdata * 15))
                    frame[pname+'_cos'] = np.cos(np.deg2rad(pdata * 15))
                else:
                    frame[pname] = pdata



        # get flux
        flux_name =  'rbsp'+ p + '_eflux_'+'ch'+str(channel) +'_'+instrument_name +'_' + res
        flux_file = selfmade_dir + flux_name
        with open(flux_file,'rb') as f:
            fdata = pickle.load(f)
        frame['eflux'] = fdata


        if p =='b' and len(probe) == 2:
            total_matrix[len(tdate):] = frame.iloc[:,2:].values
        else:
            total_matrix[0:len(tdate)] = frame.iloc[:, 2:].values

    return total_matrix,frame.columns[2:]

