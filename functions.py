from typing import Any
import variables as var


def toInt(x: str) -> int:
	"""
	Converts string value to intager value.
	Like int(x) function but specialized for Assembler.
	"""
	if x[0] == "$":
		if len(x) == 1:
			return var.addr
		if x[1] == "$":
			return var.orgin
		return var.spec_values[x[1:]]
	if x[0] == "&":
		return var.constants[x[1:]]
	if x[0] == "?":
		return 0
	if x[0] == "'":
		return ord(x[1])
	if x[0] == "^":
		return 1 << toInt(x[1:])
	return int(x, 0)


def _calculate(x: str) -> int:
	"""
	Calculates input value of string.
	>>> _calculate("3 + 5 - 3")
	5
	"""
	tmp = ""
	retu = 0
	sign = x[0] == "-"
	if sign or x[0] == "+":
		x = x[1:]
	for char in x:
		tmp2 = char == "-"
		if tmp2 or char == "+":
			retu += toInt(tmp) * (-1 if sign else 1)
			tmp = ""
			sign = tmp2
		elif char != " ":
			tmp += char
	return retu + toInt(tmp) * (-1 if sign else 1)


def convertInt(x: str) -> int:
	"""
	This converts string to int like toInt(x) but this is
	checks input is calculateble value or not.
	"""
	if x[0] == "(":
		return _calculate(x[1:-1])
	return toInt(x)


def splitBytes(x: str) -> list[str]:
	"""
	Splits string to 2 character parts.
	"""
	if x.startswith("0x"):
		x = x[2:]
	return [x[i : i + var.BYTE] for i in range(0, len(x), var.BYTE)]


def toHex(x: int, size: int = var.BYTE) -> str:
	"""
	Convert intager value to Hex string even negative values.
	"""
	return hex(x % (1 << (size << 2)))


def raiseError(
	title: str, msg: str, error: bool = True, line: int | None = None
) -> None:
	"""
	Print an error message acording Assembler settings.
	And exit if it is an error.
	"""
	print(
		var.colors.WARNING + title + ":",
		(var.colors.ERROR if error else var.colors.SECOND) + msg + var.colors.ENDL,
		f"{var.colors.ITALIC}(Line {line if line != None else '?'}.){var.colors.ENDL}",
	)
	if error and var.settings.exit_on_errors:
		exit()


def overflowError(size: int, expected: int, index: int) -> None:
	raiseError(
		"Overflow Error",
		f"Used size({size}) is smaller than should({expected}) be used.",
		line=index,
	)


def zeroExtend(x: str, size: int = var.BYTE, notation: bool = False) -> str:
	"""
	Extend string with zeros.
	"""
	if x.startswith("0x"):
		x = x[2:]
	tmp = size - len(x)
	if tmp < 0:
		raiseError(
			"Overflow Error",
			"zeroExtend function found an Negative value.",
		)
		tmp2 = x[-tmp:]
	else:
		tmp2 = "0" * tmp + x
	return "0x" + tmp2 if notation else tmp2


def findSize(
	x: int, stay_align: bool = True, forge_signed: bool = False
) -> int:  # 255, -128, 127
	"""
	Finds size of an value.
	"""
	if not x:
		return var.BYTE
	tmp = 1
	if x < 0:
		x = (-x << 1) - 1
	elif forge_signed:
		x <<= 1
	if x > 0xFFFF_FFFF:
		raiseError(
			"Overflow Error",
			"This Assembler created only for 32 bit and lower.",
		)
	while x:
		x >>= 8
		tmp <<= 1
	return var.DWORD if (tmp == 6 and stay_align) else tmp


_excluded = "_"


def splitWithoutSpecs(x: str) -> list[str]:
	retu: list[str] = []
	tmp = ""
	include = True
	for char in x:
		if char in '"()':
			include = not include
			tmp += char
		elif char == " " and include:
			if tmp != "":
				retu.append(tmp)
				tmp = ""
		elif char != _excluded:
			tmp += char
	retu.append(tmp)
	return retu


# $, $$, $<const>, (<n1> <+ | -> <n2>...),
# 0x<hex>, <decimal>, 0b<bin>, ?, &<name>, '<char>'
# process(v, s, n)	-> zeroExtend(toHex(v, s), s, n)
# memProc(v, s)		-> reverse(splitBytes(process(v, s, False)))
def memoryProc(x: int, size: int) -> list[str]:
	tmp = splitBytes(zeroExtend(toHex(x, size), size, False))
	tmp.reverse()
	return tmp


def getRegister(x: str, mod: bool = True) -> tuple[int, int]:
	"""
	Returns Register values -> (index, size).
	>>> getRegister("eax")
	(0, var.DWORD)
	>>> getRegister("ds")  # Segment Register
	(2, -1)
	"""

	if x in var.seg_regs:
		return (var.seg_regs.index(x), -1)

	tmp = var.str_regs.index(x[-2:])
	return (
		tmp % var.REG_INDEX_LEN if mod else tmp,
		var.DWORD
		if len(x) == 3
		else (var.BYTE if tmp < var.REG_INDEX_LEN else var.WORD),
	)


if __name__ == "__main__":  # Test functions.
	var.orgin = 0x10
	var.addr = 0x20

	print(f"{var.colors.DARK}toInt\t\t\t{var.colors.ENDL}", toInt("0x7c00"))
	print(f"{var.colors.DARK}_calculate\t\t{var.colors.ENDL}", _calculate("3- 4 + 6"))
	print(
		f"{var.colors.DARK}convertInt\t\t{var.colors.ENDL}", convertInt("(20 - $ + $$)")
	)
	print(f"{var.colors.DARK}splitBytes\t\t{var.colors.ENDL}", splitBytes("012345"))
	print(
		f"{var.colors.DARK}zeroExtend\t\t{var.colors.ENDL}",
		zeroExtend("0x32", var.DWORD, False),
	)
	print(
		f"{var.colors.DARK}zeroExtend\t\t{var.colors.ENDL}",
		zeroExtend("0x3210ab", var.WORD, True),
	)
	print(f"{var.colors.DARK}toHex\t\t\t{var.colors.ENDL}", toHex(-1))
	print(f"{var.colors.DARK}findSize\t\t{var.colors.ENDL}", findSize(-192))
	print(
		f"{var.colors.DARK}splitWithoutSpecs\t{var.colors.ENDL}",
		splitWithoutSpecs('"a b c" a b c (4 + 3)'),
	)
	print(
		f"{var.colors.DARK}memoryProc\t\t{var.colors.ENDL}", memoryProc(100, var.WORD)
	)
	print(f"{var.colors.DARK}getRegister\t\t{var.colors.ENDL}", getRegister("si"))

	raiseError("Exit Error", "Hello, world! (This is an test error.)", line=None)
