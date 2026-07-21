class Object:


    def __init__(self,name="Object"):

        self.name=name

        self.position=[
            0,
            0
        ]

        self.rotation=0

        self.scale=1.0

        self.visible=True

        self.selected=False

        self.material=None



    def update(self,dt):

        pass



    def draw(self,renderer,camera):

        pass



    def set_material(self,material):

        self.material=material



    def translate(self,x,y):

        self.position[0]+=x
        self.position[1]+=y

