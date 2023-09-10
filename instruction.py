import functions as func
import variables as var
from typing import Any

_index = 0


def C_int(split_: list[str]) -> list[str]:
	return ["cd", func.zeroExtend(hex(func.toInt(split_[0])))]


def C_def(split_: list[str]) -> list[str]:  # Auto Calculated Size
	if split_[0][0] == ".":
		size = var.sizes[split_[0][1:]]
		split_.pop(0)
	else:
		size = 0
	retu: list[str] = []
	for num in split_:
		num = num.rstrip(",")
		if num[0] == '"':
			retu += [func.zeroExtend(hex(ord(char))) for char in num[1:-1]]
		else:
			tmp = func.convertInt(num)
			tmp2 = func.findSize(tmp)
			if not size:
				size = var.BYTE if num[0] == "'" else tmp2
			elif size < tmp2:
				func.overflowError(size, tmp2, _index)
			retu += func.memoryProc(tmp, size)
	return retu


def _Cjmp_call_mC(split_: list[str], args: tuple[int, bool]) -> list[str]:
	if split_[0][0].isalpha():
		index, size = func.getRegister(split_[0])
		return ([var.STR_BIT_32] if size == var.DWORD else []) + [
			"ff",
			hex(args[0] + index)[2:],
		]
	value, size = (
		(split_[0], var.WORD)
		if len(split_) == 1
		else (split_[1], var.sizes[split_[0][1:]])
	)
	if value == "$":
		size = var.BYTE
	value = func.convertInt(value) - var.addr - 1 - (size >> 1)
	retu_: list[str] = []
	if size == var.DWORD:
		value -= 1
		retu_.append(var.STR_BIT_32)
	tmp = func.findSize(value, forge_signed=True)
	if size < tmp:
		func.overflowError(size, tmp, _index)
	retu_.append("e8" if args[1] else ("eb" if size == var.BYTE else "e9"))
	retu_ += func.memoryProc(value, size)
	return retu_


def C_jmp(split_: list[str]) -> list[str]:  # Size equals Word (16 bit)
	return _Cjmp_call_mC(split_, (0xE0, False))


def C_call(split_: list[str]) -> list[str]:  # Size equals Word (16 bit)
	return _Cjmp_call_mC(split_, (0xD0, True))


def _Cglobal_sC(size: int, bias: int) -> list[str]:
	return ([var.STR_BIT_32] if size == var.DWORD else []) + [
		func.zeroExtend(hex(bias + (size != var.BYTE)))
	]


def _Cglobal_mC(split_: list[str], *args: Any) -> list[str]:
	if len(args) == 1:
		args = args[0]
	if split_[0][0].isalpha():
		index, size = func.getRegister(split_[0])
		return _Cglobal_sC(size, args[1]) + [hex(args[0] + index)[2:]]
	value, size = (
		(split_[0], var.WORD)
		if len(split_) == 1
		else (split_[1], var.sizes[split_[0][1:]])
	)
	return (
		_Cglobal_sC(size, args[1])
		+ [args[2]]
		+ func.memoryProc(func.convertInt(value[1:]), var.WORD)
	)


def C_not(split_: list[str]) -> list[str]:
	return _Cglobal_mC(split_, var.spec_inst["not"])


def C_neg(split_: list[str]) -> list[str]:
	return _Cglobal_mC(split_, var.spec_inst["neg"])


def _Cinc_mC(split_: list[str], bias: int) -> list[str]:
	if split_[0][0].isalpha() and split_[0][1] not in "lh":
		index, size = func.getRegister(split_[0])
		return ([var.STR_BIT_32] if size == var.DWORD else []) + [hex(bias + index)[2:]]
	return _Cglobal_mC(split_, var.spec_inst["inc" if bias == 0x40 else "dec"])


def C_inc(split_: list[str]) -> list[str]:
	return _Cinc_mC(split_, 0x40)


def C_dec(split_: list[str]) -> list[str]:
	return _Cinc_mC(split_, 0x48)


_CONST = 0
_PTR = 1
_REG = 2


def _convertIt(x: str, mod_reg: bool = True) -> tuple[Any, int]:
	if x[0].isalpha():
		return func.getRegister(x, mod_reg), _REG
	if x[0] == "*":
		return func.convertInt(x[1:]), _PTR
	return func.convertInt(x), _CONST


