#Name: maxXY runs
#Info: Makes some runs to check the max X and Y values, sometimes the skirt, raft or brim are not the max values
#Depend: GCode
#Type: postprocess
#Param: runs(int:2) number of runs
#Param: speed(float:70) speed of the moves (mm/s)
#Param: Zheight(float:1) Height above platform (mm)

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
 print "Usage:"
 print "  "+myName+" -d difference -x centerx -y centery -w waves -l layerheight -n fromlayer -f gcodeFile"
 print "Licensed under CC-BY-NC from Jeremie.Francois@gmail.com (betterprinter.blogspot.com)"
 sys.exit()

try:
 filename
except NameError:
 # Then we are called from the command line (not from cura)
 # trying len(inspect.stack()) > 2 would be less secure btw
 opts, extraparams = getopt.getopt(sys.argv[1:],'d:x:f:h',['difference=','bedX=','file=']) 
 runs = 2
 speed = 70
 Zheight = 1
 filename="test.g"

 for o,p in opts:
  if o in ['-d','--difference']:
   minTemp = float(p)
  elif o in ['-x','--centerx']:
   maxTemp = float(p)
  elif o in ['-f','--file']:
   filename = p
  elif o in ['-n','--fromlayer']:
   layerheight = float(p)
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

z = 50
x = 50
y = 50
#e = 0
#v = 0
fspeed = speed*60
maxX = 0
maxY = 0
maxZ = 0
minX = 999
minY = 999
minZ = 999
layer = 999

with open(filename, "w") as f:
       for line in lines:
               if ";LAYER:" in line:
#                    print("binnen")
                    layer = line[7:]
#                    print(layer)
               if int(layer) > 0:
                    if getValue(line, 'G', None) == 1 or getValue(line, 'G', None) == 0:
                           maxZ = getValue(line, "Z", maxZ) 
                           x = getValue(line, "X", x)
                           y = getValue(line, "Y", y)
#                           print(x)
                    # max en min x en y uitzoeken
                           if x > maxX: maxX = x
                           if x < minX: minX = x
                           if y > maxY: maxY = y
                           if y < minY: minY = y

#       print(minX)
#       print(maxX)
#       print(minY)
#       print(maxY)


       for line in lines:
               if ";LAYER:" in line:
#                    print("binnen")
                    layer = line[7:]
#                    print(layer)
                    if int(layer) == 0:
#                        print("binnen1")
#                        f.write(";maxXY runs, maxXsize" %(maxX-minX) ", maxYsize" %(maxY-minY))
                        f.write("\n")
                        for _ in range(int(runs)):
                               f.write("G1 ")
                               f.write("X%0.4f " %(maxX))
                               f.write("Z%0.4f " %(Zheight))
                               f.write("F%0.1f " %(fspeed))
                               f.write("\n")
                               f.write("G1 ")
                               f.write("Y%0.4f " %(maxY))
                               f.write("\n")
                               f.write("G1 ")
                               f.write("X%0.4f " %(minX))
                               f.write("\n")
                               f.write("G1 ")
                               f.write("Y%0.4f " %(minY))
                               f.write("\n")
                        f.write(";LAYER:0")
                        f.write("\n")

                    else: f.write(line)
               else: f.write(line)
