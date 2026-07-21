class ObjectTree:


    def __init__(self,scene):

        self.scene=scene



    def objects(self):

        return [
            obj.name
            for obj in self.scene.objects
        ]

