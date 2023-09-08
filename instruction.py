import functions as func
import variables as var

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


_basic_dir = {"C_def": C_def, "C_jmp": C_jmp}
