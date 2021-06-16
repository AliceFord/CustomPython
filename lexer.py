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
		self.is_num = False
		self.is_op = False
		self.is_str = False
		self.is_vdef = False
		self.flags = ["num", "op", "str"]
		self.startElem = -1
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
				if not self.is_str:
					try:
						int(c)
						self.foundElement("num", parentElement, ins, self.startElem, i)
					except ValueError:
						self.setFlag("num", parentElement, ins, self.startElem, i)

					if c in ["+", "-", "*", "/"]:
						self.foundElement("op", parentElement, ins, self.startElem, i)
					else:
						self.setFlag("op", parentElement, ins, self.startElem, i)

				if c == "\"":
					self.foundElement("str", parentElement, ins, self.startElem, i)
				else:
					pass

				if c == " ":
					self.setAllFlagsExcept(None, parentElement, ins, self.startElem, i)

			self.setAllFlagsExcept(None, parentElement, ins, self.startElem)

	def foundElement(self, flag, parent, ins, startRange, endRange):
		self.setAllFlagsExcept(flag, parent, ins, startRange, endRange)
		if not getattr(self, "is_" + flag):
			setattr(self, "is_" + flag, True)
			self.startElem = endRange

	def setFlag(self, flag, element, ins, startRange, endRange):
		if getattr(self, "is_" + flag):
			tag = ET.SubElement(element, flag)
			tag.text = ins[startRange:endRange]
		setattr(self, "is_" + flag, False)

	def setAllFlagsExcept(self, flag, element, ins, startRange, endRange=None):
		if endRange is None:
			endRange = len(ins)

		if flag is None:
			for overallFlag in self.flags:
				if getattr(self, "is_" + overallFlag):
					tag = ET.SubElement(element, overallFlag)
					tag.text = ins[startRange:endRange]
		else:
			for overallFlag in self.flags:
				if flag != overallFlag:
					if getattr(self, "is_" + overallFlag):
						tag = ET.SubElement(element, overallFlag)
						tag.text = ins[startRange:endRange]
					setattr(self, "is_" + overallFlag, False)
