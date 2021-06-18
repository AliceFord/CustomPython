import xml.etree.ElementTree as ET
import os

KNOWN_FUNCTIONS = {"print": "std::cout"}
KNOWN_DOT_FUNCTIONS = {"append": "push_back", "arrlen": "size"}
LEFT_SHIFT_FUNCS = ["std::cout"]
KNOWN_TYPES = {"string": "std::string"}


class Transpile:
	def __init__(self, lexedData, output="output.cpp"):
		self.lexedData = lexedData
		self.outputLoc = output
		self.funcs = []
		self._writeCode(self.transpile())

	def _writeCode(self, data):
		with open("output/" + self.outputLoc, "w") as f:
			output = "#include <bits/stdc++.h>\n\n"
			for func in self.funcs:
				output += func

			output += "\n\n"

			output += "int main() {\n" + data + "\n}"

			f.write(output)

	def run(self):
		print(os.popen("cd output & g++ output.cpp && a").read())

	@staticmethod
	def getTypeName(name: str):
		isArr = False
		if "[]" in name:
			isArr = True

		name = name.replace("[]", "")
		typeName = ""
		if isArr:
			typeName += "std::vector<"
		try:
			typeName += KNOWN_TYPES[name]
		except KeyError:
			typeName += name
		if isArr:
			typeName += ">"
		return typeName

	def transpileRecursive(self, tree, outer=False, betweenChar=None):
		code = ""
		excludeEnding = False
		for ins in tree:
			if ins.tag == "ins":
				code += self.transpileRecursive(ins, True)
			elif ins.tag == "fc":
				useLeftShift = False
				dotFunction = False
				for key, val in KNOWN_FUNCTIONS.items():
					if ins.find("name").text == key:
						if val in LEFT_SHIFT_FUNCS:
							useLeftShift = True
						code += val
						break
				else:
					for key, val in KNOWN_DOT_FUNCTIONS.items():
						if ins.find("name").text == key:
							dotFunction = True
							code += ins.find("params")[0][0].text + "." + val
							break
					else:
						code += ins.find("name").text

				if useLeftShift:
					code += " << ("
				else:
					code += "("

				paramUsed = False
				for param in ins.find("params"):
					if dotFunction and not paramUsed:
						paramUsed = True
						continue
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
			elif ins.tag == "fd":
				excludeEnding = True
				currentFunc = ""
				currentFunc += self.getTypeName(ins.find("type").text) + " "
				currentFunc += ins.find("name").text
				currentFunc += "("
				paramUsed = False
				for param in ins.find("params"):
					paramUsed = True
					currentFunc += self.getTypeName(param.find("type").text) + " "
					currentFunc += param.find("name").text + ","
				if paramUsed:
					currentFunc = currentFunc.rstrip(",")
				currentFunc += ") {\n"
				currentFunc += self.transpileRecursive(ins.find("data"), True)
				currentFunc += "}\n"
				self.funcs.append(currentFunc)
			elif ins.tag == "vd":
				if ins.find("type").text is not None:
					try:
						code += KNOWN_TYPES[ins.find("type").text] + " "
					except KeyError:
						code += ins.find("type").text + " "
				else:
					try:
						code += "std::vector<" + KNOWN_TYPES[ins.find("type").find("type").text] + "> "
					except KeyError:
						code += "std::vector<" + ins.find("type").find("type").text + "> "
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
			elif ins.tag == "return":
				code += "return "
				code += self.transpileRecursive(ins)
			elif ins.tag == "if":
				code += "if (" + self.transpileRecursive(ins.find("cond")) + ") {\n"
				code += self.transpileRecursive(ins.find("data"))
				code += "}"
			elif ins.tag == "arr":
				code += "{"
				code += self.transpileRecursive(ins, False, ",")
				code += "}"
			elif ins.tag == "num":
				code += ins.text
			elif ins.tag == "op":
				code += ins.text
			elif ins.tag == "str":
				code += ins.text

			if betweenChar is not None:
				code += betweenChar

		if outer and not excludeEnding:
			code += ";\n"
		return code

	def transpile(self):
		root = ET.fromstring(self.lexedData)
		code = ""
		for mainIns in root:
			code += self.transpileRecursive(mainIns, True)
		return code