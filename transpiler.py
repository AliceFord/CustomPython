import xml.etree.ElementTree as ET
import os

KNOWN_FUNCTIONS = {"print": "std::cout"}
LEFT_SHIFT_FUNCS = ["std::cout"]
KNOWN_TYPES = {"string": "std::string"}


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
			if ins.tag == "ins":
				code += self.transpileRecursive(ins, True)
			elif ins.tag == "fc":
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
					code += " << ("
				else:
					code += "("

				paramUsed = False
				for param in ins.find("params"):
					paramUsed = True
					code += self.transpileRecursive(param)
					if useLeftShift:
						code += ") << ("
					else:
						code += ","

				if paramUsed:
					if useLeftShift:
						code = code.rstrip(" << (")
					else:
						code = code.rstrip(",")
				if not useLeftShift:
					code += ")"
			elif ins.tag == "vd":
				try:
					code += KNOWN_TYPES[ins.find("type").text] + " "
				except KeyError:
					code += ins.find("type").text + " "
				code += ins.find("name").text + " = "
				code += self.transpileRecursive(ins.find("data"))
			elif ins.tag == "vc":
				code += ins.text
			elif ins.tag == "vrd":
				code += ins.find("name").text + " = "
				code += self.transpileRecursive(ins.find("data"))
			elif ins.tag == "while":
				code += "while (" + self.transpileRecursive(ins.find("cond")) + ") {\n"
				code += self.transpileRecursive(ins.find("data"))
				code += "}"
			elif ins.tag == "break":
				code += "break"
			elif ins.tag == "if":
				code += "if (" + self.transpileRecursive(ins.find("cond")) + ") {\n"
				code += self.transpileRecursive(ins.find("data"))
				code += "}"
			else:
				code += self.decodeInstruction(ins)

		if outer:
			code += ";\n"
		return code

	def transpile(self):
		root = ET.fromstring(self.lexedData)
		code = ""
		for mainIns in root:
			code += self.transpileRecursive(mainIns, True)
		return code

	@staticmethod
	def decodeInstruction(ins):
		code = ""
		if ins.tag == "num":
			code += ins.text
		if ins.tag == "op":
			code += ins.text
		if ins.tag == "str":
			code += ins.text
		return code

