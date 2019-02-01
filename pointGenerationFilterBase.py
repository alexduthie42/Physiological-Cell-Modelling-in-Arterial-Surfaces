
import vtk
import math
import random

"""
Generates random points within the bounds of a triangle cell. The number of points generated is equal to the area of
the given cell divided by a given cell size. The output is a vtkPolyData containing the generated points and the
original points of the triangle but no cells.
"""

def point_generation_callback(input_cell, cell_index, size_of_cell):
    input_data = input_cell.GetPolyDataInput()
    output_data = input_cell.GetPolyDataOutput()
    output_data.ShallowCopy(input_data)

    current_cell = output_data.GetCell(cell_index)

    # Calculate the cell surfae area and the number of points to be generated with specified cell size.
    surface_area = current_cell.ComputeArea()
    number_of_points = surface_area / (size_of_cell)

    new_cell_points = vtk.vtkPoints()
    new_cell_points.DeepCopy(current_cell.GetPoints())
    point_count = 0

    # The three triangle points.
    point0 = current_cell.GetPoints().GetPoint(0)
    point1 = current_cell.GetPoints().GetPoint(1)
    point2 = current_cell.GetPoints().GetPoint(2)

    # Find minimum and maximum x and y coordinates.
    min_x = min(point0[0], point1[0], point2[0])
    max_x = max(point0[0], point1[0], point2[0])

    min_y = min(point0[1], point1[1], point2[1])
    max_y = max(point0[1], point1[1], point2[1])

    # Use vector cross product method to find the equation of the plane.
    vector1 = [point0[0] - point1[0], point0[1] -
               point1[1], point0[2] - point1[2]]
    vector2 = [point0[0] - point2[0], point0[1] -
               point2[1], point0[2] - point2[2]]

    cross_product = [(vector1[1] * vector2[2]) - (vector1[2] * vector2[1]),
                     (vector1[2] * vector2[0]) - (vector1[0] * vector2[2]),
                     (vector1[0] * vector2[1]) - (vector1[1] * vector2[0])]

    plane_value = cross_product[0] * point0[0] + cross_product[1] * point0[1] + cross_product[2] * point0[2]



    while point_count < int(number_of_points):
        # Generate random x and y coordinates within maximum and minimum bounds of polygon.
        new_x = random.uniform(min_x, max_x)
        new_y = random.uniform(min_y, max_y)

        # Determine the z value of the point.
        new_z = ((1 / cross_product[2]) * (plane_value - cross_product[0] * new_x - cross_product[1] * new_y))

        # Determine if generated point is within bounds of the triangle cell.
        if current_cell.PointInTriangle((new_x, new_y, new_z), point0, point1, point2, 0.0):
            new_cell_points.InsertNextPoint((new_x, new_y, new_z))

            point_count += 1

    # Create new points polydata
    empty_cells = vtk.vtkCellArray()
    output_data.SetPoints(new_cell_points)
    output_data.SetPolys(empty_cells)
