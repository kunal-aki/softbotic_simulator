import pygame
import math
from engine.world import World
from objects.soft_body import SoftBody
from objects.obstacle import Obstacle


pygame.init()
WIDTH, HEIGHT = 1100, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Universal 120Hz Multi-Dimensional Engine")
clock = pygame.Clock()


font = pygame.font.SysFont('consolas', 13)
font_bold = pygame.font.SysFont('consolas', 13, bold=True)


world = World(WIDTH, HEIGHT)


# Map defaults
world.obstacles.append(Obstacle(1100, 1200, z=0.0, shape_type="circle", r=140.0))
world.obstacles.append(Obstacle(1800, 1300, z=100.0, shape_type="box", w=400.0, h=150.0, d=400.0))


material_presets = ["Jello", "Memory Foam"]
current_preset_idx = 0
selected_particle = None
dragging_camera = False
last_mouse_pos = (0, 0)


camera_target = [1500.0, 1000.0, 0.0]
angle_x, angle_y = 0.40, -0.50
zoom_scale = 0.40


# Initial spawn blocks
SoftBody(world, 1200, 700, z=0.0, shape_type="square", size=120.0, preset="Jello")
SoftBody(world, 1600, 650, z=0.0, shape_type="triangle", size=100.0, preset="Jello")


def get_current_preset(): return material_presets[current_preset_idx]


def project_3d_point(pos, cx, cy):
    dx = pos[0] - camera_target[0]
    dy = pos[1] - camera_target[1]
    dz = pos[2] - camera_target[2]


    if not world.is_3d:
        return int(cx + dx * zoom_scale), int(cy + dy * zoom_scale), 0.0


    x1 = dx * math.cos(angle_y) - dz * math.sin(angle_y)
    z1 = dx * math.sin(angle_y) + dz * math.cos(angle_y)
    y2 = dy * math.cos(angle_x) - z1 * math.sin(angle_x)
    z2 = dy * math.sin(angle_x) + z1 * math.cos(angle_x)


    scale = 900.0 / max(1.0, 900.0 + z2)
    return int(cx + x1 * scale * zoom_scale), int(cy + y2 * scale * zoom_scale), z2


def get_world_pos_under_mouse(mx, my, cx, cy):
    return camera_target[0] + (mx - cx) / zoom_scale, camera_target[1] + (my - cy) / zoom_scale


def get_entities_under_mouse(mx, my, cx, cy):
    for p in world.particles:
        px, py, _ = project_3d_point(p.pos, cx, cy)
        if math.hypot(mx - px, my - py) < 18.0: return "particle", p
    for obs in world.obstacles:
        ox, oy, _ = project_3d_point(obs.pos, cx, cy)
        thresh = obs.radius * zoom_scale if obs.type == "circle" else (max(obs.width, obs.height)/2.0) * zoom_scale
        if math.hypot(mx - ox, my - oy) < max(thresh, 25.0): return "obstacle", obs
    return None, None


def clean_delete_soft_body_via_particle(particle):
    """Finds and thoroughly extracts a soft body and all connected springs/particles instantly."""
    target_body = None
    body_id = getattr(particle, 'body_id', None)
    
    if body_id is not None:
        for sb in world.soft_bodies:
            if sb.id == body_id:
                target_body = sb
                break

    if target_body:
        if target_body in world.soft_bodies:
            world.soft_bodies.remove(target_body)
        for p in target_body.particles:
            if p in world.particles:
                world.particles.remove(p)
        for s in list(world.springs):
            if s.p1 in target_body.particles or s.p2 in target_body.particles:
                world.springs.remove(s)
    else:
        # Fallback if particle is an unattached lone point
        if particle in world.particles:
            world.particles.remove(particle)
        for s in list(world.springs):
            if s.p1 == particle or s.p2 == particle:
                world.springs.remove(s)


