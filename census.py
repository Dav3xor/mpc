from files  import *
from stats  import *
from util   import *
from pprint import pprint

# first define some data for handling files:

table_data = { 'H': { 'file':        'us1850a_households.dat',
                      'name':        'households',
                      'key':         'SERIAL',
                      'description': '1850 Census Households'},
               'P': { 'file':        'us1850a_people.dat',
                      'name':        'people',
                      'key':         'PERNUM',
                      'description': '1850 Census Households'} }

database_info = { 'name': 'census1850', 
                  'description': '1850 Census',
                  'filename': 'census.h5' }



# load the data schemas from the records file.
schemas = load_schema('us1850a_records.txt')


households, orphans = load_households(table_data, schemas)
incomplete = remove_incomplete(households,schemas['H'])

write_households(households)
write_errors(orphans, incomplete, schemas)

dostats(households,schemas)

