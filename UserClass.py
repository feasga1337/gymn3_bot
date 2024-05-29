class User:
    def __init__(self):
        self.grade = None
        self.user_menu = "menu"
        self.grade_choosen = None
        self.isokey = False
        self.ishometask = None

    def SetGrade(self, grade):
        self.grade = grade