def draw_structural_grid(cx, cy):
    grid_color = (25, 27, 38)
    step = 50
    x_min, x_max = 100, world.sim_width - 100
    y_min, y_max = 100, world.sim_height - 100
    z_min, z_max = -world.sim_depth, world.sim_depth


    if not world.is_3d:
        for x in range(x_min, x_max + 1, step):
            pygame.draw.line(screen, grid_color, project_3d_point([x, y_min, 0], cx, cy)[:2], project_3d_point([x, y_max, 0], cx, cy)[:2], 1)
        for y in range(y_min, y_max + 1, step):
            pygame.draw.line(screen, grid_color, project_3d_point([x_min, y, 0], cx, cy)[:2], project_3d_point([x_max, y, 0], cx, cy)[:2], 1)
        return


    for x in range(x_min, x_max + 1, step * 2):
        pygame.draw.line(screen, grid_color, project_3d_point([x, y_max, z_min], cx, cy)[:2], project_3d_point([x, y_max, z_max], cx, cy)[:2], 1)
    for z in range(int(z_min), int(z_max) + 1, step * 2):
        pygame.draw.line(screen, grid_color, project_3d_point([x_min, y_max, z], cx, cy)[:2], project_3d_point([x_max, y_max, z], cx, cy)[:2], 1)


def draw_3d_wire_box(center, size_dims, color, cx, cy, fill_color=None):
    dx, dy, dz = size_dims[0]/2, size_dims[1]/2, size_dims[2]/2
    corners = []
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            for sz in [-1, 1]:
                corners.append([center[0]+sx*dx, center[1]+sy*dy, center[2]+sz*dz])
    pts = [project_3d_point(c, cx, cy) for c in corners]
   
    if fill_color and world.is_3d:
        quads = [[0,1,3,2], [4,5,7,6], [0,1,5,4], [2,3,7,6], [0,2,6,4], [1,3,7,5]]
        for q in quads:
            poly_pts = [pts[idx][:2] for idx in q]
            pygame.draw.polygon(screen, fill_color, poly_pts)


    indices = [(0,1), (1,3), (3,2), (2,0), (4,5), (5,7), (7,6), (6,4), (0,4), (1,5), (2,6), (3,7)]
    for start, end in indices:
        pygame.draw.line(screen, color, pts[start][:2], pts[end][:2], 1)


def draw_ui(fps):
    pygame.draw.rect(screen, (22, 22, 32), (10, 10, 260, 120), border_radius=6)
    screen.blit(font_bold.render("SYSTEM CORE MODULE", True, (0, 255, 180)), (20, 16))
    screen.blit(font.render(f"FPS Target:  120Hz ({fps:.1f})", True, (210, 215, 230)), (20, 38))
    screen.blit(font.render(f"Particles:   {len(world.particles)}", True, (210, 215, 230)), (20, 56))
    dim_str, dim_color = ("3D SOLID RENDER PLANE", (0, 191, 255)) if world.is_3d else ("2D FLATLAND PLANE", (240, 90, 40))
    screen.blit(font_bold.render(dim_str, True, dim_color), (20, 74))


    panel_w, panel_h = 480, 320
    px, py = WIDTH - panel_w - 15, 15
    pygame.draw.rect(screen, (22, 22, 32), (px, py, panel_w, panel_h), border_radius=6)
    screen.blit(font_bold.render("WORKSPACE OPERATIONAL KEYBINDS", True, (0, 255, 180)), (px + 15, py + 15))
    controls = [
        ("V Key", "TOGGLE DIMENSION SYSTEM (Auto-Morphs Everything)"),
        ("C Key", "Spawn Rectangle Matrix (3D Cube / 2D Square)"),
        ("S Key", "Spawn Angular Shape (3D Pyramid / 2D Triangle)"),
        ("X Key", "Spawn Curvature Shape (3D Sphere / 2D Circle Mesh)"),
        ("O Key", "Spawn Cylinder/Circle Pillar Obstacle"),
        ("I Key", "Spawn Box/Barrier Boundary Obstacle"),
        ("R Key", "CLEAR ALL OBJECTS FROM SIMULATION ARENA"),
        ("Hold D", "Continuous Eraser Brush (Deletes Nodes & Blocks)"),
        ("Left-Drag", "Grab / Manipulate simulation node coordinates"),
        ("Mid-Drag", "Flight Camera Track (Shift adjusts Depth layer)"),
        ("Scroll", "Zoom Camera Matrices Scale dynamically"),
        ("ESC Key", "TERMINATE SIMULATION WINDOW ENVIRONMENT")
    ]
    curr_y = py + 40
    for k, desc in controls:
        screen.blit(font_bold.render(k, True, (0, 255, 180)), (px + 15, curr_y))
        screen.blit(font.render(desc, True, (190, 190, 205)), (px + 105, curr_y))
        curr_y += 22


