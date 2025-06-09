import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Rectangle
import matplotlib.image as mpimg

# Load court image
img = mpimg.imread("shotchart.png")

fig, ax = plt.subplots(figsize=(10, 7))

# Draw court image as background
ax.imshow(img, extent=[-28.45, 28.45, 0, 53.5], zorder=0)

# Concentric shooting zones
radii = [3, 10, 16, 25]  # feet
for r in radii:
    arc = Arc((0, 2.15), 2*r, 2*r, theta1=0, theta2=180, color='orange', lw=2, linestyle='--', zorder=2)
    ax.add_patch(arc)

ax.plot(0, 2.15, 'ro')
corner_left = Rectangle((-22, 0), 3, 15.5, color='skyblue', alpha=0.3, zorder=2)
corner_right = Rectangle((19, 0), 3, 15.5, color='skyblue', alpha=0.3, zorder=2)
ax.add_patch(corner_left)
ax.add_patch(corner_right)

ax.set_xlim(-28.45, 28.45)
ax.set_ylim(0, 53.5)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title("Shot Chart Zones Over Court", fontsize=16)
plt.tight_layout()
plt.show()