def _Cmov_sC(reg: int, val: int, size: int, bias: int) -> list[str]:
	tmp2 = func.memoryProc(val, var.WORD)
	if reg == 0:
		return _Cglobal_sC(size, 0xA0 + bias) + tmp2
	return (
		_Cglobal_sC(size, 0x8A + bias) + [func.zeroExtend(hex((reg << 3) + 6))] + tmp2
	)


# mov <reg>, <const>
# mov <reg>, <ptr>
# mov <reg>, <reg>
# mov <ptr>, <reg>
# mov <size> <ptr>, <const>
# mov <ptr>, <const> *Auto Calculated Size*
def _Cmov_mC(arg1: str, arg2: str, size: int | None = None) -> list[str]:
	tmp1, tmp2 = _convertIt(arg1, False), _convertIt(arg2)
	val1, val2 = tmp1[0], tmp2[0]
	type = (tmp1[1], tmp2[1])
	del tmp1, tmp2

	retu: list[str] = []
	tmp1 = type[0] == 2

	if tmp1 or type[1] == 2:
		size = val1[1] if tmp1 else val2[1]

	if type == (_REG, _CONST):
		retu.append(hex(0xB0 + val1[0])[2:])
		retu += func.memoryProc(val2, size)  # type: ignore
	else:
		if tmp1:
			tmp = val1[0] % var.REG_INDEX_LEN
		if type == (_REG, _PTR):
			if size == -1:
				return ["8e", func.zeroExtend(hex((tmp << 3) + 6))] + func.memoryProc(val2, var.WORD)  # type: ignore
			return _Cmov_sC(tmp, val2, size, 0)  # type: ignore
		elif type == (_REG, _REG):
			if tmp == val2[0]:  # type: ignore
				func.raiseError(
					"Warning",
					"You are trying to move a register to itself.",
					False,
					_index,
				)
			retu.append("88" if size == var.BYTE else "89")
			retu.append(hex(0xC0 + tmp + (val2[0] << 3))[2:])  # type: ignore
		elif type == (_PTR, _CONST):
			tmp2 = func.findSize(val2)
			if not size:
				size = tmp2
			elif size < tmp2:
				func.overflowError(size, tmp2, _index)
			retu.append("c6" if size == var.BYTE else "c7")
			retu.append("06")
			retu += func.memoryProc(val1, var.WORD)
			retu += func.memoryProc(val2, size)
		elif type == (_PTR, _REG):
			if size == -1:
				return [
					"8c",
					func.zeroExtend(hex((val2[0] << 3) + 6)),
				] + func.memoryProc(val1, var.WORD)
			return _Cmov_sC(val2[0], val1, size, 2)  # type: ignore
	return [var.STR_BIT_32] + retu if size == var.DWORD else retu


# add <a-reg>, <const>
# add <reg>, <const>  # FUCK YEAH BABY I DID IT (Probably i didint)
# add <reg>, <const8>

# add <reg>, <reg>  # Complated


# add <reg>, <ptr>  # Done (%80 i guess)
# add <ptr>, <reg>  # Done (Probably)
# add <ptr>, <const>  # Done
# add <ptr>, <const8> # its wasn't as expected
def _Cadd_mC(arg1: str, arg2: str, size: int | None = None) -> list[str]:
	tmp1, tmp2 = _convertIt(arg1), _convertIt(arg2)
	val1, val2 = tmp1[0], tmp2[0]
	type = (tmp1[1], tmp2[1])
	del tmp1, tmp2

	retu: list[str] = []
	tmp1 = type[0] == 2

	if tmp1 or type[1] == 2:
		size = val1[1] if tmp1 else val2[1]

	if type == (_REG, _CONST):
		if val1[0] == 0:
			return _Cglobal_sC(size, 0x04) + func.memoryProc(val2, size)
		const_size = func.findSize(val2)
		retu.append(
			"83"
			if const_size == var.BYTE and size != var.BYTE
			else ("80" if size == var.BYTE else "81")
		)
		retu.append(hex(0xC0 + val1[0])[2:])
		retu += func.memoryProc(val2, size)
	else:
		if type == (_REG, _PTR):
			if size == -1:
				return
			return (
				_Cglobal_sC(size, 0x02)
				+ [func.zeroExtend(hex((val1[0] << 3) + 6))]
				+ func.memoryProc(val2, var.WORD)
			)
		elif type == (_REG, _REG):
			if tmp == val2[0]:  # type: ignore
				func.raiseError(
					"Warning",
					"You are trying to add a register to itself, you can shift-left instead.",
					False,
					_index,
				)
			retu.append("01" if size == var.BYTE else "00")
			retu.append(hex(0xC0 + val1[0] + (val2[0] << 3))[2:])  # type: ignore
		elif type == (_PTR, _CONST):
			tmp2 = func.findSize(val2)
			if not size:
				size = tmp2
			elif size < tmp2:
				func.overflowError(size, tmp2, _index)
			retu.append("b0" if size == var.BYTE else "b1")
			retu.append("06")
			retu += func.memoryProc(val1, var.WORD)
			retu += func.memoryProc(val2, size)
		elif type == (_PTR, _REG):
			if size == -1:
				return
			return (
				_Cglobal_sC(size, 0x00)
				+ [func.zeroExtend(hex((val1[1] << 3) + 6))]
				+ func.memoryProc(val1, var.WORD)
			)
	return [var.STR_BIT_32] + retu if size == var.DWORD else retu


