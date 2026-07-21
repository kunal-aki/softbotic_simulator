class History:

    def __init__(self):

        self.undo_stack=[]

        self.redo_stack=[]


    def push(self,action):

        self.undo_stack.append(action)

        self.redo_stack.clear()


    def undo(self):

        if self.undo_stack:

            action=self.undo_stack.pop()

            self.redo_stack.append(action)

            action.undo()


    def redo(self):

        if self.redo_stack:

            action=self.redo_stack.pop()

            self.undo_stack.append(action)

            action.redo()

