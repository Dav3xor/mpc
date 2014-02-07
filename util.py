import sys

# a little class to do a "please wait..." ascii spinner
class spinner():
  def __init__(self, message, rate):
    self.bars     = "/-\\|/-\\|"
    self.counter  = 1 
    self.rate     = rate

    sys.stdout.write("%-30s -- " % message)
    sys.stdout.write("|")
    sys.stdout.flush()
  
  # can't use a destructor here because it only triggers
  # when the garbage collector runs, and we care about
  # when this gets printed...
  def done(self):
    count = 0
    sys.stdout.write("\bDone\n")
    sys.stdout.flush()

  def spin(self):
    if self.counter % self.rate == 0:
      bar_index = (self.counter/8)%len(self.bars)
      sys.stdout.write("\b%s" % self.bars[bar_index])
      sys.stdout.flush()
    self.counter += 1

# simple helper function for getting a
# value from a record using a key
def get_value(key,schema,record):
  start = schema[key][0]
  end   = schema[key][1]
  return record[start:end]
