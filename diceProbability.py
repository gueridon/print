import random

die_faces = [1,2,3,4,5,6]

rolls = 0
Pn = 0
while rolls < 1000000:
    rolls += 1
    roled_face = random.choice(die_faces)
    if roled_face == 3:
        Pn += 1


print(Pn/rolls)
