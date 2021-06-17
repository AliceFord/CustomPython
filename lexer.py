import lxml.etree as ET
import re
import string


class CustomPythonLexer:
	def __init__(self, file):
		self.fors = []
		self.file = file

	def doLexing(self):
		main = ET.Element("main")
		with open(self.file) as f:
			data = f.read()
			data = self.expandMacros(data)
			data = data.split(";")
			while True:
				try:
					data.remove('')
				except ValueError:
					break

			for i, dp in enumerate(data):
				data[i] = dp.replace("\n", "").replace("\t", "")

			nestCounter = 0
			nestTag = None

			for ins in data:
				if nestCounter > 0:
					insTag = ET.SubElement(nestTag, "ins")
					chosenParent = nestTag
					flags = self.decodeInstruction(ins, insTag)
				else:
					insTag = ET.SubElement(main, "ins")
					chosenParent = main
					flags = self.decodeInstruction(ins, insTag)
				prevWhileCounter = nestCounter
				nestCounter += flags["nest"]
				if nestCounter > prevWhileCounter:
					nestTag = flags["tag"]
				elif nestCounter < prevWhileCounter:
					nestTag = flags["tag"]

				if nestCounter < prevWhileCounter and not flags["break"]:
					chosenParent.remove(insTag)

		with open("test.xml", "wb") as f: f.write(ET.tostring(main, pretty_print=True))
		return ET.tostring(main)

	def placeForLoop(self, m: re.Match[string]):
		start = m.group(1) + ";\nwhile" + m.group(2)
		message = m.string
		message = message[:m.span()[0]] + start + message[m.span()[1]:]
		endCounter = 0
		for i, line in enumerate(message.split(";")):
			if "for" in line and "(" in line:
				endCounter += 1
			if "endfor" in line:
				endCounter -= 1

				if endCounter < 0:
					message = message.split(";")
					message[i] = "\nendwhile"
					message.insert(i, "\n" + m.group(3))
					message = ';'.join(message)
					break
		return message

	def expandMacros(self, data):
		while True:
			m = re.search("for[ ]*\((.*?);(.*?);(.*?)\)", data)
			if m is None:
				break
			data = self.placeForLoop(m)

		return data

	def decodeInstruction(self, ins, parentElement):
		self.is_num = False
		self.is_op = False
		self.is_str = False
		self.is_vc = False
		self.flags = ["num", "op", "str", "vc"]
		self.startElem = -1
		funcChecker = re.compile("([a-zA-Z][a-zA-Z0-9]*?)\((.*)\)")
		vdChecker = re.compile("([a-zA-Z][a-zA-Z0-9]*) ([a-zA-Z][a-zA-Z0-9]*)[ ]*=[ ]*(.*)")
		vdarrChecker = re.compile("([a-zA-Z][a-zA-Z0-9]*)\[\] ([a-zA-Z][a-zA-Z0-9]*)[ ]*=[ ]*(.*)")
		vrdChecker = re.compile("([a-zA-Z][a-zA-Z0-9]*)[ ]*=[ ]*(.*)")
		whileChecker = re.compile("while[ ]*(.*)")
		ifChecker = re.compile("if[ ]+(.*)")
		conditionalChecker = re.compile("([a-zA-Z][a-zA-Z0-9]*)[ ]*=[=]+?[ ]*(.*)")
		arrChecker = re.compile("\[(.*)\]")

		ins = ins.replace("True", "true").replace("False", "false")

		isFunc = funcChecker.match(ins)
		isVd = vdChecker.match(ins)
		isVdarr = vdarrChecker.match(ins)
		isVrd = vrdChecker.match(ins)
		isWhile = whileChecker.match(ins)
		isIf = ifChecker.match(ins)
		isConditional = conditionalChecker.match(ins)
		isArr = arrChecker.match(ins)
		if isWhile:
			whileTag = ET.SubElement(parentElement, "while")
			condTag = ET.SubElement(whileTag, "cond")
			self.decodeInstruction(isWhile.group(1), condTag)
			dataTag = ET.SubElement(whileTag, "data")
			return {"nest": 1, "tag": dataTag}
		elif isIf:
			ifTag = ET.SubElement(parentElement, "if")
			condTag = ET.SubElement(ifTag, "cond")
			self.decodeInstruction(isIf.group(1), condTag)
			dataTag = ET.SubElement(ifTag, "data")
			return {"nest": 1, "tag": dataTag}
		elif ins == "endwhile":
			parentElement.attrib["remove"] = ""
			try:
				return {"nest": -1, "break": False, "tag": parentElement.getparent().getparent().getparent().getparent()}
			except AttributeError:
				return {"nest": -1, "break": False, "tag": "ignored"}
		elif ins == "break":
			breakTag = ET.SubElement(parentElement, "break")
		elif ins == "endif":
			parentElement.attrib["remove"] = ""
			try:
				return {"nest": -1, "break": False, "tag": parentElement.getparent().getparent().getparent().getparent()}
			except AttributeError:
				return {"nest": -1, "break": False, "tag": "ignored"}
		elif isFunc:
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
		elif isVdarr:
			vdTag = ET.SubElement(parentElement, "vd")
			typeTag = ET.SubElement(vdTag, "type")
			typeTag2 = ET.SubElement(typeTag, "type")
			typeTag2.text = isVdarr.group(1)
			arrTag = ET.SubElement(typeTag, "arr")
			nameTag = ET.SubElement(vdTag, "name")
			nameTag.text = isVdarr.group(2)
			dataTag = ET.SubElement(vdTag, "data")
			self.decodeInstruction(isVdarr.group(3), dataTag)
		elif isVrd and not isConditional:
			vrdTag = ET.SubElement(parentElement, "vrd")
			nameTag = ET.SubElement(vrdTag, "name")
			nameTag.text = isVrd.group(1)
			dataTag = ET.SubElement(vrdTag, "data")
			self.decodeInstruction(isVrd.group(2), dataTag)
		elif isArr:
			arrTag = ET.SubElement(parentElement, "arr")
			for element in isArr.group(1).split(","):
				self.decodeInstruction(element, arrTag)
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

					if c in ["+", "-", "*", "/", "<", ">", "=", "%"]:
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

		return {"nest": 0}

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
