from injest import *

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

male_percent, female_percent = male_to_female(households,schemas['P'])
print "males: %s" % male_percent
print "females: %s" % female_percent
print len(households)
print len(orphans)
print len(incomplete)
