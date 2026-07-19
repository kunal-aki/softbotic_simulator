import pygame
import math
from engine.world import World
from objects.soft_body import SoftBody
from objects.obstacle import Obstacle

pygame.init()
WIDTH, HEIGHT = 1100, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Universal Multi-Dimensional Sandbox Engine")
clock = pygame.Clock()

font = pygame.font.SysFont('consolas', 13)
font_bold = pygame.font.SysFont('consolas', 13, bold=True)

world = World(WIDTH, HEIGHT)

# Populate Obstacles
world.obstacles.append(Obstacle(500, 750, z=0.0, shape_type="circle", r=70.0))
world.obstacles.append(Obstacle(1000, 850, z=50.0, shape_type="box", w=220.0, h=60.0, d=200.0))
world.obstacles.append(Obstacle(1400, 600, z=-50.0, shape_type="circle", r=60.0))

material_presets = ["Jello", "Memory Foam"]
current_preset_idx = 0
selected_particle = None
dragging_camera = False
last_mouse_pos = (0, 0)

angle_x, angle_y = 0.35, -0.45
zoom_scale = 0.55
camera_offset = [200.0, 250.0]

# Initial Shapes (spaced to prevent clipping triggers)
SoftBody(world, 650, 450, z=0.0, shape_type="cube", size=100.0, preset="Jello")
SoftBody(world, 1250, 400, z=0.0, shape_type="sphere", size=75.0, preset="Jello")

def get_current_preset(): return material_presets[current_preset_idx]

def project_3d_point(pos, cx, cy):
    x = (pos[0] - cx + camera_offset[0]) * zoom_scale
    y = (pos[1] - cy + camera_offset[1]) * zoom_scale
    z = pos[2] * zoom_scale

    if not world.is_3d:
        return int(cx + x), int(cy + y), 0.0

    x1 = x * math.cos(angle_y) - z * math.sin(angle_y)
    z1 = x * math.sin(angle_y) + z * math.cos(angle_y)
    y2 = y * math.cos(angle_x) - z1 * math.sin(angle_x)
    z2 = y * math.sin(angle_x) + z1 * math.cos(angle_x)

    scale = 750.0 / (750.0 + z2)
    return int(cx + x1 * scale), int(cy + y2 * scale), z2

def get_world_pos_under_mouse(mx, my, cx, cy):
    return cx + (mx - cx) / zoom_scale - camera_offset[0], cy + (my - cy) / zoom_scale - camera_offset[1]

def get_entities_under_mouse(mx, my, cx, cy):
    for p in world.particles:
        px, py, _ = project_3d_point(p.pos, cx, cy)
        if math.hypot(mx - px, my - py) < 24.0:
            return "particle", p
            
    for obs in world.obstacles:
        ox, oy, _ = project_3d_point(obs.pos, cx, cy)
        threshold = obs.radius * zoom_scale if obs.type == "circle" else (max(obs.width, obs.height)/2.0) * zoom_scale
        if math.hypot(mx - ox, my - oy) < max(threshold, 20.0):
            return "obstacle", obs
    return None, None

def draw_structural_grid(cx, cy):
    grid_color = (25, 27, 38)
    step = 150
    x_min, x_max = 100, world.sim_width - 100
    y_min, y_max = 100, world.sim_height - 100
    z_min, z_max = -world.sim_depth, world.sim_depth

    if not world.is_3d:
        for x in range(x_min, x_max + 1, step):
            p1 = project_3d_point([x, y_min, 0], cx, cy)[:2]
            p2 = project_3d_point([x, y_max, 0], cx, cy)[:2]
            pygame.draw.line(screen, grid_color, p1, p2, 1)
        for y in range(y_min, y_max + 1, step):
            p1 = project_3d_point([x_min, y, 0], cx, cy)[:2]
            p2 = project_3d_point([x_max, y, 0], cx, cy)[:2]
            pygame.draw.line(screen, grid_color, p1, p2, 1)
        return

    for x in range(x_min, x_max + 1, step):
        p1 = project_3d_point([x, y_max, z_min], cx, cy)[:2]
        p2 = project_3d_point([x, y_max, z_max], cx, cy)[:2]
        pygame.draw.line(screen, grid_color, p1, p2, 1)
    for z in range(int(z_min), int(z_max) + 1, step):
        p1 = project_3d_point([x_min, y_max, z], cx, cy)[:2]
        p2 = project_3d_point([x_max, y_max, z], cx, cy)[:2]
        pygame.draw.line(screen, grid_color, p1, p2, 1)
    for x in range(x_min, x_max + 1, step):
        p1 = project_3d_point([x, y_min, z_min], cx, cy)[:2]
        p2 = project_3d_point([x, y_max, z_min], cx, cy)[:2]
        pygame.draw.line(screen, grid_color, p1, p2, 1)
    for y in range(y_min, y_max + 1, step):
        p1 = project_3d_point([x_min, y, z_min], cx, cy)[:2]
        p2 = project_3d_point([x_max, y, z_min], cx, cy)[:2]
        pygame.draw.line(screen, grid_color, p1, p2, 1)

