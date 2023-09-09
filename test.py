a = 1
b = 2
c = 3

x = b
y = c

match (x, y):
    case (c, b):
        print(x, y, a, b)
        print(b)
        print(c)
    case (b, ):
        print(x, y, b, b)
    case (b, c):
        print(x, y, c, b)