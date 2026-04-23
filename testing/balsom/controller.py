import sys
import time

import cv2
import numpy as np
import pygame
import serial
from PyQt6.QtCore import QObject, QSize, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget

pygame.init()
pygame.joystick.init()


pygame.joystick.Joystick(0)
