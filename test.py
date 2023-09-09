@staticmethod
def foo(arg: float) -> float:
    x2 = arg + 3.4
    return -(20 / x2 / x2) + 2 + arg / 8

for i in range(20):
    print(i / 5, foo(i / 5))