# BoardDisplay_naive.py
import Wireframe_naive as wf
import pygame
from operator import itemgetter
import readSensor_naive as rs
import Quaternion_naive as quat
import math

class ProjectionViewer:
    """ Displays 3D objects on a Pygame screen """
    def __init__(self, width, height, wireframe, plane, line):
        self.width = width
        self.height = height
        self.wireframe = wireframe
        self.plane = plane
        self.line = line
        self.screen = pygame.display.set_mode((width, height))
        self.write_data = []  # Added this line
        self.isWriting_prev = False  # Added this line
        self.image_surface = None
        
        pygame.display.set_caption('Attitude Determination using Quaternions')
        self.background = (10,10,50)
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 30)

    def run(self, sensorInstance):
        """ Create a pygame screen until it is closed. """
        running = True
        loopRate = 60
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sensorInstance.close()
            self.clock.tick(loopRate)
            data = sensorInstance.getSerialData()
            attitude = [data[6], data[7], data[8]]
            
            isWriting = data[9]

            yaw_rad = math.radians(attitude[0])
            pitch_rad = math.radians(attitude[1])
            roll_rad = math.radians(attitude[2])
            # Update the quaternion based on the attitude data (yaw, pitch, roll)
            self.wireframe.quaternion.q = quat.euler_to_quaternion(yaw_rad, pitch_rad, roll_rad)
            self.display(attitude)
            self.displayPlane()  # Display the fixed orange plane
            self.displayLine(isWriting)  # Display the line
            pygame.display.flip()

    def display(self, attitude):
        """ Draw the wireframes on the screen. """
        self.screen.fill(self.background)

        # Get the current attitude
        # yaw, pitch, roll = self.wireframe.getAttitude()
        yaw, pitch, roll = attitude
        self.messageDisplay("Yaw: %.1f" % yaw,
                            self.screen.get_width()*0.75,
                            self.screen.get_height()*0,
                            (220, 20, 60))      # Crimson
        self.messageDisplay("Pitch: %.1f" % pitch,
                            self.screen.get_width()*0.75,
                            self.screen.get_height()*0.075,
                            (0, 255, 255))     # Cyan
        self.messageDisplay("Roll: %.1f" % roll,
                            self.screen.get_width()*0.75,
                            self.screen.get_height()*0.15,
                            (65, 105, 225))    # Royal Blue

        # Transform nodes to perspective view
        dist = 5
        pvNodes = []
        pvDepth = []
        for node in self.wireframe.nodes:
            point = [node.x, node.y, node.z]
            newCoord = self.wireframe.rotatePoint(point)
            comFrameCoord = self.wireframe.convertToComputerFrame(newCoord)
            pvNodes.append(self.projectOthorgraphic(comFrameCoord[0], comFrameCoord[1], comFrameCoord[2],
                                                    self.screen.get_width(), self.screen.get_height(),
                                                    70, pvDepth))
            """
            pvNodes.append(self.projectOnePointPerspective(comFrameCoord[0], comFrameCoord[1], comFrameCoord[2],
                                                           self.screen.get_width(), self.screen.get_height(),
                                                           5, 10, 30, pvDepth))
            """

        # Calculate the average Z values of each face.
        avg_z = []
        for face in self.wireframe.faces:
            n = pvDepth
            z = (n[face.nodeIndexes[0]] + n[face.nodeIndexes[1]] +
                 n[face.nodeIndexes[2]] + n[face.nodeIndexes[3]]) / 4.0
            avg_z.append(z)
        # Draw the faces using the Painter's algorithm:
        for idx, val in sorted(enumerate(avg_z), key=itemgetter(1)):
            face = self.wireframe.faces[idx]
            pointList = [pvNodes[face.nodeIndexes[0]],
                         pvNodes[face.nodeIndexes[1]],
                         pvNodes[face.nodeIndexes[2]],
                         pvNodes[face.nodeIndexes[3]]]
            pygame.draw.polygon(self.screen, face.color, pointList)
            
        if self.image_surface:  # If there is an image surface, blit it onto the screen
            self.screen.blit(self.image_surface, (0, 0))    

    def displayPlane(self):
        pvNodes = []
        for node in self.plane.nodes:
            point = [node.x, node.y, node.z]
            comFrameCoord = self.wireframe.convertToComputerFrame(point)
            pvNodes.append(self.projectOthorgraphic(comFrameCoord[0], comFrameCoord[1], comFrameCoord[2],
                                                    self.screen.get_width(), self.screen.get_height(),
                                                    70, [node.z]))

        face = self.plane.faces[0]
        pointList = [pvNodes[face.nodeIndexes[0]],
                     pvNodes[face.nodeIndexes[1]],
                     pvNodes[face.nodeIndexes[2]],
                     pvNodes[face.nodeIndexes[3]]]
        pygame.draw.polygon(self.screen, face.color, pointList)

    def displayLine(self, isWriting):
        self.line.setQuaternion(self.wireframe.quaternion.q)
        pvNodes = []
        pvDepth = []
        comFrameCoords = []  # Store 3D coordinates of line points

        for i, node in enumerate(self.line.nodes):
            point = [node.x, node.y, node.z]
            newCoord = self.line.rotatePoint(point)
            comFrameCoord = self.line.convertToComputerFrame(newCoord)
            pvNodes.append(self.projectOthorgraphic(comFrameCoord[0], comFrameCoord[1], comFrameCoord[2],
                                                    self.screen.get_width(), self.screen.get_height(),
                                                    70, pvDepth))

            # Store 3D coordinates for intersection calculations
            comFrameCoords.append(comFrameCoord)

        for edge in self.line.edges:
            pygame.draw.line(self.screen, (255, 255, 255), pvNodes[edge.start], pvNodes[edge.end], 2)


        # Plane equation parameters for y = 6
        y_plane = 6

        # Get the start and end points of the line in 3D space
        P0 = comFrameCoords[0]
        P1 = comFrameCoords[1]
        
        # Check if the line is parallel to the plane
        if P1[1] - P0[1] != 0:  # This avoids the division by zero error
            t = (y_plane - P0[1]) / (P1[1] - P0[1])
            if (0 <= t <= 1) and isWriting:  # This checks if the intersection point is within the line segment
                P_intersect = [P0[i] + t * (P1[i] - P0[i]) for i in range(3)]
                
                print(f'Intersection at x={P_intersect[0]}, y={P_intersect[1]}, z={P_intersect[2]} on the plane')


                # Add the x, z coordinates to the writing data
                self.write_data.append((P_intersect[0], P_intersect[2]))
                
        # If writing has just stopped, create an image using the writing data
        if self.isWriting_prev and not isWriting:
            self.image_surface = self.createImageFromData()  # Store the generated image surface
            self.write_data = []  # Clear the writing data
            
        self.isWriting_prev = isWriting  # Update the isWriting_prev flag

    def createImageFromData(self):
        if not self.write_data:  # If there is no data, do nothing
            return

        # Get the smallest rectangle containing all points
        min_x = min(point[0] for point in self.write_data)
        max_x = max(point[0] for point in self.write_data)
        min_z = min(point[1] for point in self.write_data)
        max_z = max(point[1] for point in self.write_data)
        
        # Scale and translate the points so that they fit in the rectangle
        scale_x = 100 / (max_x - min_x)
        scale_z = 100 / (max_z - min_z)
        translated_and_scaled_data = [(scale_x * (x - min_x), scale_z * (z - min_z)) for x, z in self.write_data]

        # Draw the points on a new Surface
        image_surface = pygame.Surface((100, 100))
        for i in range(len(translated_and_scaled_data) - 1):
            pygame.draw.line(image_surface, (255, 255, 255), translated_and_scaled_data[i], translated_and_scaled_data[i + 1])

        # Draw the Surface at the top-left corner of the screen
        return image_surface
            
    # One vanishing point perspective view algorithm
    def projectOnePointPerspective(self, x, y, z, win_width, win_height, P, S, scaling_constant, pvDepth):
        # In Pygame, the y axis is downward pointing.
        # In order to make y point upwards, a rotation around x axis by 180 degrees is needed.
        # This will result in y' = -y and z' = -z
        xPrime = x
        yPrime = -y
        zPrime = -z
        xProjected = xPrime * (S/(zPrime+P)) * scaling_constant + win_width / 2
        yProjected = yPrime * (S/(zPrime+P)) * scaling_constant + win_height / 2
        pvDepth.append(1/(zPrime+P))
        return (round(xProjected), round(yProjected))

    # Normal Projection
    def projectOthorgraphic(self, x, y, z, win_width, win_height, scaling_constant, pvDepth):
        # In Pygame, the y axis is downward pointing.
        # In order to make y point upwards, a rotation around x axis by 180 degrees is needed.
        # This will result in y' = -y and z' = -z
        xPrime = x
        yPrime = -y
        zPrime = z + 5
        xProjected = xPrime * scaling_constant + win_width / 2
        yProjected = yPrime * scaling_constant + win_height / 2
        # Note that there is no negative sign here because our rotation to computer frame
        # assumes that the computer frame is x-right, y-up, z-out
        # so this z-coordinate below is already in the outward direction
        pvDepth.append(zPrime)
        return (round(xProjected), round(yProjected))

    def messageDisplay(self, text, x, y, color):
        textSurface = self.font.render(text, True, color, self.background)
        textRect = textSurface.get_rect()
        textRect.topleft = (x, y)
        self.screen.blit(textSurface, textRect)

