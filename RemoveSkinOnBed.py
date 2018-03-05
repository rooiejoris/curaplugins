# /Applications/Cura.app/Contents/MacOS/cura --debug
# Apple+k [clear screen in terminal
#/Applications/Cura.app/Contents/MacOS/cura /Users/jorisvantubergen/Downloads/resumetest_wrench.stl	 --debug

from ..Script import Script
# from cura.Settings.ExtruderManager import ExtruderManager

class RemoveSkinOnBed(Script):
	def __init__(self):
		super().__init__()

	def getSettingDataString(self):
		return """{
			"name":"RemoveSkinOnBed",
			"key": "RemoveSkinOnBed",
			"metadata": {},
			"version": 2,
			"settings":
			{
				"removeinskinonbed":
				{
					"label": "Remove skin on bed",
					"description": "Remove skin on bed for filling with plaster",
                    "type": "bool",
                    "default_value": true
				}
			}
		}"""

	def execute(self, data: list):

		"""data is a list. Each index contains a layer"""

		startEffect = 0
		startSkin = 0
		e = 0
		layer = 0
		fromZ = self.getSettingValueByKey("fromz")

		# T = ExtruderManager.getInstance().getActiveExtruderStack().getProperty("material_print_temperature", "value")

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

				if ";TYPE:SKIN" in line:
					startSkin = 1
#					 print("fill detected")
#					 print(layer)

				if ";LAYER:" in line:
					startFill = 0
#					 print("fill stop")

				if ";TYPE:" in line and not ";TYPE:SKIN" and startSkin == 1 in line:
					startSkin = 0
					lineinsert=("\n;+++++++++++++ start reset E value +++++++++++++++")
					lineinsert+=("\n")
					lineinsert+=("G92 ")
					lineinsert+=("E%0.4f " %(e))
					lineinsert+=("\n")
					lineinsert+=("\n;+++++++++++++ end reset E value +++++++++++++++")
					lineinsert+=("\n")
					line += lineinsert
#					 print("fill stop")

				if layer_nr < 3 and startSkin == 1:# and layer_nr > 0:
					print("start")
					line = ";removed\n"
					#continue

				# have to actively empty the 'lines' for the things I want to through away
#				if cutZ == 0 and layer_nr > 1:
#					print("hola3")
#					lines.pop(line_nr)
					#print("should be removed lines, line_nr: {}".format(lines[line_nr]))
					#line = ";999"
					#continue


				lines[line_nr] = line


			data[layer_nr] = "\n".join(lines)

		print(data)
		return data
