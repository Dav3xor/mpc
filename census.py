from files  import *
from stats  import *
from util   import *
from pprint import pprint

# first define some data for handling files:


database_info = { 'name': 'census1850', 
                  'description': '1850 Census',
                  'filename': 'census.h5' }



# load the data schemas from the records file.


households = load_households('us1850a_records.txt', 
                             'us1850a_households.dat',
                             'us1850a_people.dat')

remove_incomplete(households)

write_households(households)
write_errors(households)

#dostats(households)

