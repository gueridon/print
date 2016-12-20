series = [1,3,5,7,9]

def listsum(numList):
    if len(numList) == 1:
        return numList[0]
    else:
        print(numList[0] + numList[1:][0], numList[1:])
        return numList[0] + listsum(numList[1:])

print(listsum(series))
