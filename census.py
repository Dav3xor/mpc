from files  import *
from stats  import *
from util   import *
from pprint import pprint

households = load_households('us1850a_records.txt', 
                             'us1850a_households.dat',
                             'us1850a_people.dat')

remove_incomplete(households)

write_households(households)
write_errors(households)

dostats(households)

