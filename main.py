#Written By: William Gribbin in association with Gillian Garbus, Kyle Hollander, Addison Armstrong, Theresta Desir, and Tyler Allern
#The purpose of this program is generate data files showing the shortest drive times between schools in florida counties

#the extra extensions imported to make this program funciton
import sys
import time
import csv
from math import sin, cos, sqrt, atan2
from operator import itemgetter
from googlemaps.client import Client
from googlemaps.distance_matrix import distance_matrix


#helps give how long the program runs after execution
start_time = time.time()
apiusecounter = 0

#A callable function that gives the distance between two geocodes
def disCalc(latty1,longi1 , latty2, longi2):
   # approximate radius of earth in km
   R = 6373.0

   # 'converts the str into INT because thats how python grabs data from a csv
   lat1 = float(latty1)
   lon1 = float(longi1)
   lat2 = float(latty2)
   lon2 = float(longi2)

   # 'The math that calculates the distance between 2 geopoints on the curve of the earth
   dlon = lon2 - lon1
   dlat = lat2 - lat1
   a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
   c = 2 * atan2(sqrt(a), sqrt(1 - a))

   distance = R * c

   return distance


#A callable function that compares two counties schools and limits it down to one school dependent on discalc
#and gmapcalc
def CSVGenerator(county1, county2, schoolLevel, timer, outfile):
   schoolLevelCSV = schoolLevel + '.csv'

#brings in the first county data collected from user and moves it to county1.csv to allow easier use
   with open(schoolLevelCSV, 'r') as csv_file:
       csv_reader = csv.DictReader(csv_file)
       with open('county1.csv', 'w') as new_file:
           fieldnames = ['Driver','SchoolNum','SchoolName','Street','County','State','Zip','Type','Lat','Lon']
           csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames)
           csv_writer.writeheader()
           for line in csv_reader:
               if line['Driver'] == county1:
                   csv_writer.writerow(line)

# 'brings the second county data collected from the user and moves it to county2.csv
# 'this allows easier use for testing and checking when the data is imported because it is saved
   with open(schoolLevelCSV, 'r') as csv_file:
       csv_reader = csv.DictReader(csv_file)
       with open('county2.csv', 'w') as new_file:
           fieldnames = ['Driver','SchoolNum','SchoolName','Street','County','State','Zip','Type','Lat','Lon']
           csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames)
           csv_writer.writeheader()
           for line in csv_reader:
               if line['Driver'] == county2:
                   csv_writer.writerow(line)

# 'Generates 2 Lists from my saved CSV data
   list1 = []
   list2 = []
   with open('county1.csv', 'r') as readfile:
       csvread = csv.reader(readfile)
       with open('county2.csv', 'r') as readfile2:
           csvread2 = csv.reader(readfile2)
           for row in csvread:
               list1.append(row)
           for row2 in csvread2:
               list2.append(row2)



