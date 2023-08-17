#Serial Neo 6m GPS direct
'''
# Serial_Neo6mGPS_direct.py
# created by mahemys; 2019.08.28
# !perfect, but works!
# GNU-GPL; no license; free to use!
# update 2019-08-28; initial review
#
#------------------------------------------------------------
# purpose
# neo-6m gps module data collection using serial port of the device and plotting relevant graphs using matplotlib
# 
#------------------------------------------------------------
# how to use
# just copy file to your location
# run this python script in terminal
# create a routine to run at start
#
#------------------------------------------------------------
# requirements
# sqlite3 for database
# serial for serial port communication
# matplotlib for graphs
# 
#------------------------------------------------------------
# process
# using serial port communication save gps data into the database
# 
#------------------------------------------------------------
# NMEA sentences
# GGA - essential fix data which provide 3D location and accuracy data.
# $GPGGA,timestamp,lat,lat_dir,lon,lon_dir,gps_qual,num_sat,horizontal_dil,altitude,altitude_units,geo_sep,geo_sep_units,empty,checksum
# $GPGGA,071341.00,1255.37234,N,07729.09966,E,1,06,1.49,811.0,M,-86.4,M,,*70
#------------------------------------------------------------
'''
import os
import sys
import serial
import sqlite3
from datetime import datetime

try:
    port           = "/dev/ttyS0"
    sqlite_db_name = 'neo6mgps_db.db'
    sqlite_db_dir  = os.path.dirname(__file__)
    sqlite_db      = os.path.join(sqlite_db_dir, sqlite_db_name)
    text_filename  = 'neo6mgps_log.txt'
    text_neo6mgps  = os.path.join(sqlite_db_dir, text_filename)
    #text_file      = open(text_neo6mgps, "w+")
except:
    print('Exception:', sqlite_db_name)
    with open(text_neo6mgps, "a") as text_file:
        text_file.write(str(datetime.now()) + '\t' + 'Exception: %s' %(sqlite_db_name) + '\n')
    pass

def parseGPS(data):
    try:
        #print("raw:", data)
        if data[0:6] == "$GPGGA":
            s = data.split(",")
            if s[7] is not None and s[7]== '0':
                print("no satellite data available")
                with open(text_neo6mgps, "a") as text_file:
                    text_file.write(str(datetime.now()) + '\t' + 'no satellite data available' + '\n')
                return
            if data.find('GGA') > 0:
                date   = str(datetime.utcnow().date())
                time   = s[1][0:2] + ":" + s[1][2:4] + ":" + s[1][4:6]
                #utc_dt = date + "T" + time + ".000Z"
                utc_dt = date + " " + time
                lat    = decode(s[2])
                dirLat = s[3]
                lon    = decode(s[4])
                dirLon = s[5]
                alt    = s[9]
                altUni = "m"
                sat    = s[7]
                #Time(UTC): 2019-08-24 10:49:29 -- Lat: 012 55 22.3602 N -- Lon: 077 29 06.0654 E -- Alt: 811.8 m -- Sat: 07
                print("Time(UTC): %s -- Lat: %s %s -- Lon: %s %s -- Alt: %s %s -- Sat: %s"\
                      %(utc_dt, lat, dirLat, lon, dirLon, alt, altUni, sat))
                if lat is not None:
                    insertVaribleIntoTable(utc_dt, lat, dirLat, lon, dirLon, alt, altUni, sat)
    except:
        print('Exception: parseGPS')
        with open(text_neo6mgps, "a") as text_file:
            text_file.write(str(datetime.now()) + '\t' + 'Exception: parseGPS' + '\n')
        pass

