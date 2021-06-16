import xml.etree.ElementTree as ET
import os

KNOWN_FUNCTIONS = {"PRINT": "std::cout"}
LEFT_SHIFT_FUNCS = ["std::cout"]


class Transpile:
	def __init__(self, lexedData, output="output.cpp"):
		self.lexedData = lexedData
		self.outputLoc = output
		self._writeCode(self.transpile())

	def _writeCode(self, data):
		with open("output/" + self.outputLoc, "w") as f:
			f.write("#include <bits/stdc++.h>\n\nint main() {\n" + data + "\n}")

	def run(self):
		print(os.popen("cd output & g++ output.cpp && a").read())

	def transpileRecursive(self, tree, outer=False):
		code = ""
		for ins in tree:
			if ins.tag == "fc":
				useLeftShift = False
				for key, val in KNOWN_FUNCTIONS.items():
					if ins.find("name").text == key:
						if val in LEFT_SHIFT_FUNCS:
							useLeftShift = True
						code += val
						break
				else:
					code += ins.find("name").text

				if useLeftShift:
					code += " << "
				else:
					code += "("

				paramUsed = False
				for param in ins.find("params"):
					paramUsed = True
					code += self.transpileRecursive(param)
					if useLeftShift:
						code += " << "
					else:
						code += ","

				if paramUsed:
					if useLeftShift:
						code = code.rstrip(" << ")
					else:
						code = code.rstrip(",")
				if not useLeftShift:
					code += ")"
			else:
				code += self.decodeInstruction(tree)
				break

		if outer:
			code += ";"
		return code

	def transpile(self):
		root = ET.fromstring(self.lexedData)
		code = ""
		for mainIns in root:
			code += self.transpileRecursive(mainIns, True)
		return code

	@staticmethod
	def decodeInstruction(outerIns):
		code = ""
		for ins in outerIns:
			if ins.tag == "num":
				code += ins.text
			if ins.tag == "op":
				code += ins.text
		return code

