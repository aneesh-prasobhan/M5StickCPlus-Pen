# Wireframe_naive.py
import numpy as np
import Quaternion_naive as quat
import Kalman_EKF as km

# Node stores each point of the block
class Node:
    def __init__(self, coordinates, color):
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.z = coordinates[2]
        self.color = color

# Face stores 4 nodes that make up a face of the block
class Face:
    def __init__(self, nodes, color):
        self.nodeIndexes = nodes
        self.color = color

class Edge:
    def __init__(self, start, end):
        self.start = start
        self.end = end

# Wireframe stores the details of a block
class Wireframe:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.faces = []
        self.quaternion = quat.Quaternion()
        self.sys = km.System()

    def addNodes(self, nodeList, colorList):
        for node, color in zip(nodeList, colorList):
            self.nodes.append(Node(node, color))

    def addFaces(self, faceList, colorList):
        for indexes, color in zip(faceList, colorList):
            self.faces.append(Face(indexes, color))

    def quatRotate(self, w, a, m, dt):
        self.sys.predict(w, dt)
        self.sys.update(a, m)
        self.quaternion.q = self.sys.xHat[0:4]
    
    def rotatePoint(self, point):
        rotationMat = km.getRotMat(self.sys.xHat[0:4])
        print(f"Rotation Matrix:\n{rotationMat}")
        rotatedPoint = np.matmul(rotationMat, point)
        print(f"Rotated Point: {rotatedPoint}")
        return rotatedPoint

    def convertToComputerFrame(self, point):
        computerFrameChangeMatrix = np.array([[-1, 0, 0], [0, 0, -1], [0, -1, 0]])
        print(f"Computer Frame Change Matrix:\n{computerFrameChangeMatrix}")
        convertedPoint = np.matmul(computerFrameChangeMatrix, point)
        print(f"Converted Point: {convertedPoint}")
        return convertedPoint

    def getAttitude(self):
        return km.getEulerAngles(self.sys.xHat[0:4])

    def outputNodes(self):
        print("\n --- Nodes --- ")
        for i, node in enumerate(self.nodes):
            print(" %d: (%.2f, %.2f, %.2f) \t Color: (%d, %d, %d)" %
                 (i, node.x, node.y, node.z, node.color[0], node.color[1], node.color[2]))

    def outputFaces(self):
        print("\n --- Faces --- ")
        for i, face in enumerate(self.faces):
            print("Face %d:" % i)
            print("Color: (%d, %d, %d)" % (face.color[0], face.color[1], face.color[2]))
            for nodeIndex in face.nodeIndexes:
                print("\tNode %d" % nodeIndex)
                
    def addEdges(self, edgeList):
        for (start, end) in edgeList:
            self.edges.append(Edge(start, end))
    
    def calculateMidpoint(self, face):
        x = sum(self.nodes[i].x for i in face.nodeIndexes) / 4
        y = sum(self.nodes[i].y for i in face.nodeIndexes) / 4
        z = sum(self.nodes[i].z for i in face.nodeIndexes) / 4
        return (x, y, z)
    
    def setQuaternion(self, q):
        self.quaternion.q = q