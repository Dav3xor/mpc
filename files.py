import re
import tables
import sys
from util import *
from censusobjects import *

# I like to keep all this file io stuff as separate functions 
# outside of the households/household/person classes.  Keeps
# the clutter out of the classes, and I'm not making a
# proliferation of support classes (FactoryFactory...)



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



def load_households(schemafile, householdsfile, peoplefile):
  schemas = load_schema(schemafile) 
  Household.set_schema(schemas['H'])
  Person.set_schema(schemas['P'])
  
  households = Households()

  # here's where we read the household and people files...
  read_with_spinner(householdsfile,
                    'Reading Household Data',
                    households.add_household)
  read_with_spinner(peoplefile,
                    'Reading Person Data',
                    households.add_person)
  return households
        
def remove_incomplete(households):
  removals = []
  
  meter = spinner("Removing Incomplete Households", 20)
  for household in households:
    meter.spin()
    numpeople = int(household['NUMPREC'])
    if numpeople != household.num_people():
      removals.append(household['SERIAL'])

  for key in removals:
    meter.spin()
    households.move_to_incomplete(key)
  meter.done()
  
def write_households(households):
  with open('merged.txt','w') as records:
    meter = spinner("Writing Merged Data", 20)
    for household in households:
      meter.spin()
      records.write(household.record)
      for person in household.people:
        records.write(person.record)
    meter.done()


def write_errors(households):
  with open('errors.txt','w') as records:
    meter = spinner("Writing Errors", 20)
    counter = 0 

    records.write("%d Incomplete Households:\n" % households.num_incomplete)
    for household in households.incomplete:
      meter.spin()
      if counter % 7 == 0:
        records.write("\n")
      counter += 1
      records.write("%s " % household)
    
    records.write("\n\n%d Orphaned People:\n" % households.num_orphans)
      
    for orphan in households.orphans:
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

      age       = orphan['AGE']
      sex       = orphan['SEX']
      dob       = orphan['BIRTHYR']
      first     = orphan['NAMEFRST']
      last      = orphan['NAMELAST']
               
      household = orphan['SERIALP']

      records.write("%s %s %s %s %s %s\n" % (household,first,last,sex,age,dob))
    
    meter.done()



