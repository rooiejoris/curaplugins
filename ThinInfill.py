#Name: ThinInfill
#Info: make different thickness than the outerwall!
#Depend: GCode
#Type: postprocess
#Param: flow(float:50) flow for infill

# SPECIAL THANKS TO: jeremie [http://betterprinter.blogspot.fr/2013/02/how-tun-run-python-cura-plugin-without.html]

# see my projects on:
# www.rooiejoris.nl
# www.facebook.com/europerminutedesign
# www.thingiverse.com/joris


import re, math

############ BEGIN CURA PLUGIN STAND-ALONIFICATION ############
# This part is an "adapter" to Daid's version of my original Cura/Skeinforge plugin that
# he upgraded to the lastest & simpler Cura plugin system. It enables commmand-line
# postprocessing of a gcode file, so as to insert the temperature commands at each layer.
#
# Also it is still viewed by Cura as a regular and valid plugin!
#
# To run it you need Python, then simply run it like
#   wood_standalone.py --min minTemp --max maxTemp --grain grainSize --file gcodeFile
# It will "patch" your gcode file with the appropriate M104 temperature change.
#
import inspect
import sys
import getopt
import math

def plugin_standalone_usage(myName):
 print "Usage:"
 print "  "+myName+" --flow flow --file gcodeFile"
 print "  "+myName+" -e flow  -f gcodeFile"
 print "Licensed under CC-BY-NC from Jeremie.Francois@gmail.com (betterprinter.blogspot.com)"
 sys.exit()

try:
 filename
except NameError:
 # Then we are called from the command line (not from cura)
 # trying len(inspect.stack()) > 2 would be less secure btw
 opts, extraparams = getopt.getopt(sys.argv[1:],'e:f',['flow=','file=']) 
 flow = 70
 filename="test.g"

 for o,p in opts:
  if o in ['-f','--flow']:
   flow = float(p)
  elif o in ['-f','--file']:
   filename = p
#   filename = 'test.g'
 if not filename:
  plugin_standalone_usage(inspect.stack()[0][1])
#  plugin_standalone_usage('test.g')
#
############ END CURA PLUGIN STAND-ALONIFICATION ############




def getValue(line, key, default = None):
       if not key in line or (';' in line and line.find(key) > line.find(';')):
               return default
       subPart = line[line.find(key) + 1:]
       m = re.search('^[0-9]+\.?[0-9]*', subPart)
       if m == None:
               return default
       try:
               return float(m.group(0))
       except:
               return default

               
with open(filename, "r") as f:
	lines = f.readlines()

z = 0
x = 0
y = 0
startEffect = 0

               
with open(filename, "w") as f:
       for line in lines:
               #layer = getValue(line, ';LAYER:', None)
               if ";TYPE:FILL" in line:
                       f.write(";TYPE:FILL\n;thininfill setting\nM221 S%f\n" % float(flow))
               if ";TYPE:WALL-OUTER" in line:
                       f.write(";TYPE:WALL-OUTER\n;thininfill setting reset\nM221 S100")
                       
               f.write(line)
               
