from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QFileDialog , QVBoxLayout
from PyQt5.QtGui import QKeySequence
from mainwindow import Ui_MainWindow  # Ensure this is your generated UI file
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
import pydicom
import os

class Visualizer:
    def __init__(
        self,
        folder,
        mode,
        ambient=0.1,
        diffuse=0.9,
        specular=0.2,
        specular_power=10.0,
        isovalue=500,
        color=(0.0, 0.0, 1.0),
    ):
        self.folder = folder
        self.mode = mode
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.specular_power = specular_power
        self.isovalue = isovalue
        self.reader = vtk.vtkDICOMImageReader()
        self.color = color
        
        self.reader = vtk.vtkDICOMImageReader()
        self.reader.SetDirectoryName(folder)
        self.reader.Update()

    def read_data(self):
        # Read DICOM data
        self.reader.SetDirectoryName(self.folder)
        self.reader.Update()

    def raycast_rendering(self):
        # Create volume mapper
        volume_mapper = vtk.vtkSmartVolumeMapper()
        volume_mapper.SetBlendModeToComposite()
        volume_mapper.SetRequestedRenderModeToGPU()
        volume_mapper.SetInputData(self.reader.GetOutput())

        # Create volume property
        volume_property = vtk.vtkVolumeProperty()
        volume_property.ShadeOn()
        volume_property.SetInterpolationTypeToLinear()
        volume_property.SetAmbient(self.ambient)
        volume_property.SetDiffuse(self.diffuse)
        volume_property.SetSpecular(self.specular)
        volume_property.SetSpecularPower(self.specular_power)

        # Set gradient opacity
        gradient_opacity = vtk.vtkPiecewiseFunction()
        gradient_opacity.AddPoint(0.0, 0.0)
        gradient_opacity.AddPoint(2000.0, 1.0)
        volume_property.SetGradientOpacity(gradient_opacity)

        # Set scalar opacity
        scalar_opacity = vtk.vtkPiecewiseFunction()
        scalar_opacity.AddPoint(-800.0, 0.0)
        scalar_opacity.AddPoint(-750.0, 1.0)
        scalar_opacity.AddPoint(-350.0, 1.0)
        scalar_opacity.AddPoint(-300.0, 0.0)
        scalar_opacity.AddPoint(-200.0, 0.0)
        scalar_opacity.AddPoint(-100.0, 1.0)
        scalar_opacity.AddPoint(1000.0, 0.0)
        scalar_opacity.AddPoint(2750.0, 0.0)
        scalar_opacity.AddPoint(2976.0, 1.0)
        scalar_opacity.AddPoint(3000.0, 0.0)
        volume_property.SetScalarOpacity(scalar_opacity)

        # Set color transfer function
        color = vtk.vtkColorTransferFunction()
        color.AddRGBPoint(-750.0, *self.color)
        color.AddRGBPoint(-350.0, *self.color)
        color.AddRGBPoint(-200.0, *self.color)
        color.AddRGBPoint(2750.0, *self.color)
        color.AddRGBPoint(3000.0, *self.color)
        volume_property.SetColor(color)

        # Create volume
        volume = vtk.vtkVolume()
        volume.SetMapper(volume_mapper)
        volume.SetProperty(volume_property)

        # Return volume
        return volume

    def surface_rendering(self):
        # Create surface extraction filter (marching cubes)
        surface_extractor = vtk.vtkMarchingCubes()
        surface_extractor.SetInputData(self.reader.GetOutput())
        surface_extractor.SetValue(0, self.isovalue)

        # Create mapper and actor for the surface
        surface_mapper = vtk.vtkPolyDataMapper()
        surface_mapper.SetInputConnection(surface_extractor.GetOutputPort())
        surface_mapper.ScalarVisibilityOff()

        surface_actor = vtk.vtkActor()
        surface_actor.SetMapper(surface_mapper)
        surface_actor.GetProperty().SetColor(*self.color)

        # Return surface actor
        return surface_actor

    def render(self):
        self.read_data()

        # Create renderer and render window
        renderer = vtk.vtkRenderer()
        renderer.SetBackground(0.1, 0.2, 0.3)

        if self.mode == "raycast":
            # Add volume to renderer
            volume = self.raycast_rendering()
            renderer.AddVolume(volume)
        elif self.mode == "surface":
            # Add surface actor to renderer
            surface_actor = self.surface_rendering()
            renderer.AddActor(surface_actor)

        renderer.ResetCamera()
        return renderer
    
    def get_mpr_viewers(self):
            # Prepare three vtkImageViewer2 instances for Axial, Coronal, and Sagittal
        viewers = [vtk.vtkImageViewer2() for _ in range(3)]
        
        # Axial
        viewers[0].SetInputConnection(self.reader.GetOutputPort())
        viewers[0].SetSliceOrientationToXY()

        # Coronal
        viewers[1].SetInputConnection(self.reader.GetOutputPort())
        viewers[1].SetSliceOrientationToXZ()

        # Sagittal
        viewers[2].SetInputConnection(self.reader.GetOutputPort())
        viewers[2].SetSliceOrientationToYZ()

        return viewers
    
    
