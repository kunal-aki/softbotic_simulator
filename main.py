import pygame
import math
from engine.world import World
from objects.soft_body import SoftBody
from objects.obstacle import Obstacle

pygame.init()
WIDTH, HEIGHT = 1100, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Universal 120Hz Multi-Dimensional Engine")
clock = pygame.time.Clock()

font = pygame.font.SysFont('consolas', 13)
font_bold = pygame.font.SysFont('consolas', 13, bold=True)

world = World(WIDTH, HEIGHT)

world.obstacles.append(Obstacle(1100, 1200, z=0.0, shape_type="circle", r=140.0))
world.obstacles.append(Obstacle(1800, 1300, z=100.0, shape_type="box", w=400.0, h=150.0, d=400.0))
world.obstacles.append(Obstacle(1400, 850, z=0.0, shape_type="box", w=500.0, h=40.0, angle=0.35))

material_presets = ["Jello", "Water Balloon", "Memory Foam", "Rubber"]
current_preset_idx = 0
selected_particle = None
dragging_camera = False
last_mouse_pos = (0, 0)
camera_target = [1500.0, 1000.0, 0.0]
angle_x, angle_y = 0.40, -0.50
zoom_scale = 0.40

# Primary controllable player body
player_body = SoftBody(world, 1600, 650, z=0.0, shape_type="circle", size=100.0, preset="Water Balloon")
player_body.is_player = True

SoftBody(world, 1200, 700, z=0.0, shape_type="square", size=120.0, preset="Jello")

