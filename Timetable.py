class Timetable:

    def __init__(self, grade, lessons):
        self.lessons = lessons

        self.grade = grade

    def GetHomework(self, dayofweek):
        answer = dayofweek + '\n'
        for x in self.lessons[dayofweek]:
            answer += f"{x.name}:{x.homework}\n"
        return answer

    def GetTimetable(self, dayofweek):
        answer = dayofweek + '\n'
        for x in self.lessons[dayofweek]:
            answer += f"{x.name}\n"
        return answer


class Lesson:

    def __init__(self, name, homework):
        self.homework = homework
        self.name = name
