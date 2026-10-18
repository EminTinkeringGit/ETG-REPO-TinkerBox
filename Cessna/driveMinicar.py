import time
import numpy as np
import pyvista as pv
import math

# =============================================================================
# PHYSICS CONFIGURATION
# =============================================================================
MASS = 100.0          # Mass (kg)
INERTIA = 70       # Rotational Inertia (kg*m^2)
THRUST_MAG = 1000    # Forward/backward thrust force (N)
TORQUE_MAG = 100.0    # Turn torque (N*m)
LINEAR_DRAG = 5    # Damping coefficient (air resistance)
ANGULAR_DRAG = 2   # Rotational damping coefficient
DT = 0.1            # Simulation time step (seconds)

class InteractiveSimulation:
    def __init__(self, obj_path): # constructor
        
        try:
            self.mesh = pv.read(obj_path)
            self.mesh = self.mesh.rotate_x(90)
            self.mesh = self.mesh.rotate_z(180)
        except Exception as e:
            print(f"Error loading mesh: {e}. Falling back to a built-in arrow.")
            # Fallback mesh if the file path isn't immediately available
            self.mesh = pv.Arrow(direction=(1, 0, 0), scale=2.0)

        # 2. Initialize Physics State (2D Plane: X, Y and Z-rotation)
        self.pos = np.array([0.0, 0.0, 0.0])       # Position (m)
        self.vel = np.array([0.0, 0.0, 0.0])       # Velocity (m/s)
        self.angle = 0.0                        # Heading angle (radians)
        self.omega = 0.0                           # Angular velocity (rad/s)

        # Key state tracker to allow continuous holding of keys
        self.keys = {'8': False, '5': False, '4': False, '6': False}

        # 3. Setup PyVista Plotter
        self.plotter = pv.Plotter()
        
        # Add grid background for visual speed reference
        self.plotter.isometric_view()
        self.plotter.add_axes()
        
        # Add our model to the scene
        self.actor = self.plotter.add_mesh(self.mesh, show_edges=False)

        # 4. Bind VTK Key Observers for Smooth Control
        self.plotter.iren.add_observer("KeyPressEvent", self._on_key_press)
        self.plotter.iren.add_observer("KeyReleaseEvent", self._on_key_release)

    def _on_key_press(self, obj, event):
        # Access the raw VTK interactor with .interactor
        key = self.plotter.iren.interactor.GetKeySym().lower()
        if key in self.keys:
            self.keys[key] = True

    def _on_key_release(self, obj, event):
        # Access the raw VTK interactor with .interactor
        key = self.plotter.iren.interactor.GetKeySym().lower()
        if key in self.keys:
            self.keys[key] = False

    def update_physics(self):
        """
        Calculates forces/torques and updates positions using Euler-Cromer integration.
        """
        # Calculate local forward heading vector on the XY plane wrt to X
        forward = np.array([np.cos(self.angle), np.sin(self.angle), 0.0])

        force = np.zeros(3)
        torque = 0.0

        # Apply keyboard inputs to physical forces
        if self.keys['8']:  # Thrust forward
            force += forward * THRUST_MAG
        if self.keys['5']:  # Reverse thrust / brake
            force -= forward * THRUST_MAG
        if self.keys['4']:  # Rotate counter-clockwise
            torque += TORQUE_MAG
        if self.keys['6']:  # Rotate clockwise
            torque -= TORQUE_MAG

        # Apply drag forces (to prevent infinite acceleration)
        force -= LINEAR_DRAG * self.vel
        torque -= ANGULAR_DRAG * self.omega

        # --- Equations of Motion (EoM) ---
        # Linear translation
        accel = force / MASS
        self.vel += accel * DT
        self.pos += self.vel * DT

        # Angular rotation
        alpha = torque / INERTIA
        self.omega += alpha * DT
        self.angle += self.omega * DT

        # --- Update Model Transforms ---
        # Position translation
        self.actor.position = self.pos
        self.actor.orientation = [0.0, 0.0, np.degrees(self.angle)]


    def run(self):
            # 1. Open the render window in non-blocking mode (must specify auto_close=False)
            self.plotter.show(interactive_update=True, auto_close=False)
            
            # 2. Loop continuously until the window is closed
            while True:
                try:
                    self.update_physics()
                    
                    # Center the camera on the moving body
                    #self.plotter.camera.position = (self.pos[0], self.pos[1], self.plotter.camera.position[2])
                    #self.plotter.camera.focal_point = (self.pos[0], self.pos[1], 0.0)
                    
                    # Forces a screen refresh and processes user keyboard inputs
                    self.plotter.update()
                    
                    time.sleep(DT)
                    
                except Exception:
                    # If the user closes the window, plotter.update() will raise an error.
                    # Catching it here allows a clean exit.
                    break
                    
            print("Simulation ended.")

if __name__ == "__main__":
    sim = InteractiveSimulation("objs/minicar.obj")
    sim.run()