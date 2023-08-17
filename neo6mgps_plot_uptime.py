#neo 6m gps plot uptime
'''
# neo6mgps_plot_uptime.py
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
# run this script to generate uptime graphs
# 
#------------------------------------------------------------
'''
import os
import numpy as np
import pandas as pd

from datetime import datetime

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
    print(df.head())
    print(df.shape)

    #assign values...
    idd = df['id'].values
    utc = df['utc_dt'].values
    lat = df['lat'].values
    lon = df['lon'].values
    alt = df['alt'].values
    sat = df['sat'].values
except:
    print('Exception: #convert [DMS] to [DD]')
    pass

#find dates in utc_dt
df['day'] = df['utc_dt'].dt.to_period(freq='D')
day_list  = df['day'].dt.strftime('%Y-%m-%d').unique()
print('day_list {} {}'.format(len(day_list), day_list))

sat_list   = df.groupby('day')['sat'].count().tolist()
print('sat_list {} {}'.format(len(sat_list), sat_list))

#using groupby...
df_min = df.groupby('day').min()
df_max = df.groupby('day').max()
print('df_min', df_min.shape)
print('df_max', df_max.shape)
#print(df_min)
#print(df_max)

dt_stop = datetime.now()
print(dt_stop, 'file processing complete...')
dt_diff = dt_stop - dt_start
print('Time taken {}'.format(dt_diff))

#stop_further_execution_by_generating_error

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#fig = plt.figure(figsize=(20,10))
fig = plt.figure()
fig.suptitle('Neo-6m GPS - Uptime data')

# make a little extra space between the subplots
plt.subplots_adjust(wspace=0.25)

#Top Half Plot
#Scatter >> X-utc_dt >> Y-alt
plt.subplot(3, 1, 1)

#Grid
plt.minorticks_on()
plt.grid(b=True, which='major', color='k', linestyle=':', linewidth=0.5, alpha=0.25)
plt.grid(b=True, which='minor', color='gray', linestyle=':', linewidth=0.5, alpha=0.2)

try:
    #Plot
    #plt.plot(utc, alt, c='r', ls='-', lw=1, alpha=0.5)
    plt.plot(utc, alt, c='r', label='altitude', marker='o', ms=1, ls='-', lw=1, alpha=0.5)   
    #plot = plt.scatter(lon, lat, c=sat, cmap='hsv', marker='s', s=10, edgecolor='none', alpha=1)
    #plot = plt.scatter(utc, alt, c=alt, cmap='hsv', marker='s', s=10, edgecolor='none', alpha=1)
    #plt.colorbar(plot, label='Altitude')
    #plt.gcf().autofmt_xdate() #beautify the x-labels
except:
    print('Exception: #Top Half Plot')
    pass
'''
try:
    #beautify the x-labels
    #plt.gcf().autofmt_xdate()
    #plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    
    # Set minor ticks with hour numbers
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=3))
    plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%H'))
    
    # Set major ticks with day names
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('\n%Y-%m-%d %H:%M'))
    
except:
    print('Exception: #beautify the x-labels')
    pass
'''
try:
    #Details
    #plt.xlabel('DateTime UTC')
    plt.ylabel('Altitude in meter')
    plt.legend(loc=1)#'best')#Shows label, Best Location
    #plt.title('Neo-6m GPS - Altitude in meter')
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
    #Plot
    #plt.plot(utc, sat, c='g', ls='-', lw=1, alpha=0.5)
    plt.plot(utc, sat, c='g', label='satellites', marker='o', ms=1, ls='-', lw=1, alpha=0.5)
    #plot = plt.scatter(utc, sat, c=sat, cmap='hsv', marker='s', s=10, edgecolor='none', alpha=1)
    #plt.colorbar(plot, label='Satellites')
    #plt.gcf().autofmt_xdate() #beautify the x-labels
except:
    print('Exception: #Mid Half Plot')
    pass
