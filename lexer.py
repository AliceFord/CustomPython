import lxml.etree as ET
import re
import string


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
		self.is_vc = False
		self.flags = ["num", "op", "str", "vc"]
		self.startElem = -1
		funcChecker = re.compile("([a-zA-Z][a-zA-Z0-9]*?)\((.*)\)")
		vdChecker = re.compile("([a-zA-Z][a-zA-Z0-9]*) ([a-zA-Z][a-zA-Z0-9]*)[ ]*=[ ]*(.*)")
		vrdChecker = re.compile("([a-zA-Z][a-zA-Z0-9]*)[ ]*=[ ]*(.*)")

		isFunc = funcChecker.match(ins)
		isVd = vdChecker.match(ins)
		isVrd = vrdChecker.match(ins)
		if isFunc:
			fcTag = ET.SubElement(parentElement, "fc")
			nameTag = ET.SubElement(fcTag, "name")
			nameTag.text = isFunc.group(1)
			paramsTag = ET.SubElement(fcTag, "params")
			for i, param in enumerate(isFunc.group(2).split(",")):
				currentParamTag = ET.SubElement(paramsTag, "_" + str(i))
				self.decodeInstruction(param, currentParamTag)
		elif isVd:
			vdTag = ET.SubElement(parentElement, "vd")
			typeTag = ET.SubElement(vdTag, "type")
			typeTag.text = isVd.group(1)
			nameTag = ET.SubElement(vdTag, "name")
			nameTag.text = isVd.group(2)
			dataTag = ET.SubElement(vdTag, "data")
			self.decodeInstruction(isVd.group(3), dataTag)
		elif isVrd:
			vrdTag = ET.SubElement(parentElement, "vrd")
			nameTag = ET.SubElement(vrdTag, "name")
			nameTag.text = isVrd.group(1)
			dataTag = ET.SubElement(vrdTag, "data")
			self.decodeInstruction(isVrd.group(2), dataTag)
		else:
			for i, c in enumerate(ins):
				if not self.is_str:
					self.currentlyFound = False
					try:
						int(c)
						if not self.is_vc:
							self.foundElement("num", parentElement, ins, self.startElem, i)
					except ValueError:
						pass

					if c in ["+", "-", "*", "/"]:
						self.foundElement("op", parentElement, ins, self.startElem, i)
					else:
						pass

					if not self.currentlyFound:
						if c in string.ascii_letters + string.digits:
							self.foundElement("vc", parentElement, ins, self.startElem, i)

					if c == " ":
						self.setAllFlagsExcept(None, parentElement, ins, self.startElem, i)

				if c == "\"":
					self.foundElement("str", parentElement, ins, self.startElem, i)
				else:
					pass

			self.setAllFlagsExcept(None, parentElement, ins, self.startElem)

	def foundElement(self, flag, parent, ins, startRange, endRange):
		self.setAllFlagsExcept(flag, parent, ins, startRange, endRange)
		if not getattr(self, "is_" + flag):
			setattr(self, "is_" + flag, True)
			self.startElem = endRange

		self.currentlyFound = True

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
				setattr(self, "is_" + overallFlag, False)
		else:
			for overallFlag in self.flags:
				if flag != overallFlag:
					if getattr(self, "is_" + overallFlag):
						tag = ET.SubElement(element, overallFlag)
						tag.text = ins[startRange:endRange]
					setattr(self, "is_" + overallFlag, False)
