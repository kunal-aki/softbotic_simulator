from physics.forces import apply_gravity



class PhysicsSolver:


    def __init__(self):

        self.gravity=True



    def update(self,particles,dt):


        for particle in particles:


            if self.gravity:

                apply_gravity(
                    particle
                )


            particle.update(dt)

