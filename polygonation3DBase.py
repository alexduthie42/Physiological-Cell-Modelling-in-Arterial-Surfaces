import vtk

"""Takes input polydata of a triangulated model. For each point in the triangulated polydata the cells the point is
    part of are found. The center coordinates of these cells are found and polygons are created from these points."""
def polygonation_callback(polydata_input):
    input_data = polydata_input.GetPolyDataInput()
    output_data = polydata_input.GetPolyDataOutput()
    output_data.ShallowCopy(input_data)

    append_filter = vtk.vtkAppendPolyData()

    # Iterate over each point of the input data.
    for i in range(0, output_data.GetNumberOfPoints()):
        cell_ids = vtk.vtkIdList()

        # Find the ids of all triangles the current point is a part of.
        output_data.GetPointCells(i, cell_ids)

        # Create new points data and polygon data.
        center_points = vtk.vtkPoints()
        center_poly = vtk.vtkPolygon()
        center_poly.GetPointIds().SetNumberOfIds(cell_ids.GetNumberOfIds())

        # Iterate over each of the triangles the current point is a part of.
        for j in range(0, cell_ids.GetNumberOfIds()):
            current_cell = output_data.GetCell(cell_ids.GetId(j))
            point_set = current_cell.GetPoints()

            # Find the coordinates of the triangle center.
            center_coords = [0, 0, 0]
            current_cell.TriangleCenter(point_set.GetPoint(0), point_set.GetPoint(1), point_set.GetPoint(2),
                                        center_coords)
            # Insert the center coordinates into new points data and new polygon.
            center_points.InsertNextPoint(center_coords)
            center_poly.GetPointIds().SetId(j, j)

        # Add new points and polygon to new polydata.
        center_polys = vtk.vtkCellArray()
        center_polys.InsertNextCell(center_poly)
        center_polydata = vtk.vtkPolyData()
        center_polydata.SetPolys(center_polys)
        center_polydata.SetPoints(center_points)

        # Find the two dimensional convex hull of the current polygon.
        convex_hull = vtk.vtkConvexHull2D()
        convex_hull.SetInputData(center_polydata)
        convex_hull.Update()

        # Create new points data and polygon data.
        new_poly_points = vtk.vtkPoints()
        new_poly = vtk.vtkPolygon()
        new_poly.GetPointIds().SetNumberOfIds(convex_hull.GetOutput().GetNumberOfPoints())

        # Iterate over the points of the two dimensional convex hull.
        for j in range(0, convex_hull.GetOutput().GetNumberOfPoints()):
            current_point = convex_hull.GetOutput().GetPoint(j)
            # Iterate over all the triangle center coordinates.
            for k in range(0, center_points.GetNumberOfPoints()):

                # Find the two dimensional convex hull point in the three dimensional center coordinates data and add
                # the three dimensional point to new points data and new polygon data.
                if current_point[0] == center_points.GetPoint(k)[0] or current_point[1] == \
                        center_points.GetPoint(k)[1]:
                    new_poly_points.InsertNextPoint(center_points.GetPoint(k))
                    new_poly.GetPointIds().SetId(j, j)
                    break

        # Add new points and polygon to new polydata.
        new_polys = vtk.vtkCellArray()
        new_polys.InsertNextCell(new_poly)
        new_polydata = vtk.vtkPolyData()
        new_polydata.SetPoints(new_poly_points)
        new_polydata.SetPolys(new_polys)

        # Add the new polygon and points to the total polydata.
        append_filter.AddInputData(new_polydata)
        append_filter.Update()

    # Set the output data of the filter.
    output_data.SetPolys(append_filter.GetOutput().GetPolys())
    output_data.SetPoints(append_filter.GetOutput().GetPoints())