running = True
while running:
    dt = min(clock.tick(120) / 1000.0, 0.016)
    screen.fill((14, 14, 20))
    cx, cy = WIDTH // 2, HEIGHT // 2
    mx, my = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()


    # Continuous D Eraser Brush processing
    if keys[pygame.K_d]:
        etype, element = get_entities_under_mouse(mx, my, cx, cy)
        if etype == "particle":
            clean_delete_soft_body_via_particle(element)
        elif etype == "obstacle":
            world.remove_obstacle(element)


    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.size
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            elif event.key == pygame.K_v:
                world.is_3d = not world.is_3d
                for sb in list(world.soft_bodies): sb.convert_dimension(world.is_3d, cx, cy)
                if not world.is_3d:
                    for obs in world.obstacles: obs.pos[2] = 0.0
            elif event.key == pygame.K_c:
                wx, wy = get_world_pos_under_mouse(mx, my, cx, cy)
                stype = "cube" if world.is_3d else "square"
                SoftBody(world, wx, wy, z=0.0, shape_type=stype, size=110.0, preset=get_current_preset())
            elif event.key == pygame.K_s:
                wx, wy = get_world_pos_under_mouse(mx, my, cx, cy)
                stype = "pyramid" if world.is_3d else "triangle"
                SoftBody(world, wx, wy, z=0.0, shape_type=stype, size=100.0, preset=get_current_preset())
            elif event.key == pygame.K_x:
                wx, wy = get_world_pos_under_mouse(mx, my, cx, cy)
                stype = "sphere" if world.is_3d else "circle"
                SoftBody(world, wx, wy, z=0.0, shape_type=stype, size=90.0, preset=get_current_preset())
            elif event.key == pygame.K_o:
                wx, wy = get_world_pos_under_mouse(mx, my, cx, cy)
                world.obstacles.append(Obstacle(wx, wy, z=0.0, shape_type="circle", r=80.0))
            elif event.key == pygame.K_i:
                wx, wy = get_world_pos_under_mouse(mx, my, cx, cy)
                world.obstacles.append(Obstacle(wx, wy, z=0.0, shape_type="box", w=160.0, h=160.0, d=160.0))
            elif event.key == pygame.K_r:
                world.particles.clear()
                world.springs.clear()
                world.soft_bodies.clear()
                world.obstacles.clear()
       
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                etype, element = get_entities_under_mouse(mx, my, cx, cy)
                if etype == "particle": selected_particle = element
            elif event.button == 2:
                dragging_camera = True
                last_mouse_pos = event.pos
            elif event.button == 4: zoom_scale = min(zoom_scale + 0.03, 2.5)
            elif event.button == 5: zoom_scale = max(zoom_scale - 0.03, 0.15)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: selected_particle = None
            elif event.button == 2: dragging_camera = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging_camera:
                dx, dy = event.pos[0] - last_mouse_pos[0], event.pos[1] - last_mouse_pos[1]
                if world.is_3d:
                    if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                        camera_target[2] += dy / zoom_scale * 3.0
                    else:
                        camera_target[0] -= (dx * math.cos(angle_y) - dy * math.sin(angle_y)) / zoom_scale * 1.2
                        camera_target[1] -= (dy * math.cos(angle_x)) / zoom_scale * 1.2
                    angle_y += dx * 0.003
                    angle_x += dy * 0.003
                else:
                    camera_target[0] -= dx / zoom_scale
                    camera_target[1] -= dy / zoom_scale
                last_mouse_pos = event.pos
            elif selected_particle:
                wx, wy = get_world_pos_under_mouse(mx, my, cx, cy)
                selected_particle.prev_pos[0] = selected_particle.pos[0]
                selected_particle.prev_pos[1] = selected_particle.pos[1]
                selected_particle.pos[0], selected_particle.pos[1] = wx, wy


    world.step(dt)
    draw_structural_grid(cx, cy)


    draw_3d_wire_box([world.sim_width/2, world.sim_height/2, 0], [world.sim_width-200, world.sim_height-200, world.sim_depth*2], (230, 45, 45), cx, cy)


    for obs in world.obstacles:
        ox, oy, _ = project_3d_point(obs.pos, cx, cy)
        if obs.type == "circle":
            if world.is_3d:
                for r_offset in range(-int(obs.radius), int(obs.radius), 30):
                    calc_r = math.sqrt(max(1.0, obs.radius**2 - r_offset**2))
                    p_offset = project_3d_point([obs.pos[0], obs.pos[1], obs.pos[2] + r_offset], cx, cy)
                    pygame.draw.circle(screen, (48, 52, 72), (p_offset[0], p_offset[1]), int(calc_r * zoom_scale))
                    pygame.draw.circle(screen, (85, 90, 115), (p_offset[0], p_offset[1]), int(calc_r * zoom_scale), 1)
            else:
                pygame.draw.circle(screen, (58, 62, 82), (ox, oy), int(obs.radius * zoom_scale))
                pygame.draw.circle(screen, (110, 115, 140), (ox, oy), int(obs.radius * zoom_scale), 2)
        elif obs.type == "box":
            draw_3d_wire_box(obs.pos, [obs.width, obs.height, obs.depth], (110, 115, 140), cx, cy, fill_color=(48, 52, 72))


    render_queue = []


    for s in world.springs:
        p1_proj = project_3d_point(s.p1.pos, cx, cy)
        p2_proj = project_3d_point(s.p2.pos, cx, cy)
        avg_z = (p1_proj[2] + p2_proj[2]) / 2.0
        render_queue.append(('spring', avg_z, (p1_proj[:2], p2_proj[:2])))


    for sb in world.soft_bodies:
        faces = sb.get_faces()
        if world.is_3d and faces:
            for face in faces:
                try:
                    pts_3d = [sb.particles[idx].pos for idx in face]
                    projs = [project_3d_point(pt, cx, cy) for pt in pts_3d]
                    avg_z = sum(p[2] for p in projs) / len(projs)
                    poly_pts = [p[:2] for p in projs]
                   
                    base_color = (138, 43, 226) if sb.shape_type == "cube" else (230, 90, 40)
                    shade_factor = max(0.3, min(1.0, 1.0 - (avg_z / world.sim_depth)))
                    face_color = (int(base_color[0]*shade_factor), int(base_color[1]*shade_factor), int(base_color[2]*shade_factor))
                   
                    render_queue.append(('face', avg_z, (poly_pts, face_color)))
                except IndexError: pass


    for p in world.particles:
        px, py, pz = project_3d_point(p.pos, cx, cy)
        render_queue.append(('particle', pz, ((px, py), p.color)))


    render_queue.sort(key=lambda item: item[1], reverse=True)


    for item in render_queue:
        if item[0] == 'face':
            pygame.draw.polygon(screen, item[2][1], item[2][0])
            pygame.draw.polygon(screen, (20, 20, 30), item[2][0], 1)
        elif item[0] == 'spring':
            pygame.draw.line(screen, (68, 72, 95), item[2][0], item[2][1], 1)
        elif item[0] == 'particle':
            pygame.draw.circle(screen, item[2][1], item[2][0], 4)


    draw_ui(clock.get_fps())
    pygame.display.flip()


pygame.quit()


