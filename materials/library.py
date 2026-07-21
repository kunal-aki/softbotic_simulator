class Material:


    def __init__(
        self,
        name,
        stiffness,
        density,
        damping=0.1
    ):

        self.name = name

        self.stiffness = stiffness

        self.density = density

        self.damping = damping



    def __str__(self):

        return self.name




class MaterialLibrary:


    def __init__(self):

        self.materials = {}

        self.create_default_materials()



    def create_default_materials(self):


        self.add_material(

            Material(
                "Silicone",
                stiffness=0.25,
                density=1.1,
                damping=0.15
            )

        )


        self.add_material(

            Material(
                "Rubber",
                stiffness=0.5,
                density=1.3,
                damping=0.2
            )

        )


        self.add_material(

            Material(
                "TPU",
                stiffness=0.8,
                density=1.2,
                damping=0.1
            )

        )


        self.add_material(

            Material(
                "Custom",
                stiffness=1.0,
                density=1.0,
                damping=0.1
            )

        )



    def add_material(self, material):

        self.materials[
            material.name
        ] = material



    def get(self,name):

        return self.materials.get(
            name
        )



    def get_all(self):

        return self.materials


