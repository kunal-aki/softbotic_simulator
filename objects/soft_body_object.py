from objects.object import Object



class SoftBodyObject(Object):


    def __init__(self,name="Soft Body"):

        super().__init__(
            name
        )

        self.particles=[]

        self.springs=[]



    def add_particle(self,particle):

        self.particles.append(
            particle
        )



    def add_spring(self,spring):

        self.springs.append(
            spring
        )



    def update(self,dt):


        for particle in self.particles:

            particle.update(dt)



    def draw(self,renderer,camera):


        for spring in self.springs:

            spring.draw(
                renderer,
                camera
            )



        for particle in self.particles:

            particle.draw(
                renderer,
                camera
            )

