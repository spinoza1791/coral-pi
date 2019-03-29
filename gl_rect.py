# sudo apt-get install python3-pyqt4
# sudo apt-get install python3-pyqt4.qtopengl
from PyQt4.QtCore import * # QTimer  
from PyQt4.QtGui import * # QApplication  
from PyQt4.QtOpenGL import * # QGLWidget  
from OpenGL.GL import * # OpenGL functionality  
from OpenGL.GL import shaders # Utilities to compile shaders, we may not actually use this  
  
class OpenGLView(QGLWidget):  
    def initializeGL(self):  
        # set the RGBA values of the background  
        glClearColor(0.1, 0.2, 0.3, 1.0)  
        # set a timer to redraw every 1/60th of a second  
        self.__timer = QTimer()  
        self.__timer.timeout.connect(self.repaint) # make it repaint when triggered  
        self.__timer.start(1000 / 60) # make it trigger every 1000/60 milliseconds  
     
    def resizeGL(self, width, height):  
        # this tells openGL how many pixels it should be drawing into  
        glViewport(0, 0, width, height)  
     
    def paintGL(self):  
        # empty the screen, setting only the background color  
        # the depth_buffer_bit also clears the Z-buffer, which is used to make sure  
        # objects that are behind other objects actually are not shown drawing   
        # a faraway object later than a nearby object naively implies that it will   
        # just fill in the pixels with itself, but if there is already an object there   
        # the depth buffer will handle checking if it is closer or not automatically  
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  
        # the openGL window has coordinates from (-1,-1) to (1,1), so this fills in   
        # the top right corner with a rectangle. The default color is white.  
        glRecti(0, 0, 1, 1)  


# this initializes Qt  
app = QApplication([])  
# this creates the openGL window, but it isn't initialized yet  
window = OpenGLView()  
# this only schedules the window to be shown on the next Qt update  
window.show()  
# this starts the Qt main update loop, it avoids python from continuing beyond this  
# line and any Qt stuff we did above is now going to actually get executed, along with  
# any future events like mouse clicks and window resizes  
app.exec_()  