# 'fixes an issue with extra [] in my lists from strait ripping the csv and removes headers
   list1clean = [x for x in list1 if x != []]

   #Imports the county 2 data into its own section
   lst1name = [item[2] for item in list1clean]
   lst1name.pop(0)
   lst1lat = [item[8] for item in list1clean]
   lst1lat.pop(0)
   lst1lon = [item[9] for item in list1clean]
   lst1lon.pop(0)

   #Imports The Address For GMAP County 1
   lst1street = [item[3] for item in list1clean]
   lst1street.pop(0)
   lst1city = [item[4] for item in list1clean]
   lst1city.pop(0)
   lst1state = [item[5] for item in list1clean]
   lst1state.pop(0)
   lst1zip = [item[6] for item in list1clean]
   lst1zip.pop(0)

   #Imports the county 2 data into its own section
   list2clean = [x for x in list2 if x != []]
   lst2name = [item[2] for item in list2clean]
   lst2name.pop(0)
   lst2lat = [item[8] for item in list2clean]
   lst2lat.pop(0)
   lst2lon = [item[9] for item in list2clean]
   lst2lon.pop(0)

   # Imports The Address For GMAP County 2
   lst2street = [item[3] for item in list2clean]
   lst2street.pop(0)
   lst2city = [item[4] for item in list2clean]
   lst2city.pop(0)
   lst2state = [item[5] for item in list2clean]
   lst2state.pop(0)
   lst2zip = [item[6] for item in list2clean]
   lst2zip.pop(0)

   i = 0
   x = 0
   AnaList = []
   while i < len(lst1name):

       while x < len(lst2name):
           address1 = lst1lat[i] + ',' + lst1lon[i]
           address2 = lst2lat[x] + ',' + lst2lon[x]
           disty = (disCalc(lst1lat[i], lst1lon[i], lst2lat[x], lst2lon[x]))
           AnaList.append([lst1name[i], lst2name[x], disty, address1, address2])
           x = x + 1
       x = 0
       i = i + 1

   sortlist = sorted(AnaList, key=itemgetter(2))
   bestresult=sortlist[0]
   bestresult.append(county1)
   bestresult.append(county2)

   #gets the starting and ending address for gmap drive times
   startaddress = bestresult[3]
   endaddress = bestresult[4]
   #removes the spaces from the drive time for url ease of use
   startaddressmod = startaddress.replace(" ", "%")
   endaddressmod = endaddress.replace(" ", "%")

   #adds the drive time from google maps drive time api
   bestresult.append(gmapcalc(startaddressmod, endaddressmod, apiusecounter))
   print(bestresult)
   print(bestresult)

   #writes to csv
   if timer == 0:
       with open(outfile, 'w') as new_file:
           # configure writer to write standard csv file
           writer = csv.writer(new_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
           # Creates the header for the csv
           writer.writerow(['School1', 'School2', 'DistanceApart', 'School1Lat', 'School1Lon', 'School2Lat', 'School2Lon', 'County1', 'County2', 'DriveTime'])
           writer.writerow(bestresult)
   else:
       with open(outfile, 'a') as new_file:
           # configure writer to write standard csv file
           writer = csv.writer(new_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
           writer.writerow(bestresult)


#a callable function that returns the drive location of 2 gps coordinates
def gmapcalc(location1, location2, apiuse):
   api_key = 'AIzaSyAn6U1F6NJIJx226L8sK5my_ECvHm7k18o'
   gmaps = Client(api_key)
   data = distance_matrix(gmaps, location1, location2)
   timeaway = data['rows'][0]['elements'][0]['duration']['text']
   global apiusecounter
   apiusecounter += 1
   return(timeaway)


#gives the formatting for running each schooling level in its own function
def Elementary():
   ElemList = open('DRIVERELEMENTARY.csv').read().splitlines()
   i = 0
   x = 0
   timer = 0
   while i < len(ElemList):
       while x < len(ElemList):
           Elist1 = ElemList[i]
           Elist2 = str(ElemList[x])
           if Elist1 != Elist2:
               CSVGenerator(Elist1, Elist2, 'ELEMENTARY', timer, 'elementaryout.csv')
               timer = timer + 1
           x = x + 1

       x = 0
       i = i + 1
def Middle():
   MiddleList = open('DRIVERMIDDLE.csv').read().splitlines()
   i = 0
   x = 0
   timer = 0
   while i < len(MiddleList):
       while x < len(MiddleList):
           Elist1 = MiddleList[i]
           Elist2 = str(MiddleList[x])
           if Elist1 != Elist2:
               CSVGenerator(Elist1, Elist2, 'MIDDLE', timer, 'middleout.csv')
               timer = timer + 1
           x = x + 1

       x = 0
       i = i + 1
def High():
   HighList = open('DRIVERHIGH.csv').read().splitlines()
   i = 0
   x = 0
   timer = 0
   while i < len(HighList):
       while x < len(HighList):
           Elist1 = HighList[i]
           Elist2 = str(HighList[x])
           if Elist1 != Elist2:
               CSVGenerator(Elist1, Elist2, 'HIGH', timer, 'highout.csv')
               timer = timer + 1
           x = x + 1

       x = 0
       i = i + 1


# '----------------------------------------------------------------
# Creates a final function that runs each grade level and notifies user of error
def final():
   try:
       Elementary()
       print('Elementary Completed!')
       print(apiusecounter)
   except: print('Elementary Scan Failed. Check That There are Matching Counties in your data have a matching driver county that matches the word EXACTLY', sys.exc_info()[0])

   try:
       Middle()
       print('Middle Completed!')
       print(apiusecounter)
   except: print('Middle Scan Failed. Check That There are Matching Counties in your data have a matching driver county that matches the word EXACTLY', sys.exc_info()[0])
   try:
       High()
       print('High Completed!')
       print(apiusecounter)
   except: print('High Scan Failed. Check That There are Matching Counties in your data have a matching driver county that matches the word EXACTLY', sys.exc_info()[0])


#------------------------------------------------------------------
#runs the final function
final()


#notifies you of how long it took to run this entire program
print("This Analysis Took ", ((time.time() - start_time)/ 60), "minutes to run")
#stops script file from autoclosing for 10 min.
time.sleep(1200)
