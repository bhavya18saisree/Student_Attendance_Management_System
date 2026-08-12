from django.shortcuts import render, redirect, get_object_or_404
from .models import Teacher, Student, Batch, Department, Attendance
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import datetime


# --------------------------
# REGISTER
# --------------------------
def register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if Teacher.objects.filter(email=email).exists():
            return render(request, "register.html", {"error": "Email already registered"})

        teacher = Teacher.objects.create(
            name=name,
            email=email,
            password=make_password(password)
        )

        request.session["teacher_id"] = teacher.id
        request.session["teacher_name"] = teacher.name

        return redirect("dashboard")

    return render(request, "register.html")


# --------------------------
# LOGIN
# --------------------------
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            teacher = Teacher.objects.get(email=email)
            if check_password(password, teacher.password):
                request.session["teacher_id"] = teacher.id
                request.session["teacher_name"] = teacher.name
                return redirect("dashboard")
            else:
                return render(request, "login.html", {"error": "Invalid password"})
        except Teacher.DoesNotExist:
            return render(request, "login.html", {"error": "Email not registered"})

    return render(request, "login.html")


# --------------------------
# DASHBOARD
# --------------------------
def dashboard(request):
    teacher_name = request.session.get("teacher_name")
    if not teacher_name:
        return redirect("login")

    return render(request, "dashboard.html", {"teacher_name": teacher_name})


# --------------------------
# LOGOUT
# --------------------------
def logout_view(request):
    request.session.flush()
    return redirect("login")


# --------------------------
# MANAGE STUDENTS
# --------------------------
def manage_students(request):
    teacher_id = request.session.get("teacher_id")
    if not teacher_id:
        return redirect("login")

    batches = Batch.objects.filter(teacher_id=teacher_id)
    students = Student.objects.filter(is_active=True, teacher_id=teacher_id)
    departments = Department.objects.all()

    if request.method == "POST":
        Student.objects.create(
            teacher_id=teacher_id,
            name=request.POST["name"],
            email=request.POST["email"],
            phone_no=request.POST["phone"],
            batch_id=request.POST["batch"]
        )
        return redirect("manage_students")

    return render(request, "manage.html", {
        "students": students,
        "batches": batches,
        "departments": departments
    })


def edit_student(request, student_id):
    teacher_id = request.session.get("teacher_id")
    if not teacher_id:
        return redirect("login")

    student = get_object_or_404(Student, id=student_id, teacher_id=teacher_id)
    batches = Batch.objects.filter(teacher_id=teacher_id)
    departments = Department.objects.all()

    if request.method == "POST":
        student.name = request.POST["name"]
        student.email = request.POST["email"]
        student.phone_no = request.POST["phone"]
        student.batch_id = request.POST["batch"]
        student.save()
        return redirect("manage_students")

    return render(request, "edit_student.html", {
        "student": student,
        "batches": batches,
        "departments": departments
    })


def delete_student(request, student_id):
    teacher_id = request.session.get("teacher_id")
    if not teacher_id:
        return redirect("login")

    student = get_object_or_404(Student, id=student_id, teacher_id=teacher_id)
    student.is_active = False
    student.save()
    return redirect("manage_students")


# --------------------------
# MARK ATTENDANCE
# --------------------------
def mark_attendance(request):
    teacher_id = request.session.get("teacher_id")
    if not teacher_id:
        return redirect("login")

    selected_batch_id = request.GET.get("batch")
    date_str = request.GET.get("date")

    # Handle selected date
    if date_str:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        selected_date = timezone.now().date()

    batches = Batch.objects.filter(teacher_id=teacher_id)

    students = []
    if selected_batch_id:
        students = Student.objects.filter(
            teacher_id=teacher_id,
            batch_id=selected_batch_id,
            is_active=True
        )

        # Load existing attendance for selected date
        for student in students:
            attendance = Attendance.objects.filter(
                student=student,
                date=selected_date
            ).first()

            student.is_present = attendance.is_present if attendance else False

    # Save attendance
    if request.method == "POST":
        selected_batch_id = request.POST.get("batch")
        date_str = request.POST.get("date")
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        students = Student.objects.filter(
            teacher_id=teacher_id,
            batch_id=selected_batch_id,
            is_active=True
        )

        for student in students:
            is_present = f"present_{student.id}" in request.POST

            Attendance.objects.update_or_create(
                student=student,
                date=selected_date,
                defaults={"is_present": is_present}
            )

        return redirect("dashboard")

    return render(request, "attendance.html", {
        "batches": batches,
        "students": students,
        "selected_batch_id": selected_batch_id,
        "selected_date": selected_date
    })


# --------------------------
# ATTENDANCE REPORT
# --------------------------
def attendance_report(request):
    teacher_id = request.session.get("teacher_id")
    if not teacher_id:
        return redirect("login")

    report_type = request.GET.get("type", "daily")
    today = timezone.now().date()

    # Daily Date
    selected_date = request.GET.get("date")

    if selected_date:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    else:
        selected_date = today

    # Start & End Date (for monthly/range)
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    else:
        start_date = today.replace(day=1)

    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        end_date = today

    students = Student.objects.filter(
        teacher_id=teacher_id,
        is_active=True
    )

    report_data = []

    for student in students:
        if report_type == "monthly":
            attendances = Attendance.objects.filter(
                student=student,
                date__range=(start_date, end_date)
            )
        else:
            attendances = Attendance.objects.filter(
                student=student,
                date=selected_date
            )

        total_days = attendances.count()
        present_days = attendances.filter(is_present=True).count()
        absent_days = attendances.filter(is_present=False).count()

        report_data.append({
            "name": student.name,
            "email": student.email,
            "phone": student.phone_no,
            "total": total_days,
            "present": present_days,
            "absent": absent_days,
        })

    return render(request, "attendance_reports.html", {
        "report_data": report_data,
        "report_type": report_type,
        "selected_date": selected_date,
        "start_date": start_date,
        "end_date": end_date,
    })









