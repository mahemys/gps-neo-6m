# Neo 6m GPS Serial Direct

- neo6mgps_serial_direct.py
- created by mahemys; 2019.08.28
- !perfect, but works!
- GNU-GPL; no license; free to use!
- update 2019-08-28; initial review

**purpose**
- neo-6m gps module data collection using serial port of the device and plotting relevant graphs using matplotlib

**how to use**
- just copy file to your location
- run this python script in terminal
- create a routine to run at start

**requirements**
- sqlite3 for database
- serial for serial port communication
- matplotlib for graphs

**process**
- using serial port communication save gps data into the database
- first convert db to csv; neo6mgps_db.db -> neo6mgps.csv
- run `neo6mgps_plot_uptime.py` to generate **uptime graphs** like No of Satellites; No of Records
- run `neo6mgps_plot_blackouts.py` to generate **downtime or blackouts graphs** like Blackouts duration; Total No of Blackouts

**NMEA sentences**
- GGA - essential fix data which provide 3D location and accuracy data.
- $GPGGA,timestamp,lat,lat_dir,lon,lon_dir,gps_qual,num_sat,horizontal_dil,altitude,altitude_units,geo_sep,geo_sep_units,empty,checksum
- $GPGGA,071341.00,1255.37234,N,07729.09966,E,1,06,1.49,811.0,M,-86.4,M,,*70

**footnote**
- let me know if you find any bugs!
- Thank you mahemys