def draw_ui(fps):
    pygame.draw.rect(screen, (22, 22, 32), (10, 10, 260, 120), border_radius=6)
    screen.blit(font_bold.render("SYSTEM CORE MODULE", True, (0, 255, 180)), (20, 16))
    screen.blit(font.render(f"FPS:         {fps:.1f}", True, (210, 215, 230)), (20, 38))
    screen.blit(font.render(f"PARTICLES:   {len(world.particles)}", True, (210, 215, 230)), (20, 56))
    dim_str, dim_color = ("3D MATRIX UNIVERSE", (0, 191, 255)) if world.is_3d else ("2D FLATLAND PLANE", (240, 90, 40))
    screen.blit(font_bold.render(dim_str, True, dim_color), (20, 74))
    screen.blit(font.render(f"MATERIAL:    {get_current_preset().upper()}", True, (255, 200, 0)), (20, 94))

    panel_w, panel_h = 440, 280
    px, py = WIDTH - panel_w - 15, 15
    pygame.draw.rect(screen, (22, 22, 32), (px, py, panel_w, panel_h), border_radius=6)
    pygame.draw.rect(screen, (45, 48, 65), (px, py, panel_w, panel_h), 1, border_radius=6)
    screen.blit(font_bold.render("WORKSPACE OPERATIONAL KEYBINDS", True, (0, 255, 180)), (px + 15, py + 15))
    controls = [
        ("V Key", "TOGGLE DIMENSION SYSTEM (Auto-Morphs Everything)"),
        ("C Key", "Spawn Primary Shape (3D Cube / 2D Grid Square)"),
        ("S Key", "Spawn Alternate Shape (3D Sphere / 2D Triangle)"),
        ("O Key", "Spawn Rigid Obstacle Ball at Mouse Cursor"),
        ("3 Key", "Cycle Material Settings (Jello / Memory Foam)"),
        ("Hold D", "Continuous Eraser Brush (Deletes Nodes & Blocks)"),
        ("Left-Drag", "Grab / Manipulate simulation node coordinates"),
        ("Mid-Drag", "Pan Viewport Cam (2D) / Rotate Camera Orbit (3D)"),
        ("Scroll", "Zoom Camera Viewport scale matrices dynamically"),
        ("ESC Key", "TERMINATE SIMULATION WINDOW ENVIRONMENT")
    ]
    curr_y = py + 40
    for k, desc in controls:
        screen.blit(font_bold.render(k, True, (0, 255, 180)), (px + 15, curr_y))
        screen.blit(font.render(desc, True, (190, 190, 205)), (px + 105, curr_y))
        curr_y += 24

