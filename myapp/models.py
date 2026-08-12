from django.db import models

class Teacher(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Batch(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    batch_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.department.name} - {self.batch_name}"


class Student(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    
    phone_no = models.CharField(max_length=15, blank=True, null=True) 
    is_active = models.BooleanField(default=True)



class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=True)

    class Meta:
        unique_together = ("student", "date")

    def __str__(self):
        return f"{self.student.name} - {self.date}"




