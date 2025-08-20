import random

def generateData(size):
    if (isinstance(size, int) and size > 0):
        myList=[]
        for i in range(size):
            myList.append(random.randint(1,100000))
        return myList
    return ValueError

def searchL(list, x):
    i = 0
    while (i < len(list)):
        if (list[i] == x):
            return "El número se encuentra en la posicion " + str(i)
        i+=1
    return "El numero " + str(x) + " no se encuentra en la lista"

def searchB(list, x):
    myList = []
    for i in range (len(list)):
        myList.append(list[i])
    myList.sort()
    i = 0
    j = len(myList)-1
    m = 0 
 
    while (i <= j):
        m = (i + j) // 2
        if (myList[m] == x):
            return "El número se encuentra en la posicion " + str(m)
        elif(x < myList[m]):
            j = m - 1
        else: 
            i = m + 1
    return "El numero " + str(x) + " no se encuentra en la lista"