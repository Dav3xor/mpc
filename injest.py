import re

person_schema = {}
household_schema = {}
types = { 'H':household_schema, 
          'P':person_schema 
        }

read_values = False

entry = re.compile(r"^\s+(?P<name>\w+)\s+(?P<start>\d+)-(?P<end>\d+)")

with open('us1850a_records.txt') as records:
  for line in records:
    if 'record type' in line:
      current = types[line.split('"')[1]]
    elif 'data list' in line:
      read_values = True
    elif '.' in line:
      read_values = False
    elif read_values:
      fields = entry.search(line)
      try:
        current[fields.group('name')] = [int(fields.group('start')),
                                         int(fields.group('end')) ]
      except:
        print line + " . " + str(fields.groups())
#print person_schema
#print household_schema
