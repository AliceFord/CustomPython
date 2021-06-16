import xml.etree.ElementTree as ET
import re


class CustomPythonLexer:
	def __init__(self, file):
		self.file = file

	def doLexing(self):
		main = ET.Element("main")
		with open(self.file) as f:
			data = f.read().split(";")
			while True:
				try:
					data.remove('')
				except ValueError:
					break

			for i, dp in enumerate(data):
				data[i] = dp.replace("\n", "")

			funcChecker = re.compile("([a-zA-Z][a-zA-Z0-9]*?)\((.*?)\)")

			for ins in data:
				insTag = ET.SubElement(main, "ins")
				isFunc = funcChecker.match(ins)
				if isFunc:
					fcTag = ET.SubElement(insTag, "fc")
					nameTag = ET.SubElement(fcTag, "name")
					nameTag.text = isFunc.group(1)
					paramsTag = ET.SubElement(fcTag, "params")
					for i, param in enumerate(isFunc.group(2).split(",")):
						currentParamTag = ET.SubElement(paramsTag, "_" + str(i))
						self.decodeInstruction(param, currentParamTag)
				else:
					self.decodeInstruction(ins, insTag)

		ET.dump(main)  # Print
		return ET.tostring(main)
		#return "<main><ins><fc><name>PRINT</name><params><_1><num>1</num><op>*</op><num>1</num></_1></params></fc></ins><ins><fc><name>PRINT</name><params><_1><num>1</num><op>+</op><num>1</num></_1></params></fc></ins></main>"

	@staticmethod
	def decodeInstruction(ins, parentElement):
		isNum = False
		isOp = False
		startElem = -1
		for i, c in enumerate(ins):
			try:
				int(c)
				if isOp:
					opTag = ET.SubElement(parentElement, "op")
					opTag.text = ins[startElem:i]
				isOp = False
				if not isNum:
					isNum = True
					startElem = i
			except ValueError:
				if isNum:
					numTag = ET.SubElement(parentElement, "num")
					numTag.text = ins[startElem:i]
				isNum = False

			if c in ["+", "-", "*", "/"]:
				if isNum:
					numTag = ET.SubElement(parentElement, "num")
					numTag.text = ins[startElem:i]
				isNum = False
				if not isOp:
					isOp = True
					startElem = i
			else:
				if isOp:
					opTag = ET.SubElement(parentElement, "op")
					opTag.text = ins[startElem:i]
				isOp = False

		if isOp:
			opTag = ET.SubElement(parentElement, "op")
			opTag.text = ins[startElem:]

		if isNum:
			numTag = ET.SubElement(parentElement, "num")
			numTag.text = ins[startElem:]
