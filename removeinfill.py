#Name: Removeinfill
#Info: Removes the infill from the object!
#Depend: GCode
#Type: postprocess
#Param: fromLayer(float:4) Start effect from (layer nr)

# SPECIAL THANKS TO: Jelle, Hendrik and jeremie [http://betterprinter.blogspot.fr/2013/02/how-tun-run-python-cura-plugin-without.html]

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

def plugin_standalone_usage(myName):
 print "Usage:"
 print "  "+myName+" fromlayer -f gcodeFile"
 print "Standalone usage Licensed under CC-BY-NC from Jeremie.Francois@gmail.com (betterprinter.blogspot.com)"
 print "removeinfill script Licensed under CC-BY-NC from www.rooiejoris.nl"
 sys.exit()

try:
 filename
except NameError:
 # Then we are called from the command line (not from cura)
 # trying len(inspect.stack()) > 2 would be less secure btw
 opts, extraparams = getopt.getopt(sys.argv[1:],'n:f',['fromlayer=','file=']) 

 fromLayer = 5;
 filename="test.g"

 for o,p in opts:
  if o in ['-n','--fromlayer']:
   layerheight = float(p)
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
e = 0
v = 0
startEffect = 0
startFill = 0
layer = 0
#persistentZ = 0



with open(filename, "w") as f:
#       print("binnen")

       for line in lines:
#               print("binnen")
               if ";LAYER:" in line:
#                    print("binnen")
                    layer = line[7:]
#                    print(layer)

               if int(layer) > int(fromLayer):
                    startEffect = 1
#                    print("startEffect")

               if ";TYPE:FILL" in line:
                    startFill = 1
#                    print("fill detected")
#                    print(layer)

               if ";LAYER:" in line:
                    startFill = 0
#                    print("fill stop")

               if ";TYPE:" in line and not ";TYPE:FILL" in line:
                    startFill = 0
#                    print("fill stop")

               
               e = getValue(line, "E", e)        
               z = getValue(line, "Z", z)


               if (getValue(line, "G", None) == 1 or getValue(line, "G", None) == 0) and startEffect == 1 and startFill == 1:
                    f.write("G92 E%0.4f " %(e))
                    f.write("\n")

               else: f.write(line)

