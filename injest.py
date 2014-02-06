import re
import tables

def load_schema(filename):
  schemas = {}

  read_values = False

  entry = re.compile(r"^\s+(?P<name>\w+)\s+(?P<start>\d+)-(?P<end>\d+)")

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
    # the file gets closed automatically when we
    # leave the with block.
  return schemas


table_data = { 'H': { 'file': 'us1850a_households.dat',
                      'name': 'households',
                      'description': '1850 Census Households'},
               'P': { 'file': 'us1850a_people.dat',
                      'name': 'people',
                      'description': '1850 Census Households'} }


def build_table(database, group, info, schema):
  class table_desc(tables.IsDescription):
    pass
  
  for column in schema:
    start = schema[column][0]
    end   = schema[column][1]
    table_desc.columns[column] = tables.StringCol(end-start)
  
  table = database.create_table(group, info['name'], 
                                table_desc, info['description'])
  row = table.row 
  with open(info['file']) as records:
    for record in records:
      for column in schema:
        start = schema[column][0]
        end   = schema[column][1]
        row[column] = record[start:end].strip()
      row.append()
      break 

def build_tables(filename, table_data, schemas):
  database = tables.open_file(filename, mode='w')
  group = database.create_group("/","census","Census Data")

  for table in table_data:
    build_table(database, group, table_data[table], schemas[table])

  database.close()

schemas = load_schema('us1850a_records.txt')

build_tables('census.h5', table_data, schemas)