def insertVaribleIntoTable(utc_dt, lat, dirLat, lon, dirLon, alt, altUni, sat):
    try:
        #data --> tuple
        data_tuple = (utc_dt, lat, dirLat, lon, dirLon, alt, altUni, sat)
        
        #Connection, new db file will be created if does not exist
        sqlite_connec = sqlite3.connect(sqlite_db)
        sqlite_cursor = sqlite_connec.cursor()
        #print("sqlite --> successfully connected")

        #Create table, if table does not exist
        sqlite_create_query = """CREATE TABLE if not exists neo6mgps (id integer primary key AUTOINCREMENT,
                                utc_dt text, lat text, dirLat text, lon text, dirLon text, alt real, altUni text, sat integer)"""
        #Create table, execute
        sqlite_cursor.execute(sqlite_create_query)
        
        #Query, data with param
        sqlite_insert_query = """INSERT INTO 'neo6mgps' ('utc_dt', 'lat', 'dirLat', 'lon', 'dirLon', 'alt', 'altUni', 'sat') VALUES (?, ?, ?, ?, ?, ?, ?, ?);"""
        
        #Insert, insert row, execute tuple
        sqlite_cursor.execute(sqlite_insert_query, data_tuple)
        sqlite_connec.commit()
        #print("sqlite --> successfully inserted into table")
        
        sqlite_cursor.close()
        
    except sqlite3.Error as error:
        print("sqlite --> failed to insert into table", error)
        with open(text_neo6mgps, "a") as text_file:
            text_file.write(str(datetime.now()) + '\t' + 'sqlite --> failed to insert into table' + '\n')
    finally:
        if (sqlite_connec):
            #close the connection
            sqlite_connec.close()
            #print("sqlite --> connection closed")
            
def decode(coordinates):
    # Degrees, minutes, and seconds (DMS)
    # Degrees and decimal minutes (DMM)
    # Decimal degrees (DD)
    # Latitude  : max/min + 90 to - 90
    # Longitude : max/min +180 to -180
    # Lat  : 012 55 22.3602 N
    # Lon  : 077 29 06.0654 E
    # N, E : Positive
    # S, W : Negative
    # DDMM.MMMMM  -> DD deg MM.MMMMM min
    #   MM.MMMMM  -> MM min   .MMMMM sec
    if "." in coordinates:
        latlon = coordinates.split(".")
        head   = latlon[0]  #DDMM
        tail   = latlon[1]  #.MMMMM
        degree = head[0:-2] #DD
        minute = head[-2:]  #MM
        sec_tl = float('0.' + tail) * 60      #.MMMMM to sec
        degree = '{:03d}'.format(int(degree)) #DD  000
        minute = '{:02d}'.format(int(minute)) #MM  00
        second = '{:07.4f}'.format(sec_tl)    #sec 00.0000
        return degree + " " + minute + " " + second

def check_main():
    pid = os.getpid()
    if os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno()):
        print('Running in foreground... pid = %s' %(str(pid)))
        with open(text_neo6mgps, "a") as text_file:
            text_file.write(str(datetime.now()) + '\t' + 'Running in foreground... pid = %s' %(str(pid)) + '\n')
    else:
        print('Running in background... pid = %s' %(str(pid)))
        with open(text_neo6mgps, "a") as text_file:
            text_file.write(str(datetime.now()) + '\t' + 'Running in background... pid = %s' %(str(pid)) + '\n')
        
if __name__ == "__main__":
    try:
        check_main()
        print("Started... %s" %(__file__))
        ser = serial.Serial(port, baudrate = 9600, timeout = 0.5)
        print("Serial port... %s" %(port))
        with open(text_neo6mgps, "a") as text_file:
            text_file.write(str(datetime.now()) + '\t' + 'port selected %s' %(port) + '\n')
        while True:
            data = ser.readline()
            parseGPS(data)
    except KeyboardInterrupt:
        ser.close()
        print("Keyboard Interrupt...")
        with open(text_neo6mgps, "a") as text_file:
            text_file.write(str(datetime.now()) + '\t' + 'ser close, Keyboard Interrupt...' + '\n')
        #text_file.close()
        pass
