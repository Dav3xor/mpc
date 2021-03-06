from util import *
from codes import *
import operator

def dostats(households):
  meter = spinner("Writing stats.txt",1)
  with open('stats.txt', 'w') as stats:
    meter.spin()
  
    males,females = male_to_female(households)
    stats.write("Percentage Male:   %.1f\n" % males)
    stats.write("Percentage Female: %.1f\n\n" % females)
    meter.spin()

    household_sizes = household_size(households)
    stats.write("Average Household Size (by state):\n")
    for key in household_sizes:
      stats.write("%s: %.1f\n" % (reverse_states[key], household_sizes[key]))
    stats.write("\n")
    meter.spin()
    
    
    farms           = farm_households(households)
    stats.write("Percentage of Households That Are Farms (by state):\n")
    for key in farms:
      stats.write("%s: %.1f\n" % (reverse_states[key], farms[key]))
    stats.write("\n")
    meter.spin()

    male_names, female_names = common_names(households)
    stats.write("Most Common First Names:\n")
    
    stats.write("  Male:\n")
    for name in male_names:
      stats.write("    %s - %d\n" % (name[0],name[1]))
    
    stats.write("  Male:\n")
    for name in female_names:
      stats.write("    %s - %d\n" % (name[0],name[1]))
    stats.write("\n")
    meter.spin()
    
    areas           = metropolitan_areas(households)
    stats.write("Metropolitan Areas (estimated population):\n")
    for key in areas:
      area = areas[key]
      stats.write("%-30s:%d\n" % (area['name'],area['population']))
    stats.write("\n")
    meter.spin()

  meter.done()
 
def male_to_female(households):
  males   = 0
  females = 0
  total   = 0
  for household in households:
    for person in household.people:
      sex = person['SEX']
      if sex=="1":
        males   += 1
        total   += 1 
      if sex=="2":
        females += 1 
        total   += 1
  return (float(males)/float(total)*100.0, 
         float(females)/float(total)*100.0)

def household_size(households):
  states = {}
  for household in households:
    people = int(household['NUMPREC'])
    state  = int(household['STATEFIP'])
    if state not in states:
      states[state] = []
    states[state].append(people)
  for state in states:
    avg = float(sum(states[state]))/float(len(states[state]))
    states[state] = avg 
  return states

def farm_households(households):
  states = {}
  for household in households:
    farm   = int(household['FARM'])
    state  = int(household['STATEFIP'])
    if state not in states:
      states[state] = [0,0]
    states[state][0] += 1
    if farm == 2:
      states[state][1] += 1
    
  for state in states:
    percent = float(states[state][1])/float(states[state][0])*100.0
    states[state] = percent
  return states

def metropolitan_areas(households):
  areas = {7040:{'name': 'St. Louis', 'population':0},
           1120:{'name': 'Boston', 'population':0},
           6160:{'name': 'Philadelphia', 'population':0} }
  for household in households:
    metro = int(household['METRO'])
    area  = int(household['METAREA'])

    # if metro = 1, it's not actually in the metro area...
    if metro != 1 and area in areas:
      areas[area]['population'] += household.num_people()

  # expand from 1% to 100%...
  for area in areas:
    areas[area]['population'] *= 100 
  
  return areas

def common_names(households):
  male_names = {}
  female_names = {}
  for household in households:
    for person in household.people:
      name    = person['NAMEFRST']
      sex     = person['SEX']
      name = name.strip()
      if len(name):
        name = name.split()[0]  # some names include middle initial?

        if sex == "1":
          if name not in male_names:
            male_names[name] = 0
          male_names[name] += 1
        else:
          if name not in female_names:
            female_names[name] = 0
          female_names[name] += 1

  male_sorted   = sorted(male_names.iteritems(), key = operator.itemgetter(1))
  female_sorted = sorted(female_names.iteritems(), key = operator.itemgetter(1))
  male_sorted.reverse()
  female_sorted.reverse()
  return male_sorted[:5], female_sorted[:5]
