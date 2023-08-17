#neo 6m gps plot blackouts
'''
# neo6mgps_plot_blackouts.py
# created by mahemys; 2019.09.08
# !perfect, but works!
# GNU-GPL; no license; free to use!
# update 2019-09-08; initial review
#
#------------------------------------------------------------
# purpose
# neo-6m gps module data collection using serial port of the device and plotting relevant graphs using matplotlib
# 
#------------------------------------------------------------
# process
# first convert db to csv; neo6mgps_db.db -> neo6mgps.csv
# run this script to generate downtime or blackouts graphs
# 
#------------------------------------------------------------
'''
import os
import numpy as np
import pandas as pd

from datetime import datetime, timedelta

dt_start = datetime.now()
print(dt_start, 'start...')

try:
    #id,utc_dt,lat,dirLat,lon,dirLon,alt,altUni,sat
    #0,1,2,3,4,5,6,7,8
    #read file in chunks, append and create df, exclude non datastring
    chunklist = []
    chunksize = 100000
    for chunk in  pd.read_csv('neo6mgps.csv', delimiter=',', skip_blank_lines=True, low_memory=False, chunksize=chunksize):
        chunklist.append(chunk)
    df = pd.concat(chunklist, axis= 0).dropna()
    del chunklist
    #print(df.info())
    print(df.head())
    print(df.shape)
except:
    print('Exception: #list to array, neo6mgps.csv...')
    pass

def convert_to_dd(loc_in_dms_format):
    try:
        loc_string= str(loc_in_dms_format)
        loc_split = loc_string.split(' ')
        loc_hour  = int(loc_split[0])
        loc_mins  = int(loc_split[1])
        loc_secs  = float(loc_split[2])
        loc_in_dd = loc_hour + (loc_mins/60 + (loc_secs/3600))
        return float("{:.6f}".format(loc_in_dd))
    except:
        pass
def convert_dir_to_sign(dir_lat_lon):
    try:
        pos = ['N', 'E']
        neg = ['S', 'W']
        dir_string = str(dir_lat_lon)
        if dir_string.startswith(tuple(pos)):
            dir_sign = 1
            #print(dir_string, 'pos, mul by +1')
        elif dir_string.startswith(tuple(neg)):
            dir_sign = -1
            #print(dir_string, 'neg, mul by -1')
        return dir_sign
    except:
        pass
def convert_dt_to_date(utc_dt):
    try:
        dt_date = utc_dt
        dt_date = datetime.strptime(dt_date, '%Y-%m-%d %H:%M:%S')
        #print(dt_date)
        return dt_date
    except:
        pass
try:
    #convert [DMS] to [DD], multiply [DD] by [dir], drop [dir] drop [altUni]...
    #df['utc_dt']    = df['utc_dt'].apply(convert_dt_to_date)
    df['utc_dt']    = pd.to_datetime(df['utc_dt'], format='%Y-%m-%d %H:%M:%S')
    '''
    df['lat']       = df['lat'].apply(convert_to_dd)
    df['lon']       = df['lon'].apply(convert_to_dd)
    df['dirLat']    = df['dirLat'].apply(convert_dir_to_sign)
    df['dirLon']    = df['dirLon'].apply(convert_dir_to_sign)
    df['lat']       = df['lat'] * df['dirLat']
    df['lon']       = df['lon'] * df['dirLon']
    df.drop('dirLat', axis=1, inplace=True)
    df.drop('dirLon', axis=1, inplace=True)
    df.drop('altUni', axis=1, inplace=True)
    #print(df.info())
    #print(df.head())
    #print(df.shape)

    #assign values...
    idd = df['id'].values
    utc = df['utc_dt'].values
    lat = df['lat'].values
    lon = df['lon'].values
    alt = df['alt'].values
    sat = df['sat'].values
    '''
except:
    print('Exception: #convert [DMS] to [DD]')
    pass

#find dates in utc_dt
df['day'] = df['utc_dt'].dt.to_period('D')
day_list  = df['day'].dt.strftime('%Y-%m-%d').unique()
print('day_list {} {}'.format(len(day_list), day_list))

sat_list   = df.groupby('day')['sat'].count().tolist()
print('sat_list {} {}'.format(len(sat_list), sat_list))

