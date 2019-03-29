# import the necessary modules  
from PyQt4.QtCore import * # QTimer  
from PyQt4.QtGui import * # QApplication  
from PyQt4.QtOpenGL import * # QGLWidget  
from OpenGL.GL import * # OpenGL functionality  
from OpenGL.GL import shaders # Utilities to compile shaders, we may not actually use this  
  
# this is the basic window  
class OpenGLView(QGLWidget):
     def initializeGL(self):  
          print("Initializing")
     def resizeGL(self, width, height):
          print("Resizing")
     def paintGL(self):  
          print("Painting")  
  
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
