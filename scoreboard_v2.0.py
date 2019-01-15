#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: AGGGGG
# @Mail  : lynngan39@163.com
# @File  : scoreboard.py

import re


class InstructionStatusTable(object):
	def __init__(self):
		self.instructionList = list()
		self.usingTime = {
							"LD" : 1,
							"SD" : 1,
							"ADDD" : 2,
							"SUBD" : 2,
							"MULT" : 10,
							"DIVD" : 40
						}

	# 向指令列表instructionList中添加一条指令,其中target为WR的目标寄存器
	def addInstruction(self, instruction):
		ins, target, j, k = re.split(' ', instruction)
		instructionItem = {
			"instruction" : ins,
			"target" : target,
			"j" : j,
			"k" : k,
			"issue" : "",
			"readOperand" : "",
			"exeComplet" : "",
			"writeResult" : ""
		}
		# issue,readOperand,exeComplet,writeResult均初始化为0
		self.instructionList.append(instructionItem)

	def getList(self):
		return self.instructionList

	def getNext(self):
		for item in self.instructionList:
			if item["issue"] == "":
				return item["instruction"],item["target"],item["j"],item["k"]
		return None,None,None,None

	def fresh(self, name, target, instruction, funcUTable, cycle):
		release_flag = False
		# release_unit = ""
		release_target = ""
		# 更新已发射项
		for item in self.instructionList:
			if item["issue"] != "":
				# 发射但未读数
				if item["readOperand"] == "":
					for unit in funcUTable:
						if self.change_name(item["instruction"]) in unit["name"] and unit["Fi"]==item["target"]:
							if unit["Rj"]!="No" and unit["Rk"]!="No":
								item["readOperand"] = cycle
				# 发射且读数则考虑是否更新执行结束和写回执行状态
				if item["readOperand"] != "":
					if int(cycle) == int(item["readOperand"]) + self.usingTime[item["instruction"]] :
						item["exeComplet"] = cycle
					if item["exeComplet"] != "" and item["writeResult"]=="":
						if int(cycle) >= int(item["exeComplet"]) + 1:
							release_flag = True
							# 是其他已发射指令的输入数据且该指令未完成数据读取，则不能写
							for unit in funcUTable:
								if unit["Fj"] == item["target"] and unit["Rk"]=="No":
									release_flag = False
								elif unit["Fk"] == item["target"] and unit["Rj"]=="No":
									release_flag = False
							# 写数据的地址是其他未读取数据指令的输入数据，则不能写
							for item2 in self.instructionList:
								if item2["issue"] != "" and item2["readOperand"] != "":
									if item2["j"] == item["target"] or item2["k"] == item["target"]:
										if int(item2["readOperand"]) >= int(cycle) and item2["issue"] != "" and int(item2["issue"])<int(item["issue"]):
											release_flag = False
							# 完成写回操作，指令执行结束，相应地更新表2和表3
							if release_flag:
								item["writeResult"] = cycle
								release_target = item["target"]
								
		# instruction非空则发射instruction
		if name != None:
			for item in self.instructionList:
				if item["instruction"]==instruction and item["target"]==target :
					item["issue"] = cycle
					break
		# 如果更新了writeResult则更新表2表3，释放对应资源
		if release_target != "" :
			# print (release_target)
			return release_target
		else :
			return False

	def change_name(self, name):
		Uname = ""
		if name == "LD" or name == "SD":
			Uname = "Integer"
		elif name == "MULT":
			Uname = "Mult"
		elif name == "SUBD":
			Uname = "Add"
		elif name == "DIVD":
			Uname = "Divide"
		return Uname



class FunctionalUnitTable(object):
	def __init__(self):
		self.funcUnitList = list()
		self.initlist()

	# 初始化表单
	def initlist(self):
		name = ['Integer', 'Mult1', 'Mult2', 'Add', 'Divide']
		for item in name :
			funcUnit = {
				"name" : item,
				"busy" : "No",
				"Op" : "",
				"Fi" : "",
				"Fj" : "",
				"Fk" : "",
				"Qj" : "",
				"Qk" : "",
				"Rj" : "",
				"Rk" : ""
			}
			self.funcUnitList.append(funcUnit)

	def getList(self):
		return self.funcUnitList

	def checkUnit(self, name):
		Uname = ""
		if name == "LD" or name == "SD":
			Uname = "Integer"
		elif name == "MULT":
			Uname = "Mult"
		elif name == "SUBD" or name == "ADDD":
			Uname = "Add"
		elif name == "DIVD":
			Uname = "Divide"
		for item in self.funcUnitList:
			if Uname != "Mult":
				if item["name"] == Uname : 
					if item["busy"] == "No":
						return item["name"]
			else :
				if item["name"] in ["Mult1","Mult2"]:
					if item["busy"] == "No":
						return item["name"]
		return False

	# 添加功能部件的使用
	def launch_ins(self, name, instruction, target, j, k, regTable):
		for item in self.funcUnitList:
			if item["name"] == name:
				item["busy"] = "Yes"
				item["Op"] = instruction
				item["Fi"] = target
				item["Fj"] = j
				item["Fk"] = k
				if "F" in j:
					if regTable[j] != "" :
						item["Qj"] = regTable[j]
						item["Rj"] = "No"
					else :
						item["Rj"] = "Yes"
				else :
					item["Rj"] = "Yes"
				if "F" in k:
					if regTable[k] != "" :
						item["Qk"] = regTable[k]
						item["Rk"] = "No"
					else :
						item["Rk"] = "Yes"
				else :
					item["Rk"] = "Yes"

	def release_ins(self, name):
		for unit in self.funcUnitList:
			if unit["name"] == name:
				unit["busy"] = "No"
				unit["Op"] = ""
				unit["Fi"] = ""
				unit["Fj"] = ""
				unit["Fk"] = ""
				unit["Qj"] = ""
				unit["Qk"] = ""
				unit["Rj"] = ""
				unit["Rk"] = ""
			if unit["Qj"] == name:
				unit["Qj"] = ""
				unit["Rj"] = "Yes"
			if unit["Qk"] == name:
				unit["Qk"] = ""
				unit["Rk"] = "Yes"


