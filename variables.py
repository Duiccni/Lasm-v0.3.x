from typing import Any


class settings:
	"""
	Assembler settings like exit_on_errors.
	"""

	tab_size = 20
	exit_on_errors = False
	perf_print = False
	skip_times = False

	def mode(*args: Any) -> None:
		"""
		Change assembler settings.
		"""

		settings.tab_size = args[0]
		settings.exit_on_errors = args[1]
		settings.perf_print = args[2]
		settings.skip_times = args[3]


class colors:
	"""
	Unicode color codes in a class.
	"""

	ITALIC = "\033[3m"
	DARK = "\033[30m"
	SECOND = "\033[34m"
	ERROR = "\033[31m"
	WARNING = "\033[93m"
	ENDL = "\033[0m"


BYTE = 2
WORD = 4
DWORD = 8

sizes = {
	"byte": BYTE,
	"word": WORD,
	"dword": DWORD,
	"x8": BYTE,
	"x16": WORD,
	"x32": DWORD,
	"short": BYTE,
	"long": DWORD,
}

constants: dict[str, int] = {}
addr = 0
orgin = 0

# BIT_32 = 0x66
STR_BIT_32 = "66"

regs8 = ["al", "cl", "dl", "bl", "ah", "ch", "dh", "bh"]
regs16_32 = ["ax", "cx", "dx", "bx", "sp", "bp", "si", "di"]
seg_regs = ["cs", "ss", "ds", "es", "fs", "gs"]

str_regs = regs8 + regs16_32

# REGS_LEN = 16
REG_INDEX_LEN = 8

one_inst = {
	"hlt": "f4",
	"nop": "90",
	"cmc": "f5",
	"clc": "f8",
	"stc": "f9",
	"cli": "fa",
	"sti": "fb",
	"cld": "fc",
	"std": "fd",
}

spec_inst = {
	"not": (0xD0, 0xF6, "16"),
	"neg": (0xD8, 0xF6, "1e"),
	"inc": (0xC0, 0xFE, "06"),
	"dec": (0xC8, 0xFE, "0e"),
}

spec_values = {
	"mbr": 0x55AA,
	"borg": 0x7C00,
}

added: list[str] = []
memory: list[str] = []

_splitter = "---"


def _split_list(list_: list[str], sep: str = _splitter) -> list[list[str]]:
	retu: list[list[str]] = []
	tmp: list[str] = []
	for i in list_:
		i = i.strip()
		if i == sep:
			retu.append(tmp.copy())
			tmp.clear()
		else:
			tmp.append(i)
	retu.append(tmp)
	del tmp
	return retu


test_cases_file = open("test_cases.txt")
test_cases = (
	_split_list(test_cases_file.readlines())
	+ [
		# not <reg>
		["not " + i for i in str_regs]
		+ ["not e" + i for i in str_regs]
		# not *<ptr>, not .<size> *<ptr>
		+ ["not *0x4321", "not .byte *0x4321"]
	]
	+ [
		# mov <reg>, <const>
		[f"mov {i}, 0x45" for i in regs8]
		+ [f"mov {i}, 0x4321" for i in regs16_32]
		+ [f"mov e{i}, 0x4321_abcd" for i in regs16_32]
		# mov <reg>, <reg>
		+ [f"mov {i}, {k}" for i in regs8 for k in regs8]
		+ [f"mov {i}, {k}" for i in regs16_32 for k in regs16_32]
		+ [f"mov e{i}, e{k}" for i in regs16_32 for k in regs16_32]
		# mov <reg>, *<ptr>
		+ [f"mov {i}, *0x45ab" for i in regs8]
		+ [f"mov {i}, *0x4321" for i in regs16_32]
		+ [f"mov e{i}, *0x4a2f" for i in regs16_32]
		# mov *<ptr>, <reg>
		+ [f"mov *0x45ab, {i}" for i in regs8]
		+ [f"mov *0x4321, {i}" for i in regs16_32]
		+ [f"mov *0x4a2f, e{i}" for i in regs16_32]
		# mov *<ptr>, <const> -> *Auto Calculated Size.*
		# mov .<size> *<ptr>, <const>
		+ [
			"mov byte *0x1234, 0x10",
			"mov *0x1234, 0x1000",  # Size = WORD (16 bit)
			"mov dword *0x1234 0x10000",  # Size = DWORD (32 bit)
		]
	]
)
test_cases_file.close()

if __name__ == "__main__":
	print("\n\n".join(["\n".join(i) for i in test_cases]))
	input()
	for i in range(100):
		print(f"\033[{i}m{i} abc{colors.ENDL}")
