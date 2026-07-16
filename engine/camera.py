class Camera:

    def __init__(self):

        self.position=[0,0]

        self.zoom=1


    def world_to_screen(self,pos):

        x=(pos[0]+self.position[0])*self.zoom
        y=(pos[1]+self.position[1])*self.zoom

        return(int(x),int(y))


    def screen_to_world(self,pos):

        x=pos[0]/self.zoom-self.position[0]
        y=pos[1]/self.zoom-self.position[1]

        return(x,y)

