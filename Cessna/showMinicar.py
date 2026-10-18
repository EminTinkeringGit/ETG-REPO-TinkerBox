import pyvista as pv

# Load the OBJ file
mesh = pv.read("objs/minicar.obj")

# Initialize the plotter
plotter = pv.Plotter()
plotter.add_axes()

# Add the mesh with custom styling
actor = plotter.add_mesh(mesh, color="lightblue", show_edges=False)
actor.rotate_x(90)

# Open the interactive window
plotter.show()


