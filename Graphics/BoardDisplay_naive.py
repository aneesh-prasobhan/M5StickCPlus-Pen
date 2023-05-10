# BoardDisplay_naive.py
import Wireframe_naive as wf
import pygame
from operator import itemgetter
import readSensor_naive as rs
import Quaternion_naive as quat
import math

import os
from PIL import Image, ImageDraw
from io import BytesIO

class ProjectionViewer:
    """ Displays 3D objects on a Pygame screen """
    def __init__(self, width, height, wireframe):
        self.width = width
        self.height = height
        self.wireframe = wireframe
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Attitude Determination using Quaternions')
        self.background = (10,10,50)
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.xy_plane = self.create_xy_plane(300, 300, 2)
        self.intersection_points = []


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
            yaw_rad = math.radians(attitude[0])
            pitch_rad = math.radians(attitude[1])
            roll_rad = math.radians(attitude[2])
            # Update the quaternion based on the attitude data (yaw, pitch, roll)
            self.wireframe.quaternion.q = quat.euler_to_quaternion(yaw_rad, pitch_rad, roll_rad)
            self.display(attitude)
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

        # Calculate the intersection point
        axis_start_node = self.wireframe.nodes[-2]
        axis_end_node = self.wireframe.nodes[-1]
        new_start_coord = self.wireframe.rotatePoint([axis_start_node.x, axis_start_node.y, axis_start_node.z])
        new_end_coord = self.wireframe.rotatePoint([axis_end_node.x, axis_end_node.y, axis_end_node.z])

        intersection_point = self.find_intersection_point(new_start_coord, new_end_coord, -4)
        if intersection_point is not None:
            self.intersection_points.append(intersection_point)

        # Create the image from the intersection points and display it on the screen
        image = create_image_from_coordinates(self.intersection_points)
        image_width, image_height = image.size
        pygame_surface = pygame.image.frombuffer(image.tobytes(), (image_width, image_height), 'RGB')
        self.screen.blit(pygame_surface, (0, 0))
        
    
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
        xProjected = xPrime * scaling_constant + win_width / 2
        yProjected = yPrime * scaling_constant + win_height / 2
        # Note that there is no negative sign here because our rotation to computer frame
        # assumes that the computer frame is x-right, y-up, z-out
        # so this z-coordinate below is already in the outward direction
        pvDepth.append(z)
        return (round(xProjected), round(yProjected))

    def messageDisplay(self, text, x, y, color):
        textSurface = self.font.render(text, True, color, self.background)
        textRect = textSurface.get_rect()
        textRect.topleft = (x, y)
        self.screen.blit(textSurface, textRect)
        
    def create_xy_plane(self, width, height, distance):
        nodes = [(x, y, -distance) for x in (-width/2, width/2) for y in (-height/2, height/2)]
        faces = [(0, 1, 3, 2)]
        colors = [(200, 200, 200)]
        plane = wf.Wireframe()
        plane.addNodes(nodes, colors)
        plane.addFaces(faces, colors)
        return plane

    def find_intersection_point(self, p1, p2, z_plane):
        if p1[2] == p2[2]:
            return None
        t = (z_plane - p1[2]) / (p2[2] - p1[2])
        x = p1[0] + t * (p2[0] - p1[0])
        y = p1[1] + t * (p2[1] - p1[1])
        return (x, y)


def initializeCube():
    block = wf.Wireframe()

    block_nodes = [(x, y, z) for x in (-1, 1) for y in (-2, 2) for z in (-0.5, 0.5)]
    node_colors = [(255, 255, 255)] * len(block_nodes)
    block.addNodes(block_nodes, node_colors)
    block.outputNodes()

    faces = [(0, 2, 6, 4), (0, 1, 3, 2), (1, 3, 7, 5), (4, 5, 7, 6), (2, 3, 7, 6), (0, 1, 5, 4)]
    colors = [(255, 0, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255), (255, 255, 0)]
    block.addFaces(faces, colors)
    block.outputFaces()

    return block

# Function to create image from coordinates
def create_image_from_coordinates(coordinates, image_size=(300, 300), line_width=3):
    image = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(image)
    draw.line(coordinates, fill="black", width=line_width)
    return image


if __name__ == '__main__':
    # portName = 'COM4'
    # portName = 'COM6'
    # baudRate = 115200
    dataNumBytes = 2  # number of bytes of 1 data point
    numParams = 9  # number of plots in 1 graph
    s = rs.SerialRead(dataNumBytes=dataNumBytes, numParams=numParams)  # initializes all required variables
    s.readSerialStart()  # starts background thread

    block = initializeCube()
    pv = ProjectionViewer(640, 480, block)
    pv.run(s)