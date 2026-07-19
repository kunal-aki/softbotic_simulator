import pygame
import math

class Obstacle:
    def __init__(self, x, y, obstacle_type="circle", r=40.0, w=100.0, h=40.0):
        self.pos = [x, y]
        self.type = obstacle_type  # "circle" or "box"
        self.radius = r
        self.width = w
        self.height = h
        self.color = (130, 140, 150) # Industrial grey metallic color

    def resolve_collision(self, particle):
        """Pushes particles out of the obstacle walls symmetrically."""
        if self.type == "circle":
            dx = particle.pos[0] - self.pos[0]
            dy = particle.pos[1] - self.pos[1]
            dist = math.sqrt(dx*dx + dy*dy)
            min_dist = self.radius + particle.radius
            
            if dist < min_dist and dist > 0:
                # Push direction normal
                nx = dx / dist
                ny = dy / dist
                overlap = min_dist - dist
                
                # Snap position out of obstacle boundaries
                particle.pos[0] += nx * overlap
                particle.pos[1] += ny * overlap
                
                # Apply high friction dampening on surface scrub
                pvx = particle.pos[0] - particle.prev_pos[0]
                pvy = particle.pos[1] - particle.prev_pos[1]
                particle.prev_pos[0] = particle.pos[0] - pvx * 0.8
                particle.prev_pos[1] = particle.pos[1] - pvy * 0.8

        elif self.type == "box":
            half_w = self.width / 2.0
            half_h = self.height / 2.0
            
            # Find closest point on box bounds to particle center
            closest_x = max(self.pos[0] - half_w, min(particle.pos[0], self.pos[0] + half_w))
            closest_y = max(self.pos[1] - half_h, min(particle.pos[1], self.pos[1] + half_h))
            
            dx = particle.pos[0] - closest_x
            dy = particle.pos[1] - closest_y
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Collision happens if particle center is close enough or inside box completely
            is_inside = (particle.pos[0] > self.pos[0] - half_w and 
                         particle.pos[0] < self.pos[0] + half_w and 
                         particle.pos[1] > self.pos[1] - half_h and 
                         particle.pos[1] < self.pos[1] + half_h)
                         
            if dist < particle.radius or is_inside:
                if is_inside:
                    # Calculate vector displacements to closest outer edge walls
                    dl = particle.pos[0] - (self.pos[0] - half_w)
                    dr = (self.pos[0] + half_w) - particle.pos[0]
                    dt = particle.pos[1] - (self.pos[1] - half_h)
                    db = (self.pos[1] + half_h) - particle.pos[1]
                    
                    min_edge = min(dl, dr, dt, db)
                    if min_edge == dl:   particle.pos[0] -= (dl + particle.radius)
                    elif min_edge == dr: particle.pos[0] += (dr + particle.radius)
                    elif min_edge == dt: particle.pos[1] -= (dt + particle.radius)
                    else:                particle.pos[1] += (db + particle.radius)
                else:
                    if dist > 0:
                        particle.pos[0] = closest_x + (dx / dist) * particle.radius
                        particle.pos[1] = closest_y + (dy / dist) * particle.radius
                
                # Damp velocity vector profiles on rigid box wall impacts
                pvx = particle.pos[0] - particle.prev_pos[0]
                pvy = particle.pos[1] - particle.prev_pos[1]
                particle.prev_pos[0] = particle.pos[0] - pvx * 0.8
                particle.prev_pos[1] = particle.pos[1] - pvy * 0.8

    def draw(self, renderer, camera):
        if self.type == "circle":
            screen_pos = camera.world_to_screen(self.pos)
            r = int(self.radius * camera.zoom)
            if r > 0:
                pygame.draw.circle(renderer.screen, self.color, screen_pos, r)
                pygame.draw.circle(renderer.screen, (80, 90, 100), screen_pos, r, 2)
        elif self.type == "box":
            top_left = (self.pos[0] - self.width/2, self.pos[1] - self.height/2)
            tl_screen = camera.world_to_screen(top_left)
            w = int(self.width * camera.zoom)
            h = int(self.height * camera.zoom)
            if w > 0 and h > 0:
                pygame.draw.rect(renderer.screen, self.color, (tl_screen[0], tl_screen[1], w, h))
                pygame.draw.rect(renderer.screen, (80, 90, 100), (tl_screen[0], tl_screen[1], w, h), 2)