def C_add(split_: list[str]) -> list[str]:
	if split_[0][0] == ".":
		return _Cadd_mC(split_[1][:-1], split_[2], var.sizes[split_[0][1:]])
	return _Cadd_mC(split_[0][:-1], split_[1])


def C_mov(split_: list[str]) -> list[str]:
	if split_[0][0] == ".":
		return _Cmov_mC(split_[1][:-1], split_[2], var.sizes[split_[0][1:]])
	return _Cmov_mC(split_[0][:-1], split_[1])


_Cpush_segment_values = [  # f(x) = 8x + 6
	["06"],
	["0e"],
	["16"],
	["1e"],
	["0f", "a0"],
	["0f", "a8"],
]

_Cpop_segment_values = [  # f(x) = 8x + 6
	["07"],
	None,
	["17"],
	["1f"],
	["0f", "a1"],
	["0f", "a9"],
]


def _Cpush_mC(
	arg: str, args: tuple[int, str, str], size: int | None = None
) -> list[str] | None:
	retu: list[str] = []
	if arg[0].isalpha():
		index, size = func.getRegister(arg)
		if size == var.BYTE:
			func.raiseError("Push Error", "Cant use 8 bit registers.", line=_index)
			return
		if size == -1:
			if args[0] == 0x50:
				return _Cpush_segment_values[index]
			return _Cpop_segment_values[index]
		retu.append(hex(args[0] + index)[2:])
	elif arg[0] == "*":
		retu.append(args[1])
		retu.append(args[2])
		retu += func.memoryProc(func.convertInt(arg[1:]), var.WORD)
	elif args[2] == "36":
		value = func.convertInt(arg)
		tmp = func.findSize(value)
		if not size:
			size = tmp
		elif size < tmp:
			func.overflowError(size, tmp, _index)
		retu.append("6a" if size == var.BYTE else "68")
		retu += func.memoryProc(value, size)
	else:
		return
	return [var.STR_BIT_32] + retu if size == var.DWORD else retu


def C_push(split_: list[str]) -> list[str] | None:
	if split_[0][0] == ".":
		return _Cpush_mC(split_[1], var.spec_inst["push"], var.sizes[split_[0][1:]])
	return _Cpush_mC(split_[0], var.spec_inst["push"])


def C_pop(split_: list[str]) -> list[str] | None:
	if split_[0][0] == ".":
		return _Cpush_mC(split_[1], var.spec_inst["pop"], var.sizes[split_[0][1:]])
	return _Cpush_mC(split_[0], var.spec_inst["pop"])


_basic_dir = {
	"C_def": C_def,
	"C_jmp": C_jmp,
	"C_not": C_not,
	"C_neg": C_neg,
	"C_inc": C_inc,
	"C_dec": C_dec,
	"C_mov": C_mov,
	"C_push": C_push,
	"C_pop": C_pop,
	"C_int": C_int,
	"C_call": C_call,
	"C_add": C_add,
}

if __name__ == "__main__":
	print(_Cglobal_mC([".x32", "*0x1243"], [0xA0, 0xF0, "03"]))
