import functions as func
import variables as var
from typing import Any

_index = 0


def C_def(split_: list[str]) -> list[str]:  # Auto Calculated Size
	if split_[0][0] == ".":
		c_size = var.sizes[split_[0][1:]]
		split_.pop(0)
	else:
		c_size = 0
	retu: list[str] = []
	for num in split_:
		num = num.rstrip(",")
		if num[0] == '"':
			retu += [func.zeroExtend(hex(ord(char))) for char in num[1:-1]]
		else:
			tmp = func.convertInt(num)
			tmp2 = func.findSize(tmp)
			if not c_size:
				size = var.BYTE if num[0] == "'" else tmp2
			else:
				if c_size < tmp2:
					func.overflowError(c_size, tmp2, _index)
				size = c_size
			retu += func.memoryProc(tmp, size)
	return retu


def C_jmp(split_: list[str]) -> list[str]:  # Size equals Word (16 bit)
	if split_[0][0].isalpha():
		index, size = func.getRegister(split_[0])
		return ([var.STR_BIT_32] if size == var.DWORD else []) + [
			"ff",
			hex(0xE0 + index)[2:],
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
	tmp = func.findSize(value, True, True)
	if size < tmp:
		func.overflowError(size, tmp, _index)
	retu_.append("eb" if size == var.BYTE else "e9")
	retu_ += func.memoryProc(value, size)
	return retu_


def _Cglobal_sC(size: int, bias: int) -> list[str]:
	return ([var.STR_BIT_32] if size == var.DWORD else []) + [
		hex(bias + (size != var.BYTE))[2:]
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
	if split_[0][0] == "." or split_[0][0].isdigit():
		return _Cglobal_mC(split_, var.spec_inst["inc"])
	index, size = func.getRegister(split_[0])
	return ([var.STR_BIT_32] if size == var.DWORD else []) + [hex(bias + index)[2:]]


def C_inc(split_: list[str]) -> list[str]:
	return _Cinc_mC(split_, 0x40)


def C_dec(split_: list[str]) -> list[str]:
	return _Cinc_mC(split_, 0x48)


def C_mov(split_: list[str]) -> list[str]:
	if split_[0][0] == ".":
		return [""]
	return [""]

def C_push(split_: list[str]) -> list[str]:
	if split_[0][0] == ".":
		return [""]
	return [""]

def C_pop(split_: list[str]) -> list[str]:
	if split_[0][0] == ".":
		return [""]
	return [""]


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
}

if __name__ == "__main__":
	print(_Cglobal_mC([".x32", "*0x1243"], [0xA0, 0xF0, "03"]))
