class SelectionManager:

    def __init__(self):

        self.selected=[]


    def clear(self):

        self.selected.clear()


    def select(self,obj):

        if obj not in self.selected:

            self.selected.append(obj)


    def deselect(self,obj):

        if obj in self.selected:

            self.selected.remove(obj)


    def toggle(self,obj):

        if obj in self.selected:

            self.selected.remove(obj)

        else:

            self.selected.append(obj)

