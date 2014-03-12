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

class Entity(object):
  def __init__(self, record):
    self.record = record
  def __getitem__(self, key):
    start = self.schema[key][0]
    end   = self.schema[key][1]
    return  self.record[start:end]

class Person(Entity):
  schema = {}
  @staticmethod 
  def set_schema(newschema):
    Person.schema = newschema

class Household(Entity):
  schema = {}
  def __init__(self, record):
    super(Household, self).__init__(record)
    self.people = []
  @staticmethod 
  def set_schema(newschema):
    Household.schema = newschema

  def add_person(self,person):
      self.people.append(person)

  def num_people(self):
    return len(self.people)


class Households():
  def __init__(self):
    self.households = {}
    self.orphans    = []

  def __iter__(self):
    """ allows you to iterate over households contained in
        the class with a simple 
        
        >>> for household in households:
        ...   print household
    """
    for i in self.households:
      # i is the key, so we yield
      # the object instead, it's cleaner.
      yield self.households[i]

  def __getitem__(self, key):
    """ allows looking up a specific household by it's key --

        >>> households[key]['SERIAL']
        1
    """
    if self.households.has_key(key):
      return self.households[key]
    else:
      return None

  def add_household(self, record):
    household = Household(record)
    key = household['SERIAL']
    if key in self.households:
      print "duplicate household %s" % key
    else:
      self.households[key] = household
  def add_person(self, record):
    person = Person(record)
    hhkey = person['SERIALP']
    if hhkey not in self.households:
      print "-" + hhkey
      self.orphans.append(person)
    else:
      self.households[hhkey].add_person(person)

  def delete(self, key):
    del self.households[key]

def load_households(schemafile, householdsfile, peoplefile):
  schemas = load_schema(schemafile) 
  Household.set_schema(schemas['H'])
  Person.set_schema(schemas['P'])
  
  households = Households()
  try:
    with open(householdsfile) as records:
      meter = spinner("Reading Household Data", 20)
      for record in records:
        meter.spin()
        households.add_household(record)
      meter.done() 
  except IOError:
    print "Error: (load_households) could not open file: " + householdsfile
    exit()
  try:
    with open(peoplefile) as records:
      meter = spinner("Reading Person Data",20)
      for record in records:
        meter.spin()
        households.add_person(record)
      meter.done()
  except IOError:
    print "Error: (load_households) could not open file: " + peoplefile
    exit()
    meter.done() 
  return households
        
def remove_incomplete(households):
  removals = []
  incomplete = {}
  
  meter = spinner("Removing Incomplete Households", 20)
  for household in households:
    meter.spin()
    numpeople = int(household['NUMPREC'])
    if numpeople != household.num_people():
      removals.append(household['SERIAL'])
      #print str(numpeople) + "-" + str(household.num_people())
    else:
      pass
      #print str(numpeople) + "+" + str(household.num_people())

  for key in removals:
    meter.spin()
    incomplete[key] = households[key]
    households.delete(key)
  meter.done()
  households.incomplete = incomplete 
  
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

    records.write("%d Incomplete Households:\n" % len(households.incomplete))
    for household in households.incomplete:
      meter.spin()
      if counter % 7 == 0:
        records.write("\n")
      counter += 1
      records.write("%s " % household)
    
    records.write("\n\n%d Orphaned People:\n" % len(households.orphans))
      
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



