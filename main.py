VERSION = "v0.3.0"
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

test_case = var.test_cases[0]

TClen = len(test_case)
_disable = False

var.settings.mode(28, False, False, False)


def foo(bar: int) -> int:
	if bar == 1:
		return 1
	return foo(bar - 1) * bar


def procCase(_case: str) -> list[str] | None:
	global test_case, TClen, _disable
	split = func.splitWithoutSpecs(_case)
	command = split[0]
	split.pop(0)

	if not split and command[0].isalpha() and len(command) == 3:
		return [var.one_inst[command]]

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
				return None
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
				return None
			tmp = "C_" + command
			if tmp in inst._basic_dir:
				return inst._basic_dir[tmp](split)
			else:
				func.raiseError(
					"Command",
					f"'{command}'({'str' if command[0].isalpha() else hex(func.convertInt(command))[2:]}) isn't reconized by Assembler.",
					line=index,
				)
	return None


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

	index = 0
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
		retu = None if _disable else procCase(case_)
		if not var.settings.perf_print:
			print(
				func.zeroExtend(hex(index % 0x100)) + var.colors.DARK,
				("" if not retu else func.zeroExtend(hex(var.addr), var.WORD))
				+ ("" if _disable else var.colors.ENDL)
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
						index,
					)
		if retu:
			var.addr += len(retu)
			var.memory += retu
		index += 1

	print("\nSize:", len(var.memory))
	print(f"Time(μs): {(time.time() - start_t) * 1_000_000:,.0f}")
	print(var.colors.DARK + " ".join(var.memory))
	print(var.constants, var.colors.ENDL)
