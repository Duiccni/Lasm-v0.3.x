VERSION = "v0.3.1"
AUTHOR = "Egemen Yalın"

# from collections.abc import Callable, Iterable, Mapping
# from os import system
# from threading import Thread
from typing import Any  # , Union
import time

# system("cls")

start_t = time.time()

import variables as var
import functions as func
import instruction as inst

# test_case: list[str] = []
# for _sub in var.test_cases:
# 	test_case += _sub

test_case = var.test_cases[3]

TClen = len(test_case)
_disable = False
index = 0
_times_c_active = False
_times_cooldown = 0

var.settings.mode(24, 24, False, False, False, False, True, True)


def foo(bar: int) -> int:
	if bar == 1:
		return 1
	return foo(bar - 1) * bar


def printOutput(
	case_: str, retu: list[str], args: tuple[int, int, str] | None = None
) -> None:
	if not var.settings.perf_print and (_times_cooldown <= 0 or _times_c_active):
		if args == None:
			args = (index, var.addr)
		else:
			func.raiseError(
				"Line Rewrite",
				f"Function get wanted value({args[2]}) and function rewrited as:",
				False,
				args[0],
			)
		print(
			func.zeroExtend(hex(args[0] % 0x100)) + var.colors.DARK,
			("" if not retu else func.zeroExtend(hex(args[1]), var.WORD))
			+ ("" if _turn else var.colors.ENDL)
			+ "\t",
			case_,
			end=var.colors.ENDL,
		)
		if not retu:
			print()
		else:
			tmp = var.settings.tab_size - len(case_)
			print(
				" " * tmp + var.colors.DARK,
				("" if retu[0] == var.STR_BIT_32 else "   ")
				+ " ".join(retu)
				+ var.colors.ENDL,
			)
			if tmp < 0:
				func.raiseError(
					"Print Breakpoint",
					f"var.settings.tab_size({var.settings.tab_size}, +{-tmp}) not big enough.",
					False,
					args[0],
				)


def runOldWaiter(value: str) -> None:
	for waiter in var.value_waiters:
		if waiter.check(value):
			tmp = waiter.command(waiter.args[0], waiter.args[1], waiter.args[2])
			var.replaceMemory(waiter.start_i, tmp)
			printOutput(
				"(" + test_case[waiter.inst_i] + ")",
				tmp,
				(waiter.inst_i, waiter.start_i + var.orgin, waiter.name),
			)
			del waiter
			break


def procCase(_case: str) -> list[str] | None:
	if _case == "":
		return
	if _case[0] == ";":
		_case = _case[1:]
	global test_case, TClen, _disable, index, _times_cooldown, _times_c_active
	split = func.splitWithoutSpecs(_case)
	command = split[0]
	split.pop(0)

	if not split and command in var.one_inst:
		return var.one_inst[command]

	if var.settings.debug and command[0] == "#":
		match command:
			case "#jmp":
				index += int(split[0], 0)
			case "#set":
				index = int(split[0], 0)
		return

	match command:
		case "org":
			func.raiseError(
				"Command", "'org' can only be used in fist line of code.", False, index
			)
		case "con":
			if split[0] in var.constants:
				func.raiseError(
					"Constant Overwrite",
					f"Is acceptable in this version({VERSION}).",
					False,
					index,
				)
			var.constants[split[0]] = func.convertInt(split[1])
			runOldWaiter(split[0])
		case "flush":
			var.constants.clear()
		case "times":
			tmp = func.convertInt(split[0])
			if tmp < 0:
				func.raiseError(
					"Index Error",
					f"The input of 'times' command cant be negative({tmp}).",
					line=index,
				)
				return
			if not var.settings.show_times:
				_times_c_active = True
				_times_cooldown = tmp
			TClen += tmp
			test_case = (
				test_case[: index + 1]
				+ [_case[len(split[0]) + 7 :]] * tmp
				+ test_case[index + 1 :]
			)
		case _:
			if command[0] == ":":
				command = command[1:]
				if command in var.constants:
					func.raiseError(
						"Constant Overwrite",
						f"Is acceptable in this version({VERSION}).",
						False,
						index,
					)
				var.constants[command] = var.addr
				runOldWaiter(command)
				return
			tmp = "C_" + command
			if tmp in inst._basic_dir:
				return inst._basic_dir[tmp](split)
			else:
				func.raiseError(
					"Command",
					f"'{command}'({'str' if command[0].isalpha() else hex(func.convertInt(command))}) isn't reconized by Assembler.",
					line=index,
				)
	return


if __name__ == "__main__":
	if test_case[0] == "info":
		print(foo(3))
		print(f"LASM Assembler {VERSION} Created by {AUTHOR}")
		exit()

	if test_case[0].startswith("org"):
		print("\t", test_case[0])
		var.addr = func.toInt(test_case[0][4:])
		var.orgin = var.addr
		test_case.pop(0)
		TClen -= 1

	while index < TClen:
		case_ = test_case[index]
		if case_ == "'''":
			print(
				f"{func.zeroExtend(hex(index % 0x100))}\t {var.colors.DARK}'''{var.colors.ENDL}"
			)
			_disable = not _disable
			index += 1
			continue
		if var.settings.skip_times and case_.startswith("times"):
			print(
				f"\t {var.colors.DARK}Skip Times{var.colors.ENDL} {var.colors.ITALIC}(Line {index}{var.colors.ENDL})"
			)
			index += 1
			continue
		inst._index = index
		_turn = _disable or case_.startswith("//")
		retu = None if _turn else procCase(case_)
		printOutput(case_, retu)
		if not var.settings.show_times:
			_times_c_active = False
			_times_cooldown -= 1
		if retu:
			var.addr += len(retu)
			var.memory += retu
		index += 1

	print("\nSize:", len(var.memory))
	print(f"Time(μs): {(time.time() - start_t) * 1_000_000:,.0f}")
	print(
		var.colors.DARK
		+ "\n".join(
			[
				" ".join(
					var.memory[
						i : min(i + var.settings.memory_sub_size, len(var.memory))
					]
				)
				for i in range(0, len(var.memory), var.settings.memory_sub_size)
			]
		)
	)
	print(var.constants, var.colors.ENDL)