class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()

        # Setup the UI and VTK renderer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialize VTK render window
        self.vtk_layout = QVBoxLayout(self.ui.vol_render_widgt)
        # Initialize VTK render window
        self.vtk_widget = QVTKRenderWindowInteractor(self.ui.vol_render_widgt)
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.vtk_widget.Initialize()
        
        self.vtk_layout.addWidget(self.vtk_widget)

        # Ensure the layout resizes with the parent widget
        self.ui.vol_render_widgt.setLayout(self.vtk_layout)
        
        # self.sag_layout = QVBoxLayout(self.ui.sagittal_widget)
        # self.sag_widget = QVTKRenderWindowInteractor(self.ui.sagittal_widget)
        # self.sag_layout.addWidget(self.sag_widget)
        # self.sag_widget.setLayout(self.sag_layout)
        
        # self.axial_layout = QVBoxLayout(self.ui.axial_widget)
        # self.axial_widget = QVTKRenderWindowInteractor(self.ui.axial_widget)
        # self.axial_layout.addWidget(self.axial_widget)
        # self.axial_widget.setLayout(self.axial_layout)

        # self.cor_layout = QVBoxLayout(self.ui.corittal_widget)
        # self.cor_widget = QVTKRenderWindowInteractor(self.ui.corittal_widget)
        # self.cor_layout.addWidget(self.cor_widget)
        # self.cor_widget.setLayout(self.cor_layout)
        
        # Add the VTK widget to the layout
        
        self.ui.ray_btn.setChecked(True)

        self.ui.ray_btn.toggled.connect(self.toggle_inputs)
        self.ui.surface_btn.toggled.connect(self.toggle_inputs)
        
        self.ui.iso_slider.setRange(0, 1000)
        self.ui.iso_slider.setValue(100)
        self.ui.iso_slider.valueChanged.connect(self.update_isovalue_label)

        # Add shortcut for loading files
        QShortcut(QKeySequence("Ctrl+o"), self).activated.connect(self.select_folder)
        
        self.vtk_widgets = [self.ui.axial_widget, self.ui.coronal_widget, self.ui.sagittal_widget]
        self.sliders = [self.ui.axial_vSlider, self.ui.coronal_vSlider, self.ui.sagittal_vSlider]

        self.selected_folder = None
        self.viewers = None
        

   
    def setup_mpr_viewers(self):
        if not self.viewers:
            return

        for i, widget in enumerate(self.vtk_widgets):
            # Ensure only one instance of QVTKRenderWindowInteractor is created
            vtk_widget = QVTKRenderWindowInteractor(widget)
            layout = QVBoxLayout(widget)
            layout.addWidget(vtk_widget)
            widget.setLayout(layout)

            # Attach the interactor and initialize the viewer
            self.viewers[i].SetupInteractor(vtk_widget)
            self.viewers[i].Render()

            # Configure the slider with the slice range
            max_slices = self.viewers[i].GetSliceMax()
            self.sliders[i].setMinimum(0)
            self.sliders[i].setMaximum(max_slices)
            self.sliders[i].setValue(max_slices // 2)
            
            # Ensure the right slice updates using partial to avoid lambda issues
            self.sliders[i].valueChanged.connect(lambda value, idx=i: self.update_slice(value, idx)) 
   
    def update_slice(self, value, idx):
        self.viewers[idx].SetSlice(value)
        self.viewers[idx].Render()
        
        
    def select_folder(self):
        # Open a dialog to select a folder
        self.selected_folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if self.selected_folder:
            folder_name = os.path.basename(self.selected_folder)
            # self.selected_folder_label.setText(folder_name)
            # self.visualize_button.setEnabled(True)
            self.visualize()
            
            
    def visualize(self, in_place=False):
        if self.selected_folder:
            # Get the current values of the inputs
            current_mode = "raycast" if self.ui.ray_btn.isChecked() else "surface"
            current_ambient = .1
            current_diffuse = .9
            current_specular = .2
            current_specular_power = 10
            # current_isovalue = 100
            current_isovalue = self.ui.iso_slider.value()

            # Create a visualizer object
            visualizer = Visualizer(
                folder=self.selected_folder,
                mode=current_mode,
                ambient=current_ambient,
                diffuse=current_diffuse,
                specular=current_specular,
                specular_power=current_specular_power,
                isovalue=current_isovalue,
                color=(0.0, 0.0, 1.0),
            )

            # Get the current renderer
            render_window = self.vtk_widget.GetRenderWindow()
            current_renderer = render_window.GetRenderers().GetFirstRenderer()

            # Store the current camera settings
            if current_renderer:
                camera = current_renderer.GetActiveCamera()
                position = camera.GetPosition()
                focal_point = camera.GetFocalPoint()
                view_up = camera.GetViewUp()

            # Clear old data
            render_window.GetRenderers().RemoveAllItems()

            # Render the new data
            renderer = visualizer.render()

            # Apply the stored camera settings to the new renderer if update in place is enabled
            if current_renderer and in_place:
                new_camera = renderer.GetActiveCamera()
                new_camera.SetPosition(position)
                new_camera.SetFocalPoint(focal_point)
                new_camera.SetViewUp(view_up)

            # Set the background color and add the new renderer
            
            render_window.AddRenderer(renderer)
            render_window.Render()
            
            self.viewers = visualizer.get_mpr_viewers()
            self.setup_mpr_viewers()

    def toggle_inputs(self):
        # Enable/disable inputs based on the selected rendering mode
        raycast_selected = self.ui.ray_btn.isChecked()
        self.ui.iso_slider.setEnabled(not raycast_selected)
        if self.selected_folder:
            self.visualize()
    
    def update_isovalue_label(self):
        # Update the isovalue label when the slider value changes
        self.ui.iso_val_lbl.setText(f"Isovalue: {self.ui.iso_slider.value()}")
        if self.selected_folder:
            self.visualize(in_place=True)
        

def main():
    app = QApplication([])
    window = MyWindow()
    window.showMaximized()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
