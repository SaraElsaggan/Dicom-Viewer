from PyQt5.QtWidgets import  QApplication, QMainWindow, QShortcut, QFileDialog , QSplitter , QFrame , QSlider
import sys
from PyQt5.QtGui import QIcon, QKeySequence
from mainwindow import Ui_MainWindow  
import numpy as np
import pandas as pd
from scipy.io import wavfile
import pyqtgraph as pg
from scipy.fftpack import rfft, rfftfreq, irfft , fft , fftfreq
from PyQt5.QtCore import pyqtSlot
# from PyQt5.QtOpenGL import QOpenGLWidget

from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel
from vtkmodules.util.numpy_support import vtk_to_numpy
import pydicom
import numpy as np
# from PyQt5.QtOpenGL import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLUT import *


 
class MyWindow(QMainWindow):   
    
    def __init__(self ):
        super(MyWindow , self).__init__()
      
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  

        
        self.vtk_widget = QVTKRenderWindowInteractor(self.ui.openGLWidget)
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.vtk_widget.Initialize()
    
            
        self.image_data = np.array([])
        self.image_position = np.array([])
        self.pixel_spacing = np.array([])
        self.surface_actor = None
    
        # some shortcuts
        QShortcut(QKeySequence("Ctrl+o"), self).activated.connect(self.load_file)
        

    def load_file(self):
        # Open a dialog to select a DICOM series directory
        Directory = QFileDialog.getExistingDirectory(self, "Open DICOM Series Directory", "", options=QFileDialog.Options())
        if Directory:
            # Load and render the DICOM series
            self.load_dicom_series(Directory)

    # Function to load and render a DICOM series
    def load_dicom_series(self, directory):
        # Clear previous rendering
        if self.surface_actor:
            self.renderer.RemoveActor(self.surface_actor)
        self.renderer.RemoveAllViewProps()

        # Read DICOM files in a series using VTK DICOM reader
        dicom_reader = vtk.vtkDICOMImageReader()
        dicom_reader.SetDirectoryName(directory)
        dicom_reader.Update()
        self.image_data = dicom_reader.GetOutput()

        # Set up and render the surface representation of the DICOM data
        self.setup_surface_rendering()
        self.vtk_widget.GetRenderWindow().Render()

    # Function to set up surface rendering using marching cubes
    def setup_surface_rendering(self):
        # Apply marching cubes algorithm to create a surface representation
        marching_cubes = vtk.vtkMarchingCubes()
        marching_cubes.SetInputData(self.image_data)
        marching_cubes.SetValue(0, 0)
        
        # Create a mapper and actor for the surface representation
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(marching_cubes.GetOutputPort())
        self.surface_actor = vtk.vtkActor()
        self.surface_actor.SetMapper(mapper)
        
        # Add the surface actor to the renderer and adjust the camera
        self.renderer.AddActor(self.surface_actor)
        self.renderer.ResetCamera()
        
        # Update the rendering window
        self.vtk_widget.GetRenderWindow().Render()

    # Function to handle surface rendering checkbox state change
    def surface_rendering(self):
        if self.ui.radioButton_3.isChecked():
            # Clear previous rendering and set up surface rendering
            self.renderer.RemoveAllViewProps()
            self.setup_surface_rendering()
            self.vtk_widget.GetRenderWindow().Render()

 
    # Function to handle surface rendering checkbox state 

 

def main():
    app = QApplication(sys.argv)
    window = MyWindow() 
   
   
    window.showMaximized()
    window.show()
    
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()