running = True
while running:
    dt = min(clock.tick(60) / 1000.0, 0.03)
    screen.fill((14, 14, 20))
    cx, cy = WIDTH // 2, HEIGHT // 2
    mx, my = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()

    if keys[pygame.K_d]:
        etype, element = get_entities_under_mouse(mx, my, cx, cy)
        if etype == "particle": world.remove_particle(element)
        elif etype == "obstacle": world.remove_obstacle(element)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.size
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_v:
                world.is_3d = not world.is_3d
                for sb in list(world.soft_bodies):
                    sb.convert_dimension(world.is_3d, cx, cy)
                if not world.is_3d:
                    for obs in world.obstacles: obs.pos[2] = 0.0
            elif event.key == pygame.K_c:
                wx, wy = get_world_pos_under_mouse(mx, my, cx, cy)
                stype = "cube" if world.is_3d else "square"
                SoftBody(world, wx, wy, z=0.0, shape_type=stype, size=95.0, preset=get_current_preset())
            elif event.key == pygame.K_s:
                wx, wy = get_world_pos_under_mouse(mx, my, cx, cy)
                stype = "sphere" if world.is_3d else "triangle"
                SoftBody(world, wx, wy, z=0.0, shape_type=stype, size=70.0, preset=get_current_preset())
            elif event.key == pygame.K_o:
                wx, wy = get_world_pos_under_mouse(mx, my, cx, cy)
                world.obstacles.append(Obstacle(wx, wy, z=0.0, shape_type="circle", r=55.0))
            elif event.key == pygame.K_3:
                current_preset_idx = (current_preset_idx + 1) % len(material_presets)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                etype, element = get_entities_under_mouse(mx, my, cx, cy)
                if etype == "particle": selected_particle = element
            elif event.button == 2: 
                dragging_camera = True
                last_mouse_pos = event.pos
            elif event.button == 4: zoom_scale = min(zoom_scale + 0.04, 2.2)
            elif event.button == 5: zoom_scale = max(zoom_scale - 0.04, 0.25)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: selected_particle = None
            elif event.button == 2: dragging_camera = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging_camera:
                dx, dy = event.pos[0] - last_mouse_pos[0], event.pos[1] - last_mouse_pos[1]
                if world.is_3d:
                    angle_y += dx * 0.006
                    angle_x += dy * 0.006
                else:
                    camera_offset[0] += dx / zoom_scale
                    camera_offset[1] += dy / zoom_scale
                last_mouse_pos = event.pos
            elif selected_particle:
                if world.is_3d:
                    selected_particle.pos[0] += (event.rel[0] / zoom_scale) * math.cos(angle_y)
                    selected_particle.pos[1] += (event.rel[1] / zoom_scale)
                else:
                    wx, wy = get_world_pos_under_mouse(mx, my, cx, cy)
                    selected_particle.pos[0], selected_particle.pos[1] = wx, wy
                selected_particle.prev_pos = list(selected_particle.pos)

    world.step(dt)
    draw_structural_grid(cx, cy)

    # Render Boundary Frames
    b_color = (230, 45, 45)
    w_lim, h_lim, d_lim = world.sim_width - 100, world.sim_height - 100, world.sim_depth
    box_corners = [
        [100, 100, -d_lim], [w_lim, 100, -d_lim], [w_lim, h_lim, -d_lim], [100, h_lim, -d_lim],
        [100, 100, d_lim], [w_lim, 100, d_lim], [w_lim, h_lim, d_lim], [100, h_lim, d_lim]
    ]
    proj_bounds = [project_3d_point(c, cx, cy)[:2] for c in box_corners]
    
    if world.is_3d:
        for i in range(4):
            pygame.draw.line(screen, b_color, proj_bounds[i], proj_bounds[(i+1)%4], 2)
            pygame.draw.line(screen, b_color, proj_bounds[i+4], proj_bounds[((i+1)%4)+4], 2)
            pygame.draw.line(screen, b_color, proj_bounds[i], proj_bounds[i+4], 2)
    else:
        pygame.draw.line(screen, b_color, proj_bounds[3], proj_bounds[2], 3)
        pygame.draw.line(screen, b_color, proj_bounds[0], proj_bounds[1], 2)
        pygame.draw.line(screen, b_color, proj_bounds[0], proj_bounds[3], 2)
        pygame.draw.line(screen, b_color, proj_bounds[1], proj_bounds[2], 2)

    # Render Obstacles
    for obs in world.obstacles:
        ox, oy, _ = project_3d_point(obs.pos, cx, cy)
        if obs.type == "circle":
            if world.is_3d:
                for r_offset in range(0, int(obs.radius), 12):
                    z_r = int(math.sqrt(max(1.0, obs.radius**2 - r_offset**2)) * zoom_scale)
                    pygame.draw.circle(screen, (48, 52, 70), (ox, oy), z_r, 1)
            pygame.draw.circle(screen, (58, 62, 82), (ox, oy), int(obs.radius * zoom_scale))
            pygame.draw.circle(screen, (110, 115, 140), (ox, oy), int(obs.radius * zoom_scale), 2)
        elif obs.type == "box":
            rw, rh = int(obs.width * zoom_scale), int(obs.height * zoom_scale)
            if world.is_3d:
                front_p = project_3d_point([obs.pos[0], obs.pos[1], obs.pos[2] + obs.depth/2], cx, cy)[:2]
                back_p = project_3d_point([obs.pos[0], obs.pos[1], obs.pos[2] - obs.depth/2], cx, cy)[:2]
                pygame.draw.line(screen, (90, 95, 115), front_p, back_p, 1)
            pygame.draw.rect(screen, (58, 62, 82), (ox - rw//2, oy - rh//2, rw, rh))
            pygame.draw.rect(screen, (110, 115, 140), (ox - rw//2, oy - rh//2, rw, rh), 2)

    # Render Springs
    for s in world.springs:
        x1, y1, _ = project_3d_point(s.p1.pos, cx, cy)
        x2, y2, _ = project_3d_point(s.p2.pos, cx, cy)
        pygame.draw.line(screen, (68, 72, 95), (x1, y1), (x2, y2), 1)

    # Render Particles
    for p in world.particles:
        px, py, _ = project_3d_point(p.pos, cx, cy)
        pygame.draw.circle(screen, p.color, (px, py), 4)

    draw_ui(clock.get_fps())
    pygame.display.flip()

pygame.quit()


