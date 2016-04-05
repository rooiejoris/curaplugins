#Name: chop
#Info: chop a part of the gcode to combine different gcodes with different profiles
#Depend: GCode
#Type: postprocess
#Param: layer(float:30) from which layer is this profile needed
#Param: profile(float:205) size build platform X(mm)

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
#	wood_standalone.py --min minTemp --max maxTemp --grain grainSize --file gcodeFile
# It will "patch" your gcode file with the appropriate M104 temperature change.
#
import inspect
import sys
import getopt
#import math
#import os

def plugin_standalone_usage(myName):
 print "Usage:"
 print "  "+myName+" --fromlayer use the gcode from --fromz use the gcode from z height --part which part --file gcodeFile"
 print "  "+myName+" -l fromlayer -z fromZ  -p part -f gcodeFile"
 sys.exit()

try:
	filename
except NameError:
# Then we are called from the command line (not from cura)
# trying len(inspect.stack()) > 2 would be less secure btw
	opts, extraparams = getopt.getopt(sys.argv[1:],'l:z:p:f:',['fromlayer=','fromZ=','part=','file='])
#	layer = 0
#	part = ""
#	filename="test.g"
	print (opts)

for o,p in opts:
	if o in ['-l','--fromlayer']:
#		print (p)
		fromlayer = int(p)
	elif o in ['-z','--fromZ']:
#		print (p)
		fromZ = p
	elif o in ['-p','--part']:
#		print int(p)
		part = int(p)
	elif o in ['-f','--file']:
#		print (p)
		filename = p
#	filename = 'test.g'
if not filename:
	plugin_standalone_usage(inspect.stack()[0][1])
#	plugin_standalone_usage('test.g')
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

layer = 0
e = 0
z = 0
cutZ = 0
cutZ = 0
fanonaftercounter = 0
fanonafter = 4

#fromZ = 10.2

fromZ = ("%0.4f" %(float(fromZ)))
fromZ = float(fromZ)
#print ("%0.4f" %(fromZ))
print (fromZ)

removelines = 1

resumegcode = """;+++++++++++++ resumegcode +++++++++++++++
M104 S220 ;Uncomment to add your own temperature line
M42 P3 S150
G21        ;metric values
G90        ;absolute positioning
M82        ;set extruder to absolute mode
M107       ;start with the fan off
G28 X0 Y0  ;move X/Y to min endstops
M109 S220 ;Uncomment to add your own temperature line
G92 E0                  ;zero the extruded length
G1 F200 E3              ;extrude 3mm of feed stock
G92 E0                  ;zero the extruded length again
G1 F9000
M220 S30
M221 S150

;+++++++++++++ end resume +++++++++++++++\n\n"""


with open(filename, "w") as f:
	print "hola1"

	for line in lines:
			if getValue(line, "E", e) > 0:
				e = getValue(line, "E", e)

			if getValue(line, "Z", z) >= fromZ and cutZ == 0 and layer > 0:
				print(getValue(line, "Z", z))
#				print (cutZ)
				z = getValue(line, "Z", z)
#				f.write(line)
				cutZ = 1
				#print (cutZ)
#			else: cutZ = 2
			if ";LAYER:" in line:
				layer = line[7:]
#			else: layer = -1

#			if int(layer) == int(fromlayer):
			if cutZ == 1:
				print "hola"
				removelines = 0
				f.write(";+++++++++++++ " + filename + " +++++++++++++++")
				f.write("\n")
				f.write(resumegcode)
				f.write("\n")
				f.write(";+++++++++++++ cutted from here +++++++++++++++")
				f.write("\n")
				f.write(";LAYER:"+layer)	
				f.write("\n")
				f.write("G92 ")
				f.write("E%0.4f " %(e))
				f.write("\n")
				f.write("\n")
				f.write("G92 ")
				f.write("Z%0.4f " %(z))
				f.write("\n")
				f.write(";+++++++++++++   +++++++++++++++")
				f.write("\n")
				f.write("\n")
				f.write(line)
				cutZ = 2

			if cutZ == 2:
				f.write(line)

			if cutZ == 2 and ";LAYER:" in line:
				fanonaftercounter = fanonaftercounter + 1

			if fanonaftercounter == fanonafter:
				f.write("M106 S255")
				f.write("\n")
				fanonaftercounter = fanonaftercounter + 1


f.close()

