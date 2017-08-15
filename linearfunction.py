

def linearfunction(xa, ya, xb, yb , x):
    m = (ya - yb)/(xa - xb)
    y = (m * x) - (m * xa) + ya
    return y


print(linearfunction(1,5,10,10, 3))
