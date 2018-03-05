# /Applications/Cura.app/Contents/MacOS/cura --debug
# Apple+k [clear screen in terminal
#/Applications/Cura.app/Contents/MacOS/cura /Users/jorisvantubergen/Downloads/resumetest_wrench.stl  --debug

from ..Script import Script
# from cura.Settings.ExtruderManager import ExtruderManager

class ResumeAtHeight(Script):
	def __init__(self):
		super().__init__()

	def getSettingDataString(self):
		return """{
			"name":"1Resume at height",
			"key": "1ResumeAtHeight",
			"metadata": {},
			"version": 2,
			"settings":
			{
				"fromz":
				{
					"label": "From Z in mm",
					"description": "At what height should we resume",
					"unit": "mm",
					"type": "float",
					"default_value": 0.0
				}
			}
		}"""

	def execute(self, data: list):

		"""data is a list. Each index contains a layer"""

		cuttedlayernr = 0
		x = 0.
		y = 0.
		e = 0
		z = 0
		cutZ = 0
		fanonafter = 4
		fanonaftercounter = 0
		current_z = 0.
		fromZ = self.getSettingValueByKey("fromz")

		# T = ExtruderManager.getInstance().getActiveExtruderStack().getProperty("material_print_temperature", "value")
		# with open("out.txt", "w") as f:
			# f.write(T)

		# use offset to calculate the current height: <current_height> = <current_z> - <layer_0_z>
		layer_0_z = 0.

		removelines = 1

		resumegcode = """;+++++++++++++ resumegcode +++++++++++++++
		M104 S220 ;Uncomment to add your own temperature line
		M42 P3 S150
		G21		   ;metric values
		G90		   ;absolute positioning
		M82		   ;set extruder to absolute mode
		M107	   ;start with the fan off
		G28 X0 Y0  ;move X/Y to min endstops
		M109 S220 ;Uncomment to add your own temperature line
		G92 E0					;zero the extruded length
		G1 F200 E3				;extrude 3mm of feed stock
		G92 E0					;zero the extruded length again
		G1 F9000
		M220 S30
		M221 S150

		;+++++++++++++ end resume +++++++++++++++\n\n"""


		got_first_g_cmd_on_layer_0 = False
		for layer_nr, layer in enumerate(data):
			lines = layer.split("\n")
			#print("/nlayer: {}".format(layer))
			for line_nr, line in enumerate(lines):

				#print("Getvalue: {}".format(self.getValue(line, "Z", z)))
				#print("fromZ: {}".format(fromZ))
				#print("cutZ: {}".format(cutZ))
				#print("tada layer_nr: {}".format(layer_nr))

				if self.getValue(line, "E", e) > 0:
					e = self.getValue(line, "E", e)

				if cutZ == 1:
					print("hola")
					removelines = 0
					lineinsert=("\n;+++++++++++++ start resume code +++++++++++++++")
					lineinsert+=("\n")
					lineinsert+=(resumegcode)
					lineinsert+=("\n")
					lineinsert+=(";+++++++++++++ cutted from here +++++++++++++++")
					lineinsert+=("\n")
					lineinsert+=(";LAYER:"+str(layer_nr-2))	  
					lineinsert+=("\n")
					lineinsert+=("G92 ")
					lineinsert+=("E%0.4f " %(e))
					lineinsert+=("\n")
					lineinsert+=("\n")
					lineinsert+=("G92 ")
					lineinsert+=("Z%0.4f " %(z))
					lineinsert+=("\n")
					lineinsert+=(";+++++++++++++ end resume code +++++++++++++++")
					lineinsert+=("\n")
					lineinsert+=("\n")
					lineinsert+=line
					line = lineinsert
					print(lineinsert)
					cuttedlayernr = layer_nr
					cutZ = 2
					#continue

				if layer_nr == cuttedlayernr + fanonafter and cutZ == 2:
					lineinsert=(";+++++++++++++ fan on +++++++++++++++")
					lineinsert+=("\nM106 S255")
					lineinsert+=("\n")
					line+=lineinsert
					cutZ = 3
					#continue

				if self.getValue(line, "Z", z) > fromZ and cutZ == 0:# and layer_nr > 0:
					print("hola2")
					z = self.getValue(line, "Z", z)
					cutZ = 1
					#line = ";removed\n"
					#continue

				# have to actively empty the 'lines' for the things I want to through away
				if cutZ == 0 and layer_nr > 1:
					print("hola3")
#				    lines.pop(line_nr)
					#print("should be removed lines, line_nr: {}".format(lines[line_nr]))
					#line = ";999"
					#continue


				lines[line_nr] = line


			print("is this cutZ: {}".format(cutZ))
			if cutZ == 0:
				print("tada line_nr ++++: {}".format(layer_nr))
				data[layer_nr] = "\n;removed"
				#print("tada lines that should be removed: {}".format(lines))
				#lines.pop(line_nr)
				#del data[layer_nr] #this worked sort of... removes every other line
				#lines.remove(999)
				#continue
			else:
				print("binnen: {}".format(lines))
				data[layer_nr] = "\n".join(lines)
#			data[layer_nr] = "\n".join(lines)

		print(data)
		return data