class RegisterTable(object):
	def __init__(self):
		self.registerDict = {}
		self.initregister()

	def initregister(self):
		# 课件例题中使用的寄存器并没有达到31个之多，所以在此为了打印信息时方便仅设置12个寄存器
		for i in range(0, 12):
			fname = "F" + str(i)
			self.registerDict[fname] = ""

	def getDict(self):
		return self.registerDict

	def checkF(self,num):
		try:
			if self.registerDict[num] == "":
				return True
			else :
				return False
		except Exception as e:
			print (e)

	def launch_ins(self, name, target):
		self.registerDict[target] = name

	def release_ins(self, target):
		Rname = self.registerDict[target]
		self.registerDict[target] = ""
		return Rname

# 输出当前各表信息
def printInfo(cycle, insTable, funcUTable, registerTable):
	# 周期信息
	print ("Cycle : " + str(cycle))
	# 表1信息
	if insTable != None:
		ins = insTable.getList()
		print ("Instruction status")
		print ("Instruction\tj\tk\tIssue\tRead operand\tExecution complet\tWrite Result")
		for item in ins:
			print (item["instruction"]+"\t"+item["target"]+"\t"+item["j"]+"\t"+item["k"]+"\t"+item["issue"]+"\t"+item["readOperand"]+"\t"+item["exeComplet"]+"\t"+item["writeResult"])
	# 表2信息
	if funcUTable != None:
		func = funcUTable.getList()
		print ("Functional Unit status")
		print ("Name\tBusy\tOp\tFi\tFj\tFk\tQj\tQk\tRj\tRk")
		for item in func:
			print (item["name"]+"\t"+item["busy"]+"\t"+item["Op"]+"\t"+item["Fi"]+"\t"+item["Fj"]+"\t"+item["Fk"]+"\t"+item["Qj"]+"\t"+item["Qk"]+"\t"+item["Rj"]+"\t"+item["Rk"])
	# 表3信息
	if registerTable != None:
		reg = registerTable.getDict()
		print ("Register result status")
		print ("F0\tF1\tF2\tF3\tF4\tF5\t")
		print (reg["F0"]+"\t"+reg["F1"]+"\t"+reg["F2"]+"\t"+reg["F3"]+"\t"+reg["F4"]+"\t"+reg["F5"]+"\t")
		print ("F6\tF7\tF8\tF9\tF10\tF11\t")
		print (reg["F6"]+"\t"+reg["F7"]+"\t"+reg["F8"]+"\t"+reg["F9"]+"\t"+reg["F10"]+"\t"+reg["F11"]+"\t")

# 执行程序至指定周期
def goto_cycle(end_cycle, instructions):
	# insTable对应表Instruction status
	insTable = InstructionStatusTable()
	# funcUTable对应表Functional Unit status
	funcUTable = FunctionalUnitTable()
	# registerTable对应表Register result status
	registerTable = RegisterTable()

	for i in instructions:
		insTable.addInstruction(i)

	allDone = False
	cycle = 0
	
	while (not allDone and cycle < end_cycle):
		cycle += 1
		# 判断下一待发射指令能不能发射
		ins, target, j, k = insTable.getNext()
		U_available = None
		if ins != None:
			# 检查functional unit是否被占用
			U_available = funcUTable.checkUnit(ins)
			# 检查寄存器是否被占用
			F_available = registerTable.checkF(target)
			if U_available and F_available:
				registerTable.launch_ins(U_available, target)
				funcUTable.launch_ins(U_available, ins, target, j, k, registerTable.getDict())
			else :
				U_available = None
		re_target = insTable.fresh(U_available, target, ins, funcUTable.getList(), str(cycle))
		if re_target:
			Rname = registerTable.release_ins(re_target)
			funcUTable.release_ins(Rname)
			
		# 判断是否全部指令执行完毕
		allDone = True
		for item in insTable.getList():
			if item["writeResult"] == "" :
				allDone = False
	printInfo(end_cycle, insTable, funcUTable, registerTable)

if __name__ == '__main__':
	# 获取指令输入
	instructions = ""
	print ("请输入指令，以 ‘-1’结束")
	while 1 :
		inputst = input()
		if inputst != "-1" :
			instructions += inputst + "\n"
		else :
			break
	instruction = re.split('\n',instructions)
	# 输入指令后更新表1
	insTable = InstructionStatusTable()
	for i in instruction[0:-2]:
		insTable.addInstruction(i)
	printInfo(0, insTable, None, None)
	# 根据用户要求执行至相应周期
	inputst = input("请输入跳转周期，输入‘-1’结束程序\n")
	while inputst != '-1':
		goto_cycle(int(inputst), instruction[0:-2])
		inputst = input("请输入跳转周期，输入‘-1’结束程序\n")