try:
    #Details
    #plt.xlabel('DateTime UTC')
    plt.ylabel('No. of Satellites')
    plt.legend(loc=1)#'best')#Shows label, Best Location
    #plt.title('Neo-6m GPS - No. of Satellites')
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
'''
try:
    #Plot scatter
    plot = plt.scatter(utc, sat, c=sat, cmap='hsv', marker='s', s=10, edgecolor='none', alpha=1)
    plt.colorbar(plot, label='Satellites')
    #plt.xticks(np.arange(min(utc), max(utc), 1)) #Force Ticks Increment Value
    plt.gcf().autofmt_xdate() #beautify the x-labels
except:
    print('Exception: #Bottom Half Plot')
    pass
'''
''
try:
    ''
    #Plot bar
    #total seconds per day...
    dsec_list = [24*60*60] * len(day_list)
    #print('dsec_list {} {}'.format(len(dsec_list), dsec_list))
    plt.bar(day_list, dsec_list, label='', color='g', align='center', width=0.2, alpha=0.2)
    
    #Plot bar
    width = 0.2
    x_pos = np.arange(len(day_list))
    y_pos = np.arange(len(sat_list))
    plt.bar(x_pos, sat_list, label='records', color='g', align='center', width=width, alpha=0.5)
    plt.xticks(x_pos, day_list)
    for i, h in enumerate(sat_list):
        plt.text((x_pos[i]), h, '{}'.format(h), color='k', ha='center', va='bottom')
    ''
    #dt.to_period('Y') --> 2019, dt.to_period('M') --> 2019-08, dt.to_period('D') --> 2019-08-24
    #df['year']  = pd.to_datetime(df['utc_dt']).dt.to_period('Y')
    #df['month'] = pd.to_datetime(df['utc_dt']).dt.to_period('M')
    #df['day']   = pd.to_datetime(df['utc_dt']).dt.to_period('D')
    
    #dt.year --> 2019, dt.month --> 8, dt.day --> 24
    #df['year']   = df['utc_dt'].dt.year
    #df['month']  = df['utc_dt'].dt.month
    #df['day']    = df['utc_dt'].dt.day
    '''
    #Create a column containing day, count instances per day...
    df['day'] = df['utc_dt'].dt.to_period('D')
    gp_day    = df.groupby('day')['sat'].count()
    print(gp_day)
    gp_sorted = df['day'].sort_values()
    start_day = gp_sorted.iloc[0]
    end_day   = gp_sorted.iloc[-1]
    #gp_day   = gp_day.reindex(pd.period_range(start=start_day, periods=7))
    gp_day    = gp_day.reindex(pd.period_range(start=start_day, end=end_day))
    gp_day.index.name = 'day'
    gp_day.plot.bar(width=0.2)
    '''
    '''
    # Create a column containing month, count instances per month...
    df['month'] = df['utc_dt'].dt.to_period('M')
    gp_month    = df.groupby('month')['sat'].count()
    print(gp_month)
    gp_sorted   = df['month'].sort_values()
    start_month = gp_sorted.iloc[0]
    end_month   = gp_sorted.iloc[-1]
    gp_month    = gp_month.reindex(pd.period_range(start=start_month, periods=12))
    #gp_month   = gp_month.reindex(pd.period_range(start=start_month, end=end_month))
    gp_month.index.name = 'month'
    gp_month.plot.bar(width=0.2)
    '''
    #plt.gcf().autofmt_xdate() #beautify the x-labels
    #df.groupby('sat')['alt'].mean().sort_values().tail(20).plot(kind='bar')
    #df['sat'].value_counts().plot(kind='bar')
except:
    print('Exception: #Bottom Half Plot')
    pass
''
try:
    #Details
    plt.xlabel('DateTime UTC')
    plt.ylabel('No. of Records')
    plt.legend(loc=1)#'best')#Shows label, Best Location
    #plt.title('Neo-6m GPS - No. of Records')
except:
    print('Exception: #Title #Bottom Half Plot')
    pass

dt_stop = datetime.now()
print(dt_stop, 'all tasks complete...')
dt_diff = dt_stop - dt_start
print('Time taken {}'.format(dt_diff))

fig.canvas.set_window_title('Neo-6m GPS')
mng = plt.get_current_fig_manager()
mng.window.state('zoomed')
plt.show()
