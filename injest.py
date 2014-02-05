import re


def loadschema(filename):
  types = {}

  read_values = False

  entry = re.compile(r"^\s+(?P<name>\w+)\s+(?P<start>\d+)-(?P<end>\d+)")

  with open(filename) as records:
    for line in records:
      if 'record type' in line:
        rtype        = line.split('"')[1]
        types[rtype] = {}
        current     = types[rtype]
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
          # if we can't parse, print something.
          print line + " . " + str(fields.groups())
      else:
        #we are not interested in other lines
        continue
    # the file gets closed automatically when we
    # leave the with block.
  return types


print loadschema('us1850a_records.txt')
