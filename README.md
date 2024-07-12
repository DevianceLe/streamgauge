Streamgauge is an application that parses water table data from weather.gov's new api. This outputs the information and content stored in a db to a readable output for the user end. 

This is a replacement from the older streamgauge system I retired due to ahps api no longer being available. 

This is alpha software at this time. Code changes will be taking place and this can cause your older db's to no longer work. You have been warned lol.


main.py will create a db file and store it in the default db folder
fetcher.py grabs the data and stores the weather codes in seperate db's to parse current and prior stream readings

