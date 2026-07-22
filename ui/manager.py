"""
BioSim v2.0 - CAD User Interface Manager
Renders fixed top menu bar, functional toolbar, properties panel, and status bar.
"""

import pygame
from engine.config import (
    WIDTH, HEIGHT, TOP_MENU_HEIGHT, TOOLBAR_WIDTH, PROPERTIES_WIDTH, STATUS_BAR_HEIGHT,
    COLOR_TOP_BAR, COLOR_SIDEBAR, COLOR_PANEL, COLOR_STATUS_BAR, COLOR_BORDER,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_ACCENT, MATERIALS
)


class UIManager:

    def __init__(self):
        self.menu_items = ["File", "Edit", "View", "CAD", "Simulation", "Analysis", "Help"]
        self.active_dropdown = None

        self.tools = [
            {"name": "Select", "hotkey": "Q", "icon": "SEL"},
            {"name": "Move", "hotkey": "W", "icon": "MOV"},
            {"name": "Rotate", "hotkey": "E", "icon": "ROT"},
            {"name": "Scale", "hotkey": "R", "icon": "SCL"},
            {"name": "Particle", "hotkey": "P", "icon": "PTC"},
            {"name": "Spring", "hotkey": "S", "icon": "SPR"},
            {"name": "Rectangle Mesh", "hotkey": "B", "icon": "REC"},
            {"name": "Circle Mesh", "hotkey": "C", "icon": "CIR"},
        ]
        self.active_tool_index = 0
        self.tool_buttons = []
        self.material_buttons = []

    def get_active_tool_name(self):
        return self.tools[self.active_tool_index]["name"]

    def set_active_tool_by_name(self, name):
        for idx, t in enumerate(self.tools):
            if t["name"].lower() == name.lower():
                self.active_tool_index = idx
                return True
        return False

    def draw(self, surface, font, camera, selected_obj, status_text, sim_paused, scene, mouse_pos):
        self.draw_top_menu(surface, font)
        self.draw_toolbar(surface, font)
        self.draw_properties_panel(surface, font, selected_obj)
        self.draw_status_bar(surface, font, camera, selected_obj, status_text, sim_paused, mouse_pos)

    def draw_top_menu(self, surface, font):
        pygame.draw.rect(surface, COLOR_TOP_BAR, (0, 0, WIDTH, TOP_MENU_HEIGHT))
        pygame.draw.line(surface, COLOR_BORDER, (0, TOP_MENU_HEIGHT), (WIDTH, TOP_MENU_HEIGHT), 1)

        x = 12
        for item in self.menu_items:
            txt = font.render(item, True, COLOR_TEXT)
            rect = txt.get_rect(topleft=(x, 5))
            surface.blit(txt, rect)

            if self.active_dropdown == item:
                self.draw_dropdown_menu(surface, font, item, x, TOP_MENU_HEIGHT)

            x += txt.get_width() + 20

    def draw_dropdown_menu(self, surface, font, menu_name, x_pos, y_pos):
        options = []
        if menu_name == "File":
            options = ["New Project", "Save Scene (JSON)", "Load Scene (JSON)", "Exit"]
        elif menu_name == "Simulation":
            options = ["Toggle Run/Pause (SPACE)", "Reset Gravity"]

        if not options:
            return

        menu_w, menu_h = 180, len(options) * 26 + 6
        pygame.draw.rect(surface, COLOR_PANEL, (x_pos, y_pos, menu_w, menu_h))
        pygame.draw.rect(surface, COLOR_BORDER, (x_pos, y_pos, menu_w, menu_h), 1)

        for idx, opt in enumerate(options):
            opt_y = y_pos + 4 + idx * 26
            txt = font.render(opt, True, COLOR_TEXT)
            surface.blit(txt, (x_pos + 10, opt_y + 3))

    def draw_toolbar(self, surface, font):
        pygame.draw.rect(surface, COLOR_SIDEBAR, (0, TOP_MENU_HEIGHT, TOOLBAR_WIDTH, HEIGHT - TOP_MENU_HEIGHT))
        pygame.draw.line(surface, COLOR_BORDER, (TOOLBAR_WIDTH, TOP_MENU_HEIGHT), (TOOLBAR_WIDTH, HEIGHT), 1)

        self.tool_buttons.clear()
        y = TOP_MENU_HEIGHT + 10

        for idx, tool in enumerate(self.tools):
            rect = pygame.Rect(5, y, TOOLBAR_WIDTH - 10, 42)
            self.tool_buttons.append({"rect": rect, "index": idx, "name": tool["name"]})

            is_active = (idx == self.active_tool_index)
            bg = COLOR_ACCENT if is_active else COLOR_PANEL
            pygame.draw.rect(surface, bg, rect, border_radius=4)
            pygame.draw.rect(surface, COLOR_BORDER, rect, 1, border_radius=4)

            icon_txt = font.render(tool["icon"], True, COLOR_TEXT)
            surface.blit(icon_txt, (rect.centerx - icon_txt.get_width() // 2, rect.top + 6))

            key_txt = font.render(tool["hotkey"], True, COLOR_TEXT_DIM)
            surface.blit(key_txt, (rect.centerx - key_txt.get_width() // 2, rect.top + 22))

            y += 48

    def draw_properties_panel(self, surface, font, selected_obj):
        panel_x = WIDTH - PROPERTIES_WIDTH
        panel_rect = pygame.Rect(panel_x, TOP_MENU_HEIGHT, PROPERTIES_WIDTH, HEIGHT - TOP_MENU_HEIGHT - STATUS_BAR_HEIGHT)

        pygame.draw.rect(surface, COLOR_PANEL, panel_rect)
        pygame.draw.line(surface, COLOR_BORDER, (panel_x, TOP_MENU_HEIGHT), (panel_x, HEIGHT - STATUS_BAR_HEIGHT), 1)

        y = TOP_MENU_HEIGHT + 15
        title = font.render("PROPERTIES PANEL", True, COLOR_TEXT)
        surface.blit(title, (panel_x + 15, y))
        y += 25
        pygame.draw.line(surface, COLOR_BORDER, (panel_x + 15, y), (WIDTH - 15, y), 1)
        y += 15

        if not selected_obj:
            no_obj = font.render("No Object Selected", True, COLOR_TEXT_DIM)
            surface.blit(no_obj, (panel_x + 15, y))
            return

        fields = [
            ("Name", selected_obj.name),
            ("Position X", f"{selected_obj.x:.1f}"),
            ("Position Y", f"{selected_obj.y:.1f}"),
            ("Rotation", f"{getattr(selected_obj, 'rotation', 0.0):.2f} rad"),
            ("Scale", f"{getattr(selected_obj, 'scale', 1.0):.2f}"),
            ("Material", selected_obj.material_name),
            ("Visible", str(selected_obj.visible)),
        ]

        for label, val in fields:
            lbl_txt = font.render(label, True, COLOR_TEXT_DIM)
            val_txt = font.render(val, True, COLOR_TEXT)
            surface.blit(lbl_txt, (panel_x + 15, y))
            surface.blit(val_txt, (panel_x + 120, y))
            y += 22

        y += 10
        pygame.draw.line(surface, COLOR_BORDER, (panel_x + 15, y), (WIDTH - 15, y), 1)
        y += 15

        mat_title = font.render("Assign Material", True, COLOR_TEXT)
        surface.blit(mat_title, (panel_x + 15, y))
        y += 25

        self.material_buttons.clear()
        for mat_key in MATERIALS.keys():
            btn_rect = pygame.Rect(panel_x + 15, y, PROPERTIES_WIDTH - 30, 26)
            self.material_buttons.append({"rect": btn_rect, "material": mat_key})

            is_curr = (selected_obj.material_name == mat_key)
            bg = COLOR_ACCENT if is_curr else COLOR_SIDEBAR
            pygame.draw.rect(surface, bg, btn_rect, border_radius=3)
            pygame.draw.rect(surface, COLOR_BORDER, btn_rect, 1, border_radius=3)

            mat_txt = font.render(mat_key, True, COLOR_TEXT)
            surface.blit(mat_txt, (btn_rect.left + 10, btn_rect.top + 4))
            y += 32

    def draw_status_bar(self, surface, font, camera, selected_obj, status_text, sim_paused, mouse_pos):
        y_pos = HEIGHT - STATUS_BAR_HEIGHT
        pygame.draw.rect(surface, COLOR_STATUS_BAR, (0, y_pos, WIDTH, STATUS_BAR_HEIGHT))
        pygame.draw.line(surface, COLOR_BORDER, (0, y_pos), (WIDTH, y_pos), 1)

        sim_state = "PAUSED" if sim_paused else "RUNNING"
        obj_name = selected_obj.name if selected_obj else "None"

        status_str = f"Status: {status_text} | Sim: {sim_state} | Zoom: {camera.zoom:.2f}x | Cursor: ({mouse_pos[0]}, {mouse_pos[1]}) | Selected: {obj_name}"
        txt = font.render(status_str, True, COLOR_TEXT_DIM)
        surface.blit(txt, (12, y_pos + 4))

    def handle_click(self, mouse_pos, scene, app):
        # 1. Top Menu Items Click
        if mouse_pos[1] <= TOP_MENU_HEIGHT:
            x = 12
            font = app.font
            for item in self.menu_items:
                txt_w = font.render(item, True, COLOR_TEXT).get_width()
                if x <= mouse_pos[0] <= x + txt_w + 20:
                    self.active_dropdown = item if self.active_dropdown != item else None
                    return "menu"
                x += txt_w + 20
            return "menu"

        # 2. Dropdown Actions Click
        if self.active_dropdown:
            if self.active_dropdown == "File":
                if 12 <= mouse_pos[0] <= 192:
                    if TOP_MENU_HEIGHT <= mouse_pos[1] <= TOP_MENU_HEIGHT + 26:
                        scene.objects.clear()
                        scene.springs.clear()
                        app.status_text = "Created New Project"
                    elif TOP_MENU_HEIGHT + 26 < mouse_pos[1] <= TOP_MENU_HEIGHT + 52:
                        scene.save_to_file("scene.json")
                        app.status_text = "Saved Scene to scene.json"
                    elif TOP_MENU_HEIGHT + 52 < mouse_pos[1] <= TOP_MENU_HEIGHT + 78:
                        if scene.load_from_file("scene.json"):
                            app.status_text = "Loaded Scene from scene.json"
                        else:
                            app.status_text = "Failed to Load scene.json"
                    elif TOP_MENU_HEIGHT + 78 < mouse_pos[1] <= TOP_MENU_HEIGHT + 104:
                        app.running = False
            elif self.active_dropdown == "Simulation":
                scene.paused = not scene.paused
                app.status_text = "Toggled Simulation State"

            self.active_dropdown = None
            return "menu_action"

        # 3. Toolbar Buttons Click
        for btn in self.tool_buttons:
            if btn["rect"].collidepoint(mouse_pos):
                self.active_tool_index = btn["index"]
                return btn["name"]

        # 4. Material Buttons Click
        if app.selected_object:
            for btn in self.material_buttons:
                if btn["rect"].collidepoint(mouse_pos):
                    app.selected_object.set_material(btn["material"])
                    app.status_text = f"Assigned {btn['material']} to {app.selected_object.name}"
                    return "material_assigned"

        return None


