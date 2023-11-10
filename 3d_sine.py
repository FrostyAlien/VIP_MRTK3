import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Parameters
r = 1
A = 0.2
n = 4  # number of periods

# Create theta array
theta = np.linspace(0, 2.*np.pi*n, 500)

# Calculate X and Y using cylindrical coordinates for the sine wave
X = r * np.cos(theta/n)
Y = r * np.sin(theta/n)

# Calculate sine wave for Z
Z = r + A * np.sin(theta)

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the sine wave
ax.plot(X, Y, Z, color='k')

# Create z array
z = np.linspace(-A, A, 500)

# Create 2D grids for theta and z
Theta, Z_cyl = np.meshgrid(theta, z)

# Calculate X and Y for the outer cylinder
R = np.sqrt(r**2 + A**2)  # new radius for the outer cylinder
X_outer = R * np.cos(Theta/n)
Y_outer = R * np.sin(Theta/n)

# Adjust Z_cyl to be centered around r
Z_cyl = r + Z_cyl

# Plot the outer cylinder
ax.plot_surface(X_outer, Y_outer, Z_cyl, rstride=10, cstride=10, color='r', alpha=0.3)

ax.view_init(90, 90)  # set initial view
plt.show()
