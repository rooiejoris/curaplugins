#Name: KevlarWindings
#Info: Make extra gcode, the I for the amount of kevlar around the filament
#Depend: GCode
#Type: postprocess
#Param: windingratio(float:4) mm of kevlar per mm filament(mm)

# SPECIAL THANKS TO: 

# see my projects on:
# www.rooiejoris.nl
# www.facebook.com/europerminutedesign
# www.thingiverse.com/joris
# www.youmagine.com/joris


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
 print "Usage: WARNING!! NOT ADJUSTED FOR THE LATEST CODE SO IT WILL NOT RUN FROM COMMAND LINE"
 print "  "+myName+" -d difference -x centerx -y centery -w waves -l layerheight -n fromlayer -f gcodeFile"
 print "Licensed under CC-BY-NC from Jeremie.Francois@gmail.com (betterprinter.blogspot.com)"
 sys.exit()

try:
 filename
except NameError:
 # Then we are called from the command line (not from cura)
 # trying len(inspect.stack()) > 2 would be less secure btw
 opts, extraparams = getopt.getopt(sys.argv[1:],'w:f',['windingratio=','file=']) 
 windingratio = 10
 filename="test.gcode"

 for o,p in opts:
  if o in ['-w','--windingratio']:
   windings = float(p)
  elif o in ['-f','--file']:
   filename = p
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

x = 0
y = 0
z = None
e = None
i = None


with open(filename, "w") as f:
       i = 0
       for line in lines:
               #layer = getValue(line, ';LAYER:', None)

               if (getValue(line, 'G', None) == 1 or getValue(line, 'G', None) == 0): #only do something with G1 and G0 commands
                       x = getValue(line, "X", x)
                       y = getValue(line, "Y", y)
                       z = getValue(line, "Z", z)
                       v = getValue(line, "F", None)
                       e = getValue(line, 'E', e)
#                       i = e * windings


                       f.write("G1 ")
                       f.write("X%0.4f " %(x))
                       f.write("Y%0.4f " %(y))
                       f.write("Z%0.4f " %(z))
                       if e:
                       	 f.write("E%0.4f " %(e))
                         i = e * windingratio
                         f.write("I%0.4f " %(i))
                       if v: f.write("F%0.1f " %(v))
#                       f.write("; oldZ%0.4f " %(z))
                       f.write("\n")

               else: f.write(line)
