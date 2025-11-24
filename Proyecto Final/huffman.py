class Node:
    def __init__(self, value, character):
        self.value = value
        self.character = character
        self.left = None
        self.right = None
        self.key = None
        self.keyLength = None

def insertOrdered(node, list):
    for i in range(len(list)):
        if node.value < list[i].value:
            list.insert(i, node)
            return list
    list.append(node)  
    return list


def createTree(nodeList):
    while (len(nodeList)>1):
        root = Node(value=(nodeList[0].value+nodeList[1].value), character=None)
        root.left = nodeList[0]
        root.right = nodeList[1]
        nodeList.pop(0)
        nodeList.pop(0)
        createTree(insertOrdered(root, nodeList))
    return nodeList[0]

def decodeByChar(route):

    with open(route, "r", encoding="utf-8") as archive:
        text = archive.read()

    nodeList = []
    counter = {}

    for character in text:
        if character in counter:
            counter[character] += 1
        else:
            counter[character] = 1

    for letter, times in counter.items():
        nodeList.append(Node(value=times, character=letter))

    nodeList.sort(key=lambda n: n.value)
    return nodeList

def createKeys(root, key=0, length=0):
    if root is None:
        return
    root.key = key
    root.keyLength = length
    createKeys(root.left,  key << 1,     length + 1)
    createKeys(root.right, (key << 1) | 1, length + 1)
    return root

def createKeyList(root, keyList=[]):
    if root is None:
        return
    if root.character is not None:
        keyList.append(root)
    createKeyList(root.left, keyList)
    createKeyList(root.right, keyList)

    return keyList

'''def fillDict(node, codes=None):
    if codes is None:
        codes = {}

    if node is None:
        return codes

    if node.character is not None:  
        key, length = node.key
        binary = format(key, f'0{length}b')  
        codes[node.character] = binary

    fillDict(node.left, codes)
    fillDict(node.right, codes)
    return codes'''

def concatenate(route, keyList):
    myString = ""
    with open(route, "r", encoding="utf-8") as archive:
        text = archive.read()

    codeMap = {}
    for node in keyList:
        codeMap[node.character] = (node.key, node.keyLength)

    for character in text:
        code, length = codeMap[character]
        myString += format(code, f'0{length}b')

    return myString

def createCompressed(archive, route):
    nodeList = decodeByChar(archive)
    myTree = createTree(nodeList)
    myCodesTree = createKeys(myTree)
    myCodes = createKeyList(myCodesTree)
    myString = concatenate(archive, myCodes)

    length = len(myString)
    while len(myString) % 8 != 0:
        myString += "0"
    byteData = int(myString, 2).to_bytes(len(myString)//8, "big")

    with open(route, "wb") as f:
        f.write(length.to_bytes(4, "big"))  
        f.write(byteData) 
    return myCodes    

def descompressed(route):
    with open(route, "rb") as f:
        length = int.from_bytes(f.read(4), "big")
        data = f.read()

    bits = bin(int.from_bytes(data, "big"))[2:].zfill(len(data)*8)
    bits = bits[:length] 
    return bits
    #print(bits) 

def decode(archive, keyList, route):
    myString = descompressed(archive)
    # invertir diccionario
    codeMap = {}
    for node in keyList:
        codeMap[node.character] = format(node.key, f'0{node.keyLength}b')
    
    #print(codeMap)

    reverse = {code: char for char, code in codeMap.items()}
    
    current = ""
    decoded = ""

    for bit in myString:
        current += bit
        if current in reverse:
            decoded += reverse[current]
            current = ""   # reiniciar para seguir
        #print(decoded)
        #input("")

    with open(route, "w", encoding="utf-8") as f:
        f.write(decoded)







        