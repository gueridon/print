import math
import pylab
import matplotlib.pyplot as plt



length = 200
freq = 0.025
twopi = 2 * math.pi
arg = twopi * freq

i = 0
x = []
y = []
while i <= length:
    print(i)
    y.insert( i , 32000 * math.cos(i*arg))
    x.append(i)
    i+=1

print(x,y)

# Plot
colors = (0,0,0)
plt.scatter(x, y, c=colors, s=1, alpha=0.5)
plt.title('Scatter plot coswave.py')
plt.xlabel('x')
plt.ylabel('y')
plt.show()