def initializeCube():
    block = wf.Wireframe()

    block_nodes = [(x, y, z) for x in (-1, 1) for y in (-2, 2) for z in (-0.5, 0.5)]

    
    node_colors = [(255, 255, 255)] * len(block_nodes)
    block.addNodes(block_nodes, node_colors)
    block.outputNodes()

    # Magenta, Red, Green, Blue, Cyan, Yellow
    faces = [(0, 2, 6, 4), (0, 1, 3, 2), (1, 3, 7, 5), (4, 5, 7, 6), (2, 3, 7, 6), (0, 1, 5, 4)]
    colors = [(255, 0, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255), (255, 255, 0)]
    block.addFaces(faces, colors)
    block.outputFaces()

    return block

def initializePlane():
    plane = wf.Wireframe()

    plane_nodes = [(x, y, 6) for x in (-10, 10) for y in (-20, 20)]
    plane_colors = [(255, 165, 0)] * len(plane_nodes)  # Light orange color
    plane.addNodes(plane_nodes, plane_colors)

    plane_face = (0, 1, 3, 2)
    plane.addFaces([plane_face], [(255, 165, 0)])  # Light orange color

    return plane

def initializeLine(cuboid):
    line = wf.Wireframe()

    # Calculate the midpoints of the yellow and cyan faces.
    yellow_face = cuboid.faces[5]  # Change these indices to match your yellow and cyan faces.
    cyan_face = cuboid.faces[4]
    yellow_mid = cuboid.calculateMidpoint(yellow_face)
    cyan_mid = cuboid.calculateMidpoint(cyan_face)

    # Calculate the direction of the line.
    direction = (cyan_mid[0] - yellow_mid[0], cyan_mid[1] - yellow_mid[1], cyan_mid[2] - yellow_mid[2])

    # Create two points far enough along the line in both directions from the midpoint.
    factor = 3  # Change this factor to adjust the length of the line.
    line_start = (yellow_mid[0] - factor * direction[0], yellow_mid[1] - factor * direction[1], yellow_mid[2] - factor * direction[2])
    line_end = (cyan_mid[0] + factor * direction[0], cyan_mid[1] + factor * direction[1], cyan_mid[2] + factor * direction[2])

    line_nodes = [line_start, line_end]
    line_colors = [(255, 255, 255)] * len(line_nodes)  # Change this to set the color of the line.
    line.addNodes(line_nodes, line_colors)

    line_edges = [(0, 1)]
    line.addEdges(line_edges)

    return line


if __name__ == '__main__':
    # portName = 'COM4'
    # portName = 'COM6'
    # baudRate = 115200
    dataNumBytes = 2  # number of bytes of 1 data point
    numParams = 10  # number of plots in 1 graph
    s = rs.SerialRead(dataNumBytes=dataNumBytes, numParams=numParams)  # initializes all required variables
    s.readSerialStart()  # starts background thread

    block = initializeCube()
    plane = initializePlane()
    line = initializeLine(block)
    pv = ProjectionViewer(800, 1000, block, plane, line)
    pv.run(s)