class UISlider:
    def __init__(self, x, y, w, h, label, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.dragging = False

    def draw(self, screen):
        pygame.draw.rect(screen, (32, 32, 45), self.rect, border_radius=4)
        handle_x = self.rect.x + int(((self.val - self.min_val) / (self.max_val - self.min_val)) * self.rect.w)
        handle_rect = pygame.Rect(handle_x - 5, self.rect.y - 2, 10, self.rect.h + 4)
        pygame.draw.rect(screen, (0, 229, 255), handle_rect, border_radius=3)
        txt = font.render(f"{self.label}: {self.val:.1f}", True, (210, 215, 230))
        screen.blit(txt, (self.rect.x, self.rect.y - 16))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = max(0, min(event.pos[0] - self.rect.x, self.rect.w))
            self.val = self.min_val + (rel_x / self.rect.w) * (self.max_val - self.min_val)
            return True
        return False

gravity_slider = UISlider(15, 170, 180, 12, "Gravity", 0.0, 2000.0, 500.0)

def get_current_preset(): 
    return material_presets[current_preset_idx]

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
        if math.hypot(mx - px, my - py) < 18.0: 
            return "particle", p
    for obs in world.obstacles:
        ox, oy, _ = project_3d_point(obs.pos, cx, cy)
        thresh = obs.radius * zoom_scale if obs.type == "circle" else (max(obs.width, obs.height) / 2.0) * zoom_scale
        if math.hypot(mx - ox, my - oy) < max(thresh, 25.0): 
            return "obstacle", obs
    return None, None

def clean_delete_soft_body_via_particle(particle):
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
    if not world.is_3d:
        for x in range(x_min, x_max + 1, step):
            pygame.draw.line(screen, grid_color, project_3d_point([x, y_min, 0], cx, cy)[:2], project_3d_point([x, y_max, 0], cx, cy)[:2], 1)
        for y in range(y_min, y_max + 1, step):
            pygame.draw.line(screen, grid_color, project_3d_point([x_min, y, 0], cx, cy)[:2], project_3d_point([x_max, y, 0], cx, cy)[:2], 1)

def draw_3d_wire_box(center, size_dims, color, cx, cy, angle=0.0):
    dx, dy, dz = size_dims[0] / 2.0, size_dims[1] / 2.0, size_dims[2] / 2.0
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    
    corners = []
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            for sz in [-1, 1]:
                lx, ly, lz = sx * dx, sy * dy, sz * dz
                rx = lx * cos_a - ly * sin_a
                ry = lx * sin_a + ly * cos_a
                corners.append([center[0] + rx, center[1] + ry, center[2] + lz])
                
    pts = [project_3d_point(c, cx, cy) for c in corners]
    indices = [(0, 1), (1, 3), (3, 2), (2, 0), (4, 5), (5, 7), (7, 6), (6, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
    for start, end in indices:
        pygame.draw.line(screen, color, pts[start][:2], pts[end][:2], 2 if angle != 0.0 else 1)

def draw_soft_body_skinned(sb, cx, cy):
    if len(sb.particles) < 3:
        return

    ring_pts = sb.particles[1:] if sb.shape_type in ("circle", "sphere") else sb.particles
    proj_poly = [project_3d_point(p.pos, cx, cy)[:2] for p in ring_pts]

    avg_strain = 0.0
    if sb.springs:
        tot_strain = 0.0
        for s in sb.springs:
            dx = s.p1.pos[0] - s.p2.pos[0]
            dy = s.p1.pos[1] - s.p2.pos[1]
            dz = s.p1.pos[2] - s.p2.pos[2]
            curr_length = math.sqrt(dx * dx + dy * dy + dz * dz)
            
            rest_l = getattr(s, 'rest_length', getattr(s, 'rest_len', 1.0))
            tot_strain += abs(curr_length - rest_l) / max(1.0, rest_l)
            
        avg_strain = min(1.0, (tot_strain / len(sb.springs)) * 3.5)

    base_r = int(0 + avg_strain * 255)
    base_g = int(191 * (1.0 - avg_strain))
    base_b = int(255 * (1.0 - avg_strain))
    
    if getattr(sb, 'is_player', False):
        base_g, base_b = 255, 100

    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (base_r, base_g, base_b, 100), proj_poly)
    pygame.draw.polygon(surf, (base_r, base_g, base_b, 230), proj_poly, 3)
    screen.blit(surf, (0, 0))

def draw_ui(fps):
    pygame.draw.rect(screen, (22, 22, 32), (10, 10, 260, 200), border_radius=6)
    screen.blit(font_bold.render("SYSTEM CORE MODULE", True, (0, 255, 180)), (20, 16))
    screen.blit(font.render(f"FPS Target: 120Hz ({fps:.1f})", True, (210, 215, 230)), (20, 38))
    screen.blit(font.render(f"Particles: {len(world.particles)}", True, (210, 215, 230)), (20, 56))
    screen.blit(font.render(f"Preset: {get_current_preset()}", True, (255, 215, 0)), (20, 74))

    gravity_slider.draw(screen)

    panel_w, panel_h = 480, 360
    px, py = WIDTH - panel_w - 15, 15
    pygame.draw.rect(screen, (22, 22, 32), (px, py, panel_w, panel_h), border_radius=6)
    screen.blit(font_bold.render("WORKSPACE OPERATIONAL KEYBINDS", True, (0, 255, 180)), (px + 15, py + 15))
    controls = [
        ("WASD / Arrows", "SQUISHY CHARACTER CONTROLLER (Roll / Move)"),
        ("Spacebar", "Character Impulse Compression Jump"),
        ("V Key", "TOGGLE DIMENSION SYSTEM (Auto-Morphs Everything)"),
        ("C Key", "Spawn Rectangle Matrix (3D Cube / 2D Square)"),
        ("S Key", "Spawn Angular Shape (3D Pyramid / 2D Triangle)"),
        ("X Key", "Spawn Dynamic Balloon/Circle Mesh"),
        ("3 Key", "Cycle Material Presets (Jello/Balloon/Foam/Rubber)"),
        ("O Key", "Spawn Pillar Obstacle"),
        ("I Key", "Spawn Tilted Platform Ramp"),
        ("R Key", "CLEAR ALL OBJECTS FROM SIMULATION ARENA"),
        ("Delete / Bksp", "Delete selected/hovered soft-body or obstacle"),
        ("Hold D", "Continuous Eraser Brush (Deletes Nodes & Blocks)"),
        ("Left-Drag", "Grab / Manipulate dynamic simulation nodes"),
        ("Mid-Drag", "Flight Camera Track (Shift adjusts Depth layer)")
    ]
    curr_y = py + 40
    for k, desc in controls:
        screen.blit(font_bold.render(k, True, (0, 255, 180)), (px + 15, curr_y))
        screen.blit(font.render(desc, True, (190, 190, 205)), (px + 125, curr_y))
        curr_y += 22

running = True
jump_triggered = False

while running:
    dt = min(clock.tick(120) / 1000.0, 0.016)
    screen.fill((14, 14, 20))
    cx, cy = WIDTH // 2, HEIGHT // 2
    mx, my = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()

    world.gravity[1] = gravity_slider.val

    # Continuous eraser functionality
    if keys[pygame.K_d]:
        etype, element = get_entities_under_mouse(mx, my, cx, cy)
        if etype == "particle":
            clean_delete_soft_body_via_particle(element)
        elif etype == "obstacle":
            world.remove_obstacle(element)

    # Character Controller Inputs (Arrow keys / WASD)
    move_x = (1.0 if keys[pygame.K_RIGHT] or (keys[pygame.K_d] and not selected_particle) else 0.0) - \
             (1.0 if keys[pygame.K_LEFT] or (keys[pygame.K_a] and not selected_particle) else 0.0)
    move_y = (1.0 if keys[pygame.K_DOWN] or (keys[pygame.K_s] and not selected_particle) else 0.0) - \
             (1.0 if keys[pygame.K_UP] or (keys[pygame.K_w] and not selected_particle) else 0.0)
    
    if player_body in world.soft_bodies and hasattr(player_body, 'apply_character_controls'):
        player_body.apply_character_controls((move_x, move_y, 0.0), jump_trigger=jump_triggered)
    jump_triggered = False

    for event in pygame.event.get():
        if gravity_slider.handle_event(event):
            continue

        if event.type == pygame.QUIT: 
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.size
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: 
                running = False
            elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                if selected_particle:
                    clean_delete_soft_body_via_particle(selected_particle)
                    selected_particle = None
                else:
                    etype, element = get_entities_under_mouse(mx, my, cx, cy)
                    if etype == "particle":
                        clean_delete_soft_body_via_particle(element)
                    elif etype == "obstacle":
                        world.remove_obstacle(element)
            elif event.key == pygame.K_SPACE:
                jump_triggered = True
            elif event.key == pygame.K_v:
                world.is_3d = not world.is_3d
                for sb in list(world.soft_bodies):
                    sb.convert_dimension(world.is_3d, cx, cy)
            elif event.key == pygame.K_3:
                current_preset_idx = (current_preset_idx + 1) % len(material_presets)
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
                world.obstacles.append(Obstacle(wx, wy, z=0.0, shape_type="box", w=250.0, h=40.0, angle=0.35))
            elif event.key == pygame.K_r:
                world.particles.clear()
                world.springs.clear()
                world.soft_bodies.clear()
                world.obstacles.clear()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                etype, element = get_entities_under_mouse(mx, my, cx, cy)
                if etype == "particle": 
                    selected_particle = element
                    selected_particle.is_grabbed = True
            elif event.button == 2:
                dragging_camera = True
                last_mouse_pos = event.pos
            elif event.button == 4: 
                zoom_scale = min(zoom_scale + 0.03, 2.5)
            elif event.button == 5: 
                zoom_scale = max(zoom_scale - 0.03, 0.15)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: 
                if selected_particle:
                    selected_particle.is_grabbed = False
                    selected_particle = None
            elif event.button == 2: 
                dragging_camera = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging_camera:
                dx, dy = event.pos[0] - last_mouse_pos[0], event.pos[1] - last_mouse_pos[1]
                camera_target[0] -= dx / zoom_scale
                camera_target[1] -= dy / zoom_scale
                last_mouse_pos = event.pos
            elif selected_particle:
                wx, wy = get_world_pos_under_mouse(mx, my, cx, cy)
                dx = wx - selected_particle.pos[0]
                dy = wy - selected_particle.pos[1]

                parent_body = None
                for sb in world.soft_bodies:
                    if selected_particle in sb.particles:
                        parent_body = sb
                        break

                if parent_body:
                    parent_body.move_body_by_delta(dx, dy)
                else:
                    selected_particle.pos[0] = wx
                    selected_particle.pos[1] = wy
                    selected_particle.prev_pos[0] = wx
                    selected_particle.prev_pos[1] = wy

    world.step(dt)

    draw_structural_grid(cx, cy)
    draw_3d_wire_box([world.sim_width / 2, world.sim_height / 2, 0], [world.sim_width - 200, world.sim_height - 200, world.sim_depth * 2], (230, 45, 45), cx, cy)

    for obs in world.obstacles:
        if obs.type == "circle":
            ox, oy, _ = project_3d_point(obs.pos, cx, cy)
            pygame.draw.circle(screen, (58, 62, 82), (ox, oy), int(obs.radius * zoom_scale))
            pygame.draw.circle(screen, (110, 115, 140), (ox, oy), int(obs.radius * zoom_scale), 2)
        elif obs.type == "box":
            draw_3d_wire_box(obs.pos, [obs.width, obs.height, obs.depth], (110, 115, 140), cx, cy, angle=obs.angle)

    # Render visual soft body skins
    for sb in world.soft_bodies:
        draw_soft_body_skinned(sb, cx, cy)

    render_queue = []
    for s in world.springs:
        p1_proj = project_3d_point(s.p1.pos, cx, cy)
        p2_proj = project_3d_point(s.p2.pos, cx, cy)
        avg_z = (p1_proj[2] + p2_proj[2]) / 2.0
        render_queue.append(('spring', avg_z, (p1_proj[:2], p2_proj[:2])))

    for p in world.particles:
        px, py, pz = project_3d_point(p.pos, cx, cy)
        render_queue.append(('particle', pz, ((px, py), p.color)))

    render_queue.sort(key=lambda item: item[1], reverse=True)

    for item in render_queue:
        if item[0] == 'spring':
            pygame.draw.line(screen, (68, 72, 95), item[2][0], item[2][1], 1)
        elif item[0] == 'particle':
            pygame.draw.circle(screen, item[2][1], item[2][0], 4)

    draw_ui(clock.get_fps())
    pygame.display.flip()

pygame.quit()


