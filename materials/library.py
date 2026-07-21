class Material:

    def __init__(
        self,
        name,
        density,
        stiffness,
        damping,
        color
    ):

        self.name=name

        self.density=density

        self.stiffness=stiffness

        self.damping=damping

        self.color=color


class MaterialLibrary:

    def __init__(self):

        self.materials={}

        self.load_defaults()


    def load_defaults(self):

        self.add(
            Material(
                "Ecoflex 00-30",
                1070,
                25,
                0.15,
                (70,180,255)
            )
        )

        self.add(
            Material(
                "Dragon Skin 20",
                1120,
                40,
                0.18,
                (255,150,60)
            )
        )

        self.add(
            Material(
                "TPU",
                1200,
                80,
                0.10,
                (120,255,120)
            )
        )

        self.add(
            Material(
                "Rubber",
                1100,
                60,
                0.20,
                (255,80,80)
            )
        )


    def add(self,material):

        self.materials[material.name]=material


    def get(self,name):

        return self.materials.get(name)