#find missing timestamps => diff method
df['day']  = df['utc_dt'].dt.to_period('D')
#df['diff'] = df['utc_dt'].diff()               #diff utc => overall df, error if tblko is 0
df['diff'] = df.groupby('day')['utc_dt'].diff() #diff utc => groupby day, no error if tblko is 0
df['diff'] = df['diff'].fillna(pd.Timedelta(seconds=0))
df['tsec'] = df['diff'].dt.total_seconds()
#print(df.info())
#print(df.head())
#print(df.shape)
#print(df)

#dd => only lines with tsec greater than 1, less than 1 to retain line with 0 tsec
#use "bitwise" | (or) or & (and) operations
dd = df.loc[(df['tsec'] > 1) | (df['tsec'] < 1)].reset_index(drop = True)
#print(dd.info())
print(dd.head())
print(dd.shape)
#print(dd)

print('Total missing count {}'.format(len(dd)))

#groupby day...
#bo_day_list  => unique day list
#bo_tcou_list => total numer of blackouts in sec
#bo_tsec_list => total duration of blackouts in sec
#tblko_list   => [tsec - tcoun] #tcoun has instance + records #tblko_list + bo_tsec_list => dsec_list
#utc_min      => min time of day in sec
#utc_max      => max time of day in sec
#dsec_list    =>  #24hrs in sec - min time of day in sec
#idsec_list   => ideal total seconds per day

bo_day_list  = dd['day'].dt.strftime('%Y-%m-%d').unique()
print('bo_day_list  {} {}'.format(len(bo_day_list), bo_day_list))

#subtract 1 from all in bo_tsec_cou => as we have considered line with 0 tsec.
bo_tcou_list = dd.groupby('day')['tsec'].count().tolist()
bo_tcou_list[:] = [x - 1 for x in bo_tcou_list]
print('bo_tcou_list {} {}'.format(len(bo_tcou_list), bo_tcou_list))

bo_tsec_list = dd.groupby('day')['tsec'].sum().astype(int).tolist()
print('bo_tsec_list {} {}'.format(len(bo_tsec_list), bo_tsec_list))

#get min max of utc => groupby day => from original df
utc_min = df.groupby('day')['utc_dt'].min().tolist()
utc_max = df.groupby('day')['utc_dt'].max().tolist()
#print('utc_min      {} {}'.format(len(utc_min), utc_min))
#print('utc_max      {} {}'.format(len(utc_max), utc_max))

#get actual dsec
dsec_list = []
for i in range(0, len(utc_min)):
    if i == len(utc_min)-1:
        #last day
        utc_mxx = utc_max[i]
        utc_mxsec = (utc_mxx.hour *60*60) + (utc_mxx.minute *60) + utc_mxx.second
        dsec_list.append(utc_mxsec)
    else:
        #first and other days
        utc_mnn = utc_min[i]
        utc_sec = (utc_mnn.hour *60*60) + (utc_mnn.minute *60) + utc_mnn.second
        dsec_list.append((24*60*60) - utc_sec)
print('dsec_list    {} {}'.format(len(dsec_list), dsec_list))

idsec_list = [24*60*60] * len(bo_day_list)
print('idsec_list   {} {}'.format(len(idsec_list), idsec_list))

tblko_list = [i - j for i, j in zip(bo_tsec_list, bo_tcou_list)]
print('tblko_list   {} {}'.format(len(tblko_list), tblko_list))

#assign values...
t_utc = dd['utc_dt'].values
t_sec = dd['tsec'].values

dt_stop = datetime.now()
print(dt_stop, 'file processing complete...')
dt_diff = dt_stop - dt_start
print('Time taken {}'.format(dt_diff))

#stop_further_execution_by_generating_error

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#fig = plt.figure(figsize=(20,10))
fig = plt.figure()
fig.suptitle('Neo-6m GPS - Downtime / Blackouts data')

#Top Half Plot
#Scatter >> X-utc_dt >> Y-tsec
plt.subplot(3, 1, 1)

#Grid
plt.minorticks_on()
plt.grid(b=True, which='major', color='k', linestyle=':', linewidth=0.5, alpha=0.25)
plt.grid(b=True, which='minor', color='gray', linestyle=':', linewidth=0.5, alpha=0.2)

