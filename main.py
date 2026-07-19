import pygame
import math
from engine.world import World
from objects.soft_body import SoftBody

pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Soft-Body Physics Sandbox")
clock = pygame.Clock()

world = World(WIDTH, HEIGHT)

# Spawn initial 3D Meshes in center field
SoftBody(world, 400, 200, z=0.0, shape_type="cube", size=90.0, preset="Jello")
SoftBody(world, 550, 150, z=20.0, shape_type="sphere", size=60.0, preset="Jello")

# Orbital variables to visually rotate perspective
angle_x, angle_y = 0.0, 0.0

def project_3d_point(pos, cx, cy, rx, ry):
    """Applies Matrix Rotation + Perspective Projection to flat pixel space."""
    # Translate space to pivot origin around center stage
    x = pos[0] - cx
    y = pos[1] - cy
    z = pos[2]

    # Rotate around Y-axis
    x1 = x * math.cos(ry) - z * math.sin(ry)
    z1 = x * math.sin(ry) + z * math.cos(ry)

    # Rotate around X-axis
    y2 = y * math.cos(rx) - z1 * math.sin(rx)
    z2 = y * math.sin(rx) + z1 * math.cos(rx)

    # Perspective projection mapping calculations
    fov = 500.0
    distance = 600.0
    scale = fov / (distance + z2)
    
    proj_x = int(cx + x1 * scale)
    proj_y = int(cy + y2 * scale)
    return proj_x, proj_y

running = True
while running:
    dt = min(clock.tick(60) / 1000.0, 0.03)
    screen.fill((22, 22, 28))

    # Auto orbit rotation over runtime frames
    angle_x += 0.003
    angle_y += 0.005

    for event in pygame.get_event_dict():
        if event['type'] == pygame.QUIT:
            running = False
        elif event['type'] == pygame.MOUSEBUTTONDOWN:
            mx, my = event['pos']
            # Spawn random 3D elements via click
            stype = "sphere" if event['button'] == 3 else "cube"
            SoftBody(world, mx, my, z=0.0, shape_type=stype, size=75.0)

    world.step(dt)

    # Render environmental depth boundary guide tracks
    cx, cy = WIDTH // 2, HEIGHT // 2
    box_corners = [
        [40, 40, -250], [WIDTH-40, 40, -250], [WIDTH-40, HEIGHT-40, -250], [40, HEIGHT-40, -250],
        [40, 40, 250], [WIDTH-40, 40, 250], [WIDTH-40, HEIGHT-40, 250], [40, HEIGHT-40, 250]
    ]
    proj_bounds = [project_3d_point(c, cx, cy, angle_x, angle_y) for c in box_corners]
    
    for i in range(4):
        pygame.draw.line(screen, (45, 45, 60), proj_bounds[i], proj_bounds[(i+1)%4], 1)
        pygame.draw.line(screen, (45, 45, 60), proj_bounds[i+4], proj_bounds[((i+1)%4)+4], 1)
        pygame.draw.line(screen, (45, 45, 60), proj_bounds[i], proj_bounds[i+4], 1)

    # Render structural springs
    for s in world.springs:
        p1_2d = project_3d_point(s.p1.pos, cx, cy, angle_x, angle_y)
        p2_2d = project_3d_point(s.p2.pos, cx, cy, angle_x, angle_y)
        pygame.draw.line(screen, (70, 75, 95), p1_2d, p2_2d, 1)

    # Render node vertices
    for p in world.particles:
        p_2d = project_3d_point(p.pos, cx, cy, angle_x, angle_y)
        pygame.draw.circle(screen, p.color, p_2d, 4)

    pygame.display.flip()

pygame.quit()


