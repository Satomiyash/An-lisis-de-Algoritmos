import math
import random

class Point:
    def __init__(self):
        self.xPos = 0
        self.yPos = 0
        self.name = ""

def generateListOfPoints(num):
    listOfPoints = []
    for i in range(num):
        point = Point()
        point.xPos = random.randint(0,40)
        point.yPos = random.randint(0,40)
        point.name = "P" + str(i+1)
        listOfPoints.append(point)
    return listOfPoints

def calculateDistance(listOfPoints):
    listOfDistances = []
    for i in range(len(listOfPoints)):
        for j in range(i+1, len(listOfPoints)):
            distancePoints = []
            distance = (math.sqrt(((listOfPoints[i].xPos-listOfPoints[j].xPos)**2)+((listOfPoints[i].yPos-listOfPoints[j].yPos)**2)))
            distancePoints.append(distance)
            distancePoints.append(listOfPoints[i].name)
            distancePoints.append(listOfPoints[j].name)
            listOfDistances.append(distancePoints)
    return listOfDistances


def findShortDistance(listOfDistances):
    shortDistance = listOfDistances[0]
    for i in range(1, len(listOfDistances)):
        if shortDistance[0] > listOfDistances[i][0]:
            shortDistance = listOfDistances[i]
    return shortDistance

"""myPoints = generateListOfPoints(5)
print("La lista de puntos y sus respectivas coordenadas: \n")
for i in range(len(myPoints)):
    print(f"{myPoints[i].name} \tx:{myPoints[i].xPos} \ty:{myPoints[i].yPos}")

myDistances = calculateDistance(myPoints)
print("\nLas distancias entre los puntos son: \n")
for i in range(len(myDistances)):
    print(f"{myDistances[i][1]} y {myDistances[i][2]} distancia: {myDistances[i][0]}")

shortDistance = findShortDistance(myDistances)

print(f"\nLa distancia mas corta esta en los puntos {shortDistance[1]} y {shortDistance[2]} distancia: {shortDistance[0]}")"""





        