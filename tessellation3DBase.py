
import vtk
import math
import random
import pointGenerationFilterBase
import polygonation3DBase

"""Takes an input model and cell size (area) and a tolerance for the delaunay triangulation. Triangulates the input
    model and generates points within the triangulated cells. The number of generated points is equal to the cell area
    divided by the input cell size. The points are then triangulated using delaunay 2d triangulation. The output of this
    triagunlation is cleaned to remove degenerate triangles and duplicate points. The final step of this filter creates
    convex polygons around each point using the centers of the neighboring cells to the point."""
def tessellation_callback(tessellation, size_of_cell1, tolerance1):
    input_data = tessellation.GetPolyDataInput()
    output_data = tessellation.GetPolyDataOutput()
    output_data.ShallowCopy(input_data)

    # Triangulate Surface.
    triangle_data = vtk.vtkTriangleFilter()
    triangle_data.SetInputData(output_data)
    triangle_data.Update()
    triangulated_model = triangle_data.GetOutput()

    number_of_polys = triangulated_model.GetNumberOfPolys()
    append_filter = vtk.vtkAppendPolyData()

    # Iterate over triangles.
    for i in range(0, 40):

        # Apply point generation filter.
        cell_index = i
        point_generation = vtk.vtkProgrammableFilter()
        point_generation.AddInputData(triangulated_model)
        point_generation.SetExecuteMethod(
            pointGenerationFilterBase.point_generation_callback(point_generation, cell_index, size_of_cell1))
        current_polydata = point_generation.GetPolyDataOutput()

        # Append current triangulation polyData to total model polyData.
        append_filter.AddInputData(current_polydata)
        append_filter.Update()

    # Triangulate current cells generated points.
    delaunay2D = vtk.vtkDelaunay2D()
    delaunay2D.SetInputData(append_filter.GetOutput())
    delaunay2D.SetSourceData(append_filter.GetOutput())
    delaunay2D.SetTolerance(tolerance1)
    delaunay2D.Update()

    # Remove degenerate triangles and remove duplicate points.
    cleaner = vtk.vtkCleanPolyData()
    cleaner.SetInputData(delaunay2D.GetOutput())
    cleaner.Update()

    polygonation = vtk.vtkProgrammableFilter()
    polygonation.AddInputData(cleaner.GetOutput())
    polygonation.SetExecuteMethod(polygonation3DBase.polygonation_callback(polygonation))

    output_data.SetPolys(polygonation.GetOutput().GetPolys())
    output_data.SetPoints(polygonation.GetOutput().GetPoints())

def main():

    # Read in data set.
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName("quadMeshFullc4080.vtp")
    reader.Update()

    cleaner = vtk.vtkCleanPolyData()
    cleaner.SetInputConnection(reader.GetOutputPort())
    cleaner.Update()

    # Apply tessellation filter.
    tessellation = vtk.vtkProgrammableFilter()
    tessellation.AddInputConnection(cleaner.GetOutputPort())
    tessellation.SetExecuteMethod(tessellation_callback(tessellation, 250, 0.008))

    # Set up mapper.
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(tessellation.GetOutput())
    mapper.ScalarVisibilityOff()

    # Set up actor.
    actor = vtk.vtkLODActor()
    actor.SetMapper(mapper)

    # Render.
    ren = vtk.vtkRenderer()
    ren_win = vtk.vtkRenderWindow()
    ren_win.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    # Add the actors to the renderer, set the background and size.
    ren.AddActor(actor)
    ren.SetBackground(0.1, 0.2, 0.4)
    ren_win.SetSize(800, 800)

    # Start event.
    iren.Initialize()
    ren_win.Render()
    iren.Start()

main()
