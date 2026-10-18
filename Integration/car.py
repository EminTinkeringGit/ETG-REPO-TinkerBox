import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ------------------------
# Simulation parameters
# ------------------------
dt = 0.5
t_end = 200.0

# ------------------------
# Vehicle parameters
# ------------------------
m = 1200.0            # kg

F_engine = 3000.0     # N
F_roll = 150.0        # N
Cd = 0.35             # Simplified drag coefficient

# ------------------------
# Initial state
# ------------------------
x = 0.0
v = 0.0
t = 0.0

# History
time = []
position = []
velocity = []
acceleration = []

# ------------------------
# Create figure
# ------------------------
fig, axs = plt.subplots(3, 1, figsize=(9, 8))

# Position
line_pos, = axs[0].plot([], [], lw=2)
axs[0].set_title("Position")
axs[0].set_xlim(0, t_end)
axs[0].set_ylim(0, 4000)
axs[0].grid(True)

# Velocity
line_vel, = axs[1].plot([], [], lw=2)
axs[1].set_title("Velocity")
axs[1].set_xlim(0, t_end)
axs[1].set_ylim(0, 100)
axs[1].grid(True)

# Acceleration
line_acc, = axs[2].plot([], [], lw=2)
axs[2].set_title("Acceleration")
axs[2].set_xlim(0, t_end)
axs[2].set_ylim(-2, 3)
axs[2].set_xlabel("Time (s)")
axs[2].grid(True)

plt.tight_layout()


# ------------------------
# Animation update
# ------------------------
def update(frame):

    global x, v, t

    # -------- Physics --------

    F_drag = Cd * v**2

    F_net = F_engine - F_roll - F_drag

    a = F_net / m

    # -------- Euler integration --------

    dx = v
    dv = a

    x += dx * dt
    v += dv * dt
    t += dt

    # -------- Store history --------

    time.append(t)
    position.append(x)
    velocity.append(v)
    acceleration.append(a)

    # -------- Update plots --------

    line_pos.set_data(time, position)
    line_vel.set_data(time, velocity)
    line_acc.set_data(time, acceleration)

    return line_pos, line_vel, line_acc


ani = FuncAnimation(
    fig,
    update,
    frames=int(t_end/dt),
    interval=1,
    blit=True,
    repeat=False
)

plt.show()