import re
import tables
import sys
from util import *

# a spinner for showing progress on
# long term tasks.


# a function to load schemas from *_records.txt files
    
def load_schema(filename):
  schemas = {}

  read_values = False

  entry = re.compile(r"^\s+(?P<name>\w+)\s+(?P<start>\d+)-(?P<end>\d+)")

  try:
    with open(filename) as records:
      for line in records:
        if 'record type' in line:
          rtype        = line.split('"')[1]
          schemas[rtype] = {}
          current     = schemas[rtype]
        elif 'data list' in line:
          read_values = True
        elif '.' in line:
          read_values = False
        elif read_values:
          fields = entry.search(line)
          try:
            current[fields.group('name')] = [int(fields.group('start'))-1,
                                             int(fields.group('end')) ]
          except:
            # if we can't parse, print something.
            print line + " . " + str(fields.groups())
        else:
          #we are not interested in other lines
          continue
  except IOError:
    print "Error: (load_schema) could not open file: " + filename
    exit()

    # the file gets closed automatically when we
    # leave the with block.
  return schemas




def load_households(table_data, schemas):
  households = {}
  orphans    = []
  household_schema = schemas['H']
  person_schema    = schemas['P']
  try:
    with open(table_data['H']['file']) as records:
      meter = spinner("Reading Household Data", 20)
      for record in records:
        meter.spin()
        key = get_value('SERIAL',
                        household_schema,
                        record)
        if key in households:
          print "duplicate household%s" % key
        else:
          households[key] = { 'record':record,
                              'people':[] }
      meter.done() 
  except IOError:
    print "Error: (load_households) could not open file: " + table_data['H']['file']
    exit()
  try:
    with open(table_data['P']['file']) as records:
      meter = spinner("Reading Person Data",20)
      for record in records:
        meter.spin()
        household = get_value('SERIALP',
                              person_schema,
                              record)
        if household not in households:
          pernum  = get_value('PERNUM',
                              person_schema,
                              record)
          orphans.append(record)
        else:
          households[household]['people'].append(record)
      meter.done()
  except IOError:
    print "Error: (load_households) could not open file: " + table_data['H']['file']
    exit()
    meter.done() 
  return households,orphans
        
def remove_incomplete(households,schema):
  removals = []
  incomplete = {}
  
  meter = spinner("Removing Incomplete Households", 20)

  for key in households:
    meter.spin()
    household = households[key]
    numpeople = int(get_value('NUMPREC',
                              schema,
                              household['record']))
    if numpeople != len(household['people']):
      removals.append(key)

  for key in removals:
    meter.spin()
    incomplete[key] = households[key]
    households.pop(key,None)
  meter.done()
  
  return incomplete
  
def write_households(households):
  with open('merged.txt','w') as records:
    meter = spinner("Writing Merged Data", 20)
    for key in households:
      meter.spin()
      household = households[key]
      records.write(household['record'])
      for person in household['people']:
        records.write(person)
    meter.done()


def write_errors(orphans, incomplete, schemas):
  with open('errors.txt','w') as records:
    person_schema = schemas['P']
    meter = spinner("Writing Errors", 20)
    counter = 0 

    records.write("%d Incomplete Households:\n" % len(incomplete))
    for key in incomplete:
      meter.spin()
      if counter % 7 == 0:
        records.write("\n")
      counter += 1
      records.write("%s " % key)
    
    records.write("\n\n%d Orphaned People:\n" % len(incomplete))
      
    for orphan in orphans:
      meter.spin()

      if counter % 10 == 0:
        records.write("\n")
      
      # Hmmm, the doc lists some values to get from
      # the Household record for uniquely identifying
      # People, but these people don't have a household
      # record, because they're orphans, so...
      #
      # I'm going to throw a hail mary, and include the
      # household id, so if the household record is found,
      # there's no problem and if it isn't I will include
      # a few facts about the person...

      age       = get_value('AGE',
                            person_schema,
                            orphan)
      sex       = get_value('SEX',
                            person_schema,
                            orphan)
      dob       = get_value('BIRTHYR',
                            person_schema,
                            orphan)
      first     = get_value('NAMEFRST',
                            person_schema,
                            orphan)
      last      = get_value('NAMELAST',
                            person_schema,
                            orphan)
               
      household = get_value('SERIALP',
                            person_schema,
                            orphan)

      records.write("%s %s %s %s %s %s\n" % (household,first,last,sex,age,dob))
    
    meter.done()



