class Camera:
    def __init__(self):
        self.x=0; self.y=0
        self.zoom=1.0
        self.min_zoom=0.25
        self.max_zoom=5.0
    def world_to_screen(self,pos):
        return (int((pos[0]+self.x)*self.zoom), int((pos[1]+self.y)*self.zoom))
    def screen_to_world(self,pos):
        return (pos[0]/self.zoom-self.x, pos[1]/self.zoom-self.y)
    def move(self,dx,dy):
        self.x+=dx/self.zoom; self.y+=dy/self.zoom
    def zoom_in(self):
        self.zoom=min(self.max_zoom,self.zoom*1.1)
    def zoom_out(self):
        self.zoom=max(self.min_zoom,self.zoom/1.1)



