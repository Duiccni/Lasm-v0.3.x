import functions as func
import variables as var

index = 0


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
					func.raiseError(
						"Overflow Error",
						f"Used size({c_size}) is smaller than should({tmp2}) be used.",
						line=index,
					)
				size = c_size
			retu += func.memoryProc(tmp, size)
	return retu


def C_jmp(split_: list[str]) -> list[str]:
	return [""]


_basic_dir = {'C_def': C_def, 'C_jmp': C_jmp}