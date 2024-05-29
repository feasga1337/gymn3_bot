from Timetable import Timetable
from Timetable import Lesson
lessonend = []
timetables = []
for x in range(10):
    lessonend.append(Lesson(x, x+1))
dayofweek = 'Mondey'
grade = '10a'
timetables.append(Timetable(grade, lessonend))
print(timetables[0].GetHomework())