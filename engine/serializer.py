import json



class Serializer:


    def save(self,scene,path):


        data=[]


        for obj in scene.objects:


            data.append({

                "name":obj.name,

                "position":obj.position,

                "rotation":obj.rotation,

                "scale":obj.scale

            })



        with open(
            path,
            "w"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )



    def load(self,path):


        with open(
            path,
            "r"
        ) as file:

            return json.load(file)

