
class Entity(object):
  # using slots helps reduce
  # per object memory use
  __slots__ = ['record', 'schema']
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
  __slots__ = ['people']
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


class Households(object):
  __slots__ = ['households','orphans','incomplete']
  
  def __init__(self):
    self.households = {}
    self.orphans    = []
    self.incomplete = {}
  
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
      self.orphans.append(person)
    else:
      self.households[hhkey].add_person(person)

  def move_to_incomplete(self,key):
    self.incomplete[key] = self.households[key]
    self.delete(key)

  @property
  def num_incomplete(self):
    return len(self.incomplete)

  @property 
  def num_orphans(self):
    return len(self.orphans)
  
  def delete(self, key):
    del self.households[key]

