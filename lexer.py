import lxml.etree as ET
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

			for ins in data:
				insTag = ET.SubElement(main, "ins")
				self.decodeInstruction(ins, insTag)

		with open("test.xml", "wb") as f: f.write(ET.tostring(main, pretty_print=True))
		return ET.tostring(main)
		#return "<main><ins><fc><name>PRINT</name><params><_1><num>1</num><op>*</op><num>1</num></_1></params></fc></ins><ins><fc><name>PRINT</name><params><_1><num>1</num><op>+</op><num>1</num></_1></params></fc></ins></main>"

	def decodeInstruction(self, ins, parentElement):
		self.isNum = False
		self.isOp = False
		self.isStr = False
		self.isVDef = False
		startElem = -1
		funcChecker = re.compile("([a-zA-Z][a-zA-Z0-9]*?)\((.*)\)")

		isFunc = funcChecker.match(ins)
		if isFunc:
			fcTag = ET.SubElement(parentElement, "fc")
			nameTag = ET.SubElement(fcTag, "name")
			nameTag.text = isFunc.group(1)
			paramsTag = ET.SubElement(fcTag, "params")
			for i, param in enumerate(isFunc.group(2).split(",")):
				currentParamTag = ET.SubElement(paramsTag, "_" + str(i))
				self.decodeInstruction(param, currentParamTag)
		else:
			for i, c in enumerate(ins):
				if not self.isStr:
					try:
						int(c)
						self.setAllFlagsExcept("num", parentElement, ins, startElem, i)
						if not self.isNum:
							self.isNum = True
							startElem = i
					except ValueError:
						self.setFlag("num", parentElement, ins, startElem, i)

					if c in ["+", "-", "*", "/"]:
						self.setAllFlagsExcept("op", parentElement, ins, startElem, i)
						if not self.isOp:
							self.isOp = True
							startElem = i
					else:
						self.setFlag("op", parentElement, ins, startElem, i)

				if c == "\"":
					self.setAllFlagsExcept("str", parentElement, ins, startElem, i)
					if not self.isStr:
						self.isStr = True
						startElem = i
				else:
					pass

				if c == " ":
					self.setAllFlagsExcept(None, parentElement, ins, startElem, i)

			self.setAllFlagsExcept(None, parentElement, ins, startElem)

	def setFlag(self, flag, element, ins, startRange, endRange):
		if flag == "op":
			if self.isOp:
				opTag = ET.SubElement(element, "op")
				opTag.text = ins[startRange:endRange]
			self.isOp = False
		elif flag == "num":
			if self.isNum:
				numTag = ET.SubElement(element, "num")
				numTag.text = ins[startRange:endRange]
			self.isNum = False
		elif flag == "str":
			if self.isStr:
				strTag = ET.SubElement(element, "str")
				strTag.text = ins[startRange:endRange]
			self.isStr = False
		elif flag == "vdef":
			if self.isVDef:
				strTag = ET.SubElement(element, "vdef")
				strTag.text = ins[startRange:endRange]
			self.isStr = False

	def setAllFlagsExcept(self, flag, element, ins, startRange, endRange=None):
		if endRange is None:
			endRange = len(ins)

		if flag is None:
			if self.isOp:
				opTag = ET.SubElement(element, "op")
				opTag.text = ins[startRange:endRange]

			if self.isNum:
				numTag = ET.SubElement(element, "num")
				numTag.text = ins[startRange:endRange]

			if self.isStr:
				strTag = ET.SubElement(element, "str")
				strTag.text = ins[startRange:endRange]
		elif flag == "num":
			if self.isOp:
				opTag = ET.SubElement(element, "op")
				opTag.text = ins[startRange:endRange]
			self.isOp = False

			if self.isStr:
				strTag = ET.SubElement(element, "str")
				strTag.text = ins[startRange:endRange]
			self.isStr = False
		elif flag == "op":
			if self.isNum:
				numTag = ET.SubElement(element, "num")
				numTag.text = ins[startRange:endRange]
			self.isNum = False

			if self.isStr:
				strTag = ET.SubElement(element, "str")
				strTag.text = ins[startRange:endRange]
			self.isStr = False

		elif flag == "str":
			if self.isNum:
				numTag = ET.SubElement(element, "num")
				numTag.text = ins[startRange:endRange]
			self.isNum = False

			if self.isOp:
				opTag = ET.SubElement(element, "op")
				opTag.text = ins[startRange:endRange]
			self.isOp = False
