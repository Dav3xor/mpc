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



# function to handle reading from files, what happen
# if the file doesn't exist, etc...

def read_with_spinner(filename, msg, visitor_function):
  try:
    with open(filename) as records:
      meter = spinner(msg, 20)
      for record in records:
        meter.spin()
        visitor_function(record)
      meter.done() 
  except IOError:
    print "Error: (load_households) could not open file: " + filename
    exit()