try:
    #Plot
    plt.plot(t_utc, t_sec, c='r', label='downtime', marker='o', ms=1, ls='-', lw=1, alpha=0.5)
    #plt.scatter(t_utc, t_sec, c='r', label='downtime', marker='o', s=5, alpha=0.5)
except:
    print('Exception: #Top Half Plot')
    pass
try:
    #Details
    #plt.xlabel('DateTime UTC')
    plt.ylabel('Blackouts duration in sec')
    plt.legend(loc=1)#'best')#Shows label, Best Location
    #plt.title('Neo-6m GPS - Blackouts duration in sec')
except:
    print('Exception: #Title #Top Half Plot')
    pass

print(datetime.now(), 'Top Half Plot complete...')

#Mid Half Plot
#Scatter >> X-utc_dt >> Y-alt
plt.subplot(3, 1, 2)

#Grid
plt.minorticks_on()
plt.grid(b=True, which='major', color='k', linestyle=':', linewidth=0.5, alpha=0.25)
plt.grid(b=True, which='minor', color='gray', linestyle=':', linewidth=0.5, alpha=0.2)

try:
    #Plot bar
    #total seconds per day #actutal total seconds per day
    plt.bar(bo_day_list, idsec_list, label='', color='g', align='center', width=0.2, alpha=0.2)
    plt.bar(bo_day_list, dsec_list, label='uptime', color='g', align='center', width=0.2, alpha=0.4)
    
    #Plot bar
    width = 0.2
    x_pos = np.arange(len(bo_day_list))
    y_pos = np.arange(len(bo_tsec_list))
    plt.bar(x_pos, bo_tsec_list, label='blackout', color='r', align='center', width=width, alpha=0.5)
    plt.xticks(x_pos, bo_day_list)
    for i, h in enumerate(tblko_list):
        plt.text((x_pos[i]), h, '{:0.2f}%\n{}s\n{}'\
                 .format((tblko_list[i]/dsec_list[i]*100), h, timedelta(seconds=h)), color='k', ha='center', va='bottom')
except:
    print('Exception: #Mid Half Plot')
    pass
try:
    #Details
    #plt.xlabel('DateTime UTC')
    plt.ylabel('Total duration of Blackouts in sec')
    plt.legend(loc=1)#'best')#Shows label, Best Location
    #plt.title('Neo-6m GPS - Total duration of Blackouts in sec')
except:
    print('Exception: #Title #Mid Half Plot')
    pass

print(datetime.now(), 'Mid Half Plot complete...')

#Bottom Half Plot
#Scatter >> X-utc_dt >> Y-sat
plt.subplot(3, 1, 3)

#Grid
plt.minorticks_on()
plt.grid(b=True, which='major', color='k', linestyle=':', linewidth=0.5, alpha=0.25)
plt.grid(b=True, which='minor', color='gray', linestyle=':', linewidth=0.5, alpha=0.2)
''
try:
    #Plot bar
    width = 0.2
    x_pos = np.arange(len(bo_day_list))
    y_pos = np.arange(len(bo_tcou_list))
    plt.bar(x_pos, bo_tcou_list, label='instance', color='b', align='center', width=width, alpha=0.5)
    plt.xticks(x_pos, bo_day_list)
    for i, h in enumerate(bo_tcou_list):
        plt.text((x_pos[i]), h, '#{}'.format(h), color='k', ha='center', va='bottom')
except:
    print('Exception: #Bottom Half Plot')
    pass
''
try:
    #Details
    plt.xlabel('DateTime UTC')
    plt.ylabel('Total # of Blackouts')
    plt.legend(loc=1)#'best')#Shows label, Best Location
    #plt.title('Neo-6m GPS - Total # of Blackouts')
except:
    print('Exception: #Title #Bottom Half Plot')
    pass

print(datetime.now(), 'Bottom Plot complete...')

dt_stop = datetime.now()
print(dt_stop, 'all tasks complete...')
dt_diff = dt_stop - dt_start
print('Time taken {}'.format(dt_diff))

fig.canvas.set_window_title('Neo-6m GPS')
mng = plt.get_current_fig_manager()
mng.window.state('zoomed')
plt.show()
