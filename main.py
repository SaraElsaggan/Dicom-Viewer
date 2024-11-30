from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QFileDialog
from PyQt5.QtGui import QKeySequence
from mainwindow import Ui_MainWindow  # Ensure this is your generated UI file
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
import pydicom
import os


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()

        # Setup the UI and VTK renderer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialize VTK render window
        self.vtk_widget = QVTKRenderWindowInteractor(self.ui.widget)
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.vtk_widget.Initialize()

        # Add shortcut for loading files
        QShortcut(QKeySequence("Ctrl+o"), self).activated.connect(self.load_file)

    def load_file(self):
        """Load a folder of DICOM files and display it in 3D."""
        folder = QFileDialog.getExistingDirectory(self, "Select DICOM Folder")
        if not folder:
            return

        # Load all DICOM files in the folder
        reader = vtk.vtkDICOMImageReader()
        reader.SetDirectoryName(folder)
        reader.Update()

        # Extract volume data from the reader
        volume = vtk.vtkImageData()
        volume.DeepCopy(reader.GetOutput())

        # Create a volume mapper
        volume_mapper = vtk.vtkGPUVolumeRayCastMapper()
        volume_mapper.SetInputData(volume)

        # Create a volume property
        volume_property = vtk.vtkVolumeProperty()
        volume_property.ShadeOn()
        volume_property.SetInterpolationTypeToLinear()

        # Set up transfer functions for color and opacity
        color_func = vtk.vtkColorTransferFunction()
        color_func.AddRGBPoint(0, 0.0, 0.0, 0.0)
        color_func.AddRGBPoint(500, 1.0, 0.5, 0.3)
        color_func.AddRGBPoint(1000, 1.0, 1.0, 0.9)
        color_func.AddRGBPoint(1150, 1.0, 1.0, 1.0)

        opacity_func = vtk.vtkPiecewiseFunction()
        opacity_func.AddPoint(0, 0.0)
        opacity_func.AddPoint(500, 0.2)
        opacity_func.AddPoint(1000, 0.4)
        opacity_func.AddPoint(1150, 0.8)

        volume_property.SetColor(color_func)
        volume_property.SetScalarOpacity(opacity_func)

        # Create the volume
        volume_actor = vtk.vtkVolume()
        volume_actor.SetMapper(volume_mapper)
        volume_actor.SetProperty(volume_property)

        # Add the volume to the renderer
        self.renderer.AddVolume(volume_actor)
        self.renderer.SetBackground(0.1, 0.1, 0.1)  # Set background color
        self.renderer.ResetCamera()

        # Render the scene
        self.vtk_widget.GetRenderWindow().Render()


def main():
    app = QApplication([])
    window = MyWindow()
    window.showMaximized()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
