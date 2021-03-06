#Name: Skew
#Info: make the Zlevel uneven over the x-direction full print. CAUTION: maybe you fan or other parts will collide with the object!
#Depend: GCode
#Type: postprocess
#Param: difference(float:30) max skew difference(mm)
#Param: bedX(float:205) size build platform X(mm)
#Param: zScale(float:80) correction in Z

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
import math

def plugin_standalone_usage(myName):
 print "Usage:"
 print "  "+myName+" --min minTemp --max maxTemp --grain grainSize --file gcodeFile"
 print "  "+myName+" -i minTemp -a maxTemp -g grainSize -f gcodeFile"
 print "Licensed under CC-BY-NC from Jeremie.Francois@gmail.com (betterprinter.blogspot.com)"
 sys.exit()

try:
 filename
except NameError:
 # Then we are called from the command line (not from cura)
 # trying len(inspect.stack()) > 2 would be less secure btw
 opts, extraparams = getopt.getopt(sys.argv[1:],'d:x:f:h',['difference=','bedX=','file=']) 
 difference = 40
 bedX = 105
 filename="test.g"
 zScale = 80

 for o,p in opts:
  if o in ['-d','--difference']:
   minTemp = float(p)
  elif o in ['-x','--centerx']:
   maxTemp = float(p)
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
#e = 0
#v = 0
maxZ = 0
maxX = 0
minX = 999
layerheight = 0.2
#zScale = 0.8
startEffect = 0

layer = 0
#persistentZ = 0

with open(filename, "w") as f:
       for line in lines:
               if getValue(line, 'G', None) == 1 or getValue(line, 'G', None) == 0:
                       maxZ = getValue(line, "Z", maxZ) 
                       x = getValue(line, "X", x)
#                       print(maxZ)
# max en min x uitzoeken
                       if x > maxX: maxX = x
                       if x < minX: minX = x

       print(maxX)
       bedX = maxX-minX
#       f.write(maxX)
#       f.write("\n")
#       f.write(bedX)
#       f.write("\n")
#       f.write(difference)
#       f.write("\n")
#       f.write(zScale)
       for line in lines:
               #layer = getValue(line, ';LAYER:', None)
               if ";LAYER:" in line:
                       startEffect = 1
                       print(line)
               
               e = getValue(line, 'E', None)        
               z = getValue(line, "Z", z)
#               if getValue(line, 'G', None) == 1 and e: #only do something with G1 commands
               if (getValue(line, 'G', None) == 1 or getValue(line, 'G', None) == 0) and startEffect == 1: #only do something with G1 and G0 commands
                       #print(e) #should never be None?
                       x = getValue(line, "X", x)
                       y = getValue(line, "Y", y)
                       z = getValue(line, "Z", z)
                       v = getValue(line, "F", None)
                       e = getValue(line, 'E', e)
                       
                       dfactor = (bedX-x)/bedX
#                       newZ = (z * zScale * 0.01) + dfactor*difference*z/maxZ-dfactor-layerheight;
#                       newZ = (z * zScale) + dfactor*difference*z/maxZ-dfactor-layerheight
                       newZ = (z * zScale * 0.01) + dfactor*difference*z/maxZ
#                       if newZ < 0: newZ = 0

                       if e:
                         newE = e + dfactor*0.3*z/maxZ
#                         newE = e
                         newE = round(newE, 3)

                       f.write("G1 ")
                       f.write("X%0.4f " %(x))
                       f.write("Y%0.4f " %(y))
                       f.write("Z%0.4f " %(newZ))
                       if e: f.write("E%0.4f " %(newE))
                       if v: f.write("F%0.1f " %(v))
                       f.write("; oldZ%0.4f " %(z))
                       f.write("\n")
                       
               else: f.write(line)
               
