from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth import authenticate, login
from datetime import timedelta, datetime
from .forms import *
from .models import *
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.db.models import Q
import os
from django.contrib import messages
from django.utils import timezone
from .models import CustomUser, Course, CourseTimeToBeat, UserReg

import uuid
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from django.conf import settings
from yookassa import Configuration, Payment
from .models import PaymentLog

from openpyxl import Workbook
from openpyxl.styles import Font
from io import BytesIO


def home(request):
    user = request.user if request.user.is_authenticated else None
    username = user.username if user else None
    admin_status = user.is_staff if user else False  # <- always define this

    courses = Course.objects.prefetch_related('coursetimetobeat_set').all()
    category = Category.objects.all()
    topic = Topic.objects.all()
    term_of_study = Term_of_study.objects.all()

    return render(request, 'homepage.html', {
        'courses': courses,
        'category': category,
        'topic': topic,
        'term_of_study': term_of_study,
        'username': username,
        'user': user,
        'admin_status': admin_status
    })


def register(request, course_id):
    if request.user.is_authenticated:
        return redirect('register_user_reg', course_id=course_id)

    # Fetch the course and its available CourseTimeToBeat options
    course = Course.objects.get(id=course_id)
    course_times = CourseTimeToBeat.objects.filter(course=course)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        birthdate = request.POST.get('birthdate')
        snils = request.POST.get('snils')
        gender = request.POST.get('gender')
        promocode_name = request.POST.get('promocode')
        education = request.POST.get('education')  # Get the education level
        picture1 = request.FILES.get('picture1')
        picture2 = request.FILES.get('picture2')
        time_to_beat_id = request.POST.get('time_to_beat')  # Get the selected course duration

        
        print(request.POST.get('promocode'))
        promocode = Promocode.objects.filter(name=promocode_name).first()
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        print(promocode)

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким E-mail уже существует.')
            return render(request, 'register.html', {
                'email': email,
                'username': username,
                'phone_number': phone_number,
                'address': address,
                'birthdate': birthdate,
                'snils': snils,
                'gender': gender,
                'promocode': promocode.name,
                'education': education,
                'course_times': course_times,  # Pass course_times to the template
            })

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует.')
            return render(request, 'register.html', {
                'email': email,
                'username': username,
                'phone_number': phone_number,
                'address': address,
                'birthdate': birthdate,
                'snils': snils,
                'gender': gender,
                'promocode': promocode.name,
                'education': education,
                'course_times': course_times,  # Pass course_times to the template
            })
        if promocode_name:
            if not promocode:
                messages.error(request, 'Данный промокод не существует проверьте правильность его написания.')
                return render(request, 'register.html', {
                    'email': email,
                    'username': username,
                    'phone_number': phone_number,
                    'address': address,
                    'birthdate': birthdate,
                    'snils': snils,
                    'gender': gender,
                    'promocode': promocode_name,
                    'education': education,
                    'course_times': course_times,  # Pass course_times to the template
                })
            if promocode.is_available():
                messages.error(request, 'Данный промокод уже не действует.')
                return render(request, 'register.html', {
                    'email': email,
                    'username': username,
                    'phone_number': phone_number,
                    'address': address,
                    'birthdate': birthdate,
                    'snils': snils,
                    'gender': gender,
                    'promocode': promocode_name,
                    'education': education,
                    'course_times': course_times,  # Pass course_times to the template
                })

        if not email or not password or not username or not phone_number or not address or not birthdate or not snils or not gender:
            messages.error(request, 'Пожалуйста, заполните все обязательные поля.')
            return render(request, 'register.html', {
                'email': email,
                'username': username,
                'phone_number': phone_number,
                'address': address,
                'birthdate': birthdate,
                'snils': snils,
                'gender': gender,
                'promocode': promocode_name,
                'education': education,
                'course_times': course_times,  # Pass course_times to the template
            })

        try:
            birthdate_obj = timezone.datetime.strptime(birthdate, '%Y-%m-%d')
        except ValueError:
            messages.error(request, 'Значение даты рождения имеет неверный формат. Оно должно быть в формате YYYY-MM-DD.')
            return render(request, 'register.html', {
                'email': email,
                'username': username,
                'phone_number': phone_number,
                'address': address,
                'birthdate': birthdate,
                'snils': snils,
                'gender': gender,
                'promocode': promocode,
                'education': education,
                'course_times': course_times,  # Pass course_times to the template
            })

        time_to_beat = get_object_or_404(CourseTimeToBeat, id=time_to_beat_id)
        duration = time_to_beat.time.duration
        end_date = datetime.now() + duration


        user = CustomUser(email=email, username=username)
        user.set_password(password)
        user.save()

        user_reg = UserReg(
            user=user,
            username=username,
            phone_number=phone_number,
            address=address,
            birthdate=birthdate_obj,
            snils=snils,
            gender=gender,
            promocode=promocode,
            education=education,
            picture1=picture1,
            picture2=picture2,
            date_joined=timezone.now(),
            course=course,
            time_to_beat=time_to_beat,
            end_date=end_date,
        )
        user_reg.save()

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'Регистрация успешна!')
        return redirect('profile_view')

    return render(request, 'register.html', {
        'course_times': course_times,  # Pass course_times to the template
    })


def register_user_reg(request, course_id):
    if not request.user.is_authenticated:
        return redirect('register', course_id=course_id)

    user = get_object_or_404(CustomUser, id=request.user.id)

    if UserReg.objects.filter(user=user, course__id=course_id).exists():
        messages.error(request, 'Вы уже зарегистрированы на этот курс.')
        print("Вы уже зарегистрированы на этот курс.")
        return redirect('home')

    course = Course.objects.get(id=course_id)
    course_times = CourseTimeToBeat.objects.filter(course=course)

    if request.method == 'POST':
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        birthdate = request.POST.get('birthdate')
        snils = request.POST.get('snils')
        gender = request.POST.get('gender')
        promocode_name = request.POST.get('promocode')
        education = request.POST.get('education')
        picture1 = request.FILES.get('picture1')
        picture2 = request.FILES.get('picture2')
        time_to_beat_id = request.POST.get('time_to_beat')

        promocode = Promocode.objects.filter(name=promocode_name).first()

        if not username or not phone_number or not address or not birthdate or not snils or not gender:
            messages.error(request, 'Пожалуйста, заполните все обязательные поля.')
            return render(request, 'register_user_reg.html', {
                'user': user,
                'username': username,
                'phone_number': phone_number,
                'address': address,
                'birthdate': birthdate,
                'snils': snils,
                'gender': gender,
                'promocode': promocode_name,
                'education': education,
                'course_times': course_times,
            })
        print(not promocode_name)
        if promocode_name:
            if not promocode:
                messages.error(request, 'Данный промокод не существует проверьте правильность его написания.')
                return render(request, 'register_user_reg.html', {
                    'user': user,
                    'username': username,
                    'phone_number': phone_number,
                    'address': address,
                    'birthdate': birthdate,
                    'snils': snils,
                    'gender': gender,
                    'promocode': promocode_name,
                    'education': education,
                    'course_times': course_times,
                })
            
            if not promocode.is_available() and bool(promocode_name):
                messages.error(request, 'Данный промокод уже не действует.')
                return render(request, 'register_user_reg.html', {
                    'user': user,
                    'username': username,
                    'phone_number': phone_number,
                    'address': address,
                    'birthdate': birthdate,
                    'snils': snils,
                    'gender': gender,
                    'promocode': promocode_name,
                    'education': education,
                    'course_times': course_times,
                })

        try:
            birthdate_obj = timezone.datetime.strptime(birthdate, '%Y-%m-%d')
        except ValueError:
            messages.error(request, 'Значение даты рождения имеет неверный формат. Оно должно быть в формате YYYY-MM-DD.')
            return render(request, 'register_user_reg.html', {
                'user': user,
                'username': username,
                'phone_number': phone_number,
                'address': address,
                'birthdate': birthdate,
                'snils': snils,
                'gender': gender,
                'promocode': promocode_name,
                'education': education,
                'course_times': course_times,
            })
        time_to_beat = get_object_or_404(CourseTimeToBeat, id=time_to_beat_id)
        duration = time_to_beat.time.duration
        end_date = datetime.now() + duration
        user_reg = UserReg(
            user=user,
            username=username,
            phone_number=phone_number,
            address=address,
            birthdate=birthdate_obj,
            snils=snils,
            gender=gender,
            promocode=promocode,
            education=education,
            picture1=picture1,
            picture2=picture2,
            date_joined=timezone.now(),
            course=course,
            time_to_beat=time_to_beat,
            end_date=end_date,
        )
        user_reg.save()

        messages.success(request, 'Регистрация успешна! Вы можете войти в систему позже.')
        return redirect('profile_view')

    return render(request, 'register_user_reg.html', {
        'user': user,
        'username': user.username,
        'course_times': course_times,
    })


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile_view')  # Redirect to a home page or dashboard
        else:
            messages.error(request, 'Не правильный E-Mail или Пароль.')
    return render(request, 'login.html')
from django.shortcuts import render, redirect
from django.contrib.auth import logout


@login_required
def upload_files(request, course_id):
    user_reg = UserReg.objects.get(user=request.user, course_id=course_id)  # Ensure you're using course_id instead of course.id
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES, instance=user_reg)

        if form.is_valid():
            user_reg = form.save()  # Save the form and update the registration info
            print("Uploaded pictures:", user_reg.picture1, user_reg.picture2)  # Debugging output
            return redirect('home')  # Redirect to a success page or home
        else:
            print("Form errors:", form.errors)  # Print form errors for debugging

    else:
        form = FileUploadForm(instance=user_reg)  # Initialize the form with the user's registration info

    return render(request, 'uploadpics.html', {'form': form})



def user_logout(request):
    logout(request)
    return redirect('login')


def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def deleteacc(request):
    user_profile = get_object_or_404(CustomUser, user=request.user)
    user_profile.delete()
    request.user.delete()
    messages.success(request, "Your profile has been deleted successfully.")
    return redirect('home')


def profile_view(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    user_regs = user.registration_info.select_related('course', 'time_to_beat').all()

    courses_info = []
    paid_courses = []

    for reg in user_regs:
        print(reg)
        course = reg.course
        if reg.is_paid:
            paid_courses.append(course)

        # Check if pictures are uploaded
        pictures_uploaded = bool(reg.picture1 and reg.picture2)

        finished = True

        grades = CourseGrade.objects.filter(user=user, course=course).first()
        if grades:
            total_blocks = course.blocks
            grade_list = [
                grades.test_grade_1,
                grades.test_grade_2,
                grades.test_grade_3,
                grades.test_grade_4,
                grades.test_grade_5,
                grades.test_grade_6,
            ]
            relevant_grades = grade_list[:total_blocks]
            finished = not any(g == 0.00 for g in relevant_grades)
            total_grades = sum(relevant_grades)

            if total_blocks > 0:
                percentage = (total_grades / (total_blocks * 100)) * 100  # Assuming each test is out of 100
            else:
                percentage = 0
        else:
            percentage = 0


        if percentage >= 90:
            grade = 5
        elif percentage >= 80:
            grade =  4
        elif percentage >= 70:
            grade = 3
        elif percentage <= 10:
            grade = "Пока не пройден"
        else:
            grade = "Неудовлетворительно"

        if finished == False:
            grade = "Пока не пройден"

        print(reg.time_to_beat)
        price_with_discoint = reg.time_to_beat.price * (reg.promocode.percent / 100) if reg.promocode else None
        courses_info.append({
            'course': course,
            'time_to_beat_info': reg.time_to_beat,
            'is_approved': reg.is_approved,
            'is_sended': reg.is_sended,
            'scans_approved': reg.scans_approved,
            'pictures_uploaded': pictures_uploaded,
            'percentage': percentage,
            'grade': grade,
            'price_with_discount': price_with_discoint
        })

    return render(request, 'profile.html', {
        'user': user,
        'username': user.username,
        'courses_info': courses_info,
        'paid_courses': paid_courses
    })



def course_view(request, course_id):
    user = get_object_or_404(CustomUser, id=request.user.id)

    course = get_object_or_404(Course, id=course_id)  # Use course_id from the URL

    return render(request, 'course.html', {
        'course': course,
        'username': user.username,
        'user': user,

                                           })


def buy_course(request):
    return render(request, 'buy_course.html')


def get_text_grade(percentage):

    if percentage >= 90:
        return 5
    elif percentage >= 80:
        return 4
    elif percentage >= 70:
        return 3
    elif percentage <= 5:
        return "Пока не пройден"
    else:
        return "Неудовлетворительно"



def course_files(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user

    user_reg = UserReg.objects.filter(user=user, course=course).first()
    course_grades = CourseGrade.objects.filter(user=user, course=course).first()

    if user_reg is None or not user_reg.is_paid:
        price = user_reg.time_to_beat.price if user_reg and user_reg.time_to_beat else 1000
        payment_url = reverse('create_payment', args=[price, user_reg.id if user_reg else 0])
        return redirect(payment_url)

    if course_grades:
        course_grade1 = get_text_grade(course_grades.test_grade_1)
        course_grade2 = get_text_grade(course_grades.test_grade_2)
        course_grade3 = get_text_grade(course_grades.test_grade_3)
        course_grade4 = get_text_grade(course_grades.test_grade_4)
        course_grade5 = get_text_grade(course_grades.test_grade_5)
        course_grade6 = get_text_grade(course_grades.test_grade_6)

    else:
        course_grade1 = course_grade2 = course_grade3 = course_grade4 = course_grade5 = course_grade6 = "Пока не пройден"

    block_1_exercises = CourseExercise.objects.filter(course=course, block_number=1)
    block_2_exercises = CourseExercise.objects.filter(course=course, block_number=2)
    block_3_exercises = CourseExercise.objects.filter(course=course, block_number=3)
    block_4_exercises = CourseExercise.objects.filter(course=course, block_number=4)
    block_5_exercises = CourseExercise.objects.filter(course=course, block_number=5)
    block_6_exercises = CourseExercise.objects.filter(course=course, block_number=6)



    course_blocks = course.blocks



    return render(request, 'course_files.html', {
        'course': course,
        'block_1_exercises': block_1_exercises,
        'block_2_exercises': block_2_exercises,
        'block_3_exercises': block_3_exercises,
        'block_4_exercises': block_4_exercises,
        'block_5_exercises': block_5_exercises,
        'block_6_exercises': block_6_exercises,
        'test_grade_1': course_grade1,
        'test_grade_2': course_grade2,
        'test_grade_3': course_grade3,
        'test_grade_4': course_grade4,
        'test_grade_5': course_grade5,
        'test_grade_6': course_grade6,
        'course_id': course_id,
        'howmuch_blocks' : course_blocks,
        'username': user.username,
        'user': user,

    })

def take_test(request, block_number, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = get_object_or_404(CustomUser, id=request.user.id)
    user_reg = get_object_or_404(UserReg, course=course, user=user)
    test = get_object_or_404(Test, course=course, block_number=block_number)

    questions = test.questions.all()

    if request.method == 'POST':
        score = 0
        for question in questions:
            # The POST data will have keys like 'answers_<question.id>'
            user_answer = request.POST.get(f'answers_{question.id}')
            if user_answer:
                try:
                    user_answer = int(user_answer)
                except ValueError:
                    continue  # invalid answer format, skip

                # Check which answer option matches user_answer and if it's correct
                if user_answer == 1 and question.is_1correct:
                    score += 1
                elif user_answer == 2 and question.is_2correct:
                    score += 1
                elif user_answer == 3 and question.is_3correct:
                    score += 1
                elif user_answer == 4 and question.is_4correct:
                    score += 1

        total_questions = questions.count()
        percentage = (score / total_questions) * 100 if total_questions > 0 else 0

        if percentage >= 90:
            grade = 5
        elif percentage >= 80:
            grade = 4
        elif percentage >= 70:
            grade = 3
        else:
            grade = "неудовлетворительно"

        course_grade, created = CourseGrade.objects.get_or_create(user=user, course=course)
        grade_field = f'test_grade_{test.block_number}'

        if hasattr(course_grade, grade_field):
            setattr(course_grade, grade_field, percentage)
            course_grade.save()

            blocks = course_grade.course.blocks
            if int(test.block_number) == int(blocks):
                if percentage >= 70:
                    user_reg.attestation_finished = True
                    user_reg.save()
                else:
                    print("Percentage is below passing threshold")

        return render(request, 'test_result.html', {
            'score': score,
            'total': total_questions,
            'percentage': percentage,
            'grade': grade,
            'course': course,
        })

    return render(request, 'take_test.html', {
        'test': test,
        'questions': questions,
        'user': user,
        'username': user.username,
    })


def purchase_course(request, course_id):
    user = get_object_or_404(CustomUser, id=request.user.id)
    course = get_object_or_404(Course, id=course_id)  # Use course_id from the URL

    user.courses.add(course)
    user.save()
    return render(request, 'course.html', {'user': user, 'username': user.username, 'course': course})

def pdf_view(request, file_name):

    file_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', file_name)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as pdf:  # Open the file in binary mode
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename={file_name}'
            return response
    else:
        raise Http404("File not found")



# @login_required
# def check_users(request):
#     if not request.user.is_staff:
#         return render(request, '403.html')

#     all_users = UserReg.objects.select_related('user', 'course').all()

#     users_paid = list(all_users.filter(is_paid=True))

#     users_docs_on_check = [user for user in all_users if user.picture1 and user.picture2 and user.is_paid]
#     users_docs_checked = [user for user in all_users if
#                           user.picture1 and user.picture2 and user.is_paid and user.scans_approved]
#     users_sended = [user for user in all_users if
#                     user.picture1 and user.picture2 and user.is_paid and user.scans_approved and user.is_sended]
#     users_recieved = [user for user in all_users if
#                       user.picture1 and user.picture2 and user.is_paid and user.scans_approved and user.is_sended and user.recieved_docs]
#     users_finished = [user for user in all_users if
#                       user.picture1 and user.picture2 and user.is_paid and user.scans_approved and user.is_sended and user.recieved_docs and user.attestation_finished]

#     # Now remove duplicates from previous lists
#     users_recieved = [user for user in users_recieved if user not in users_finished]
#     users_sended = [user for user in users_sended if user not in users_finished and user not in users_recieved]
#     users_docs_checked = [user for user in users_docs_checked if user not in users_finished and user not in users_recieved and user not in users_sended]
#     users_docs_on_check = [user for user in users_docs_on_check if user not in users_finished and user not in users_recieved and user not in users_sended and user not in users_docs_checked]
#     users_paid = [user for user in users_paid if user not in users_finished and user not in users_recieved and user not in users_sended and user not in users_docs_checked and user not in users_docs_on_check]
#     print({
#         'all_users': all_users,
#         'users_paid': users_paid,
#         'users_docs_on_check': users_docs_on_check,
#         'users_docs_checked': users_docs_checked,
#         'users_sended': users_sended,
#         'users_recieved': users_recieved,
#         'users_finished': users_finished,
#     })
#     return render(request, 'check_users.html', {
#         'all_users': all_users,
#         'users_paid': users_paid,
#         'users_docs_on_check': users_docs_on_check,
#         'users_docs_checked': users_docs_checked,
#         'users_sended': users_sended,
#         'users_recieved': users_recieved,
#         'users_finished': users_finished,
#     })

STATUS_LABELS = {
    "new": "Новая заявка",
    "paid": "Оплачен",
    "docs_pending": "Документы на проверке",
    "docs_verified": "Документы проверены",
    "attestation": "Аттестация",
    "sent": "Отправлен почтой РФ",
}

def _docs_attached_q():
    # Есть хотя бы один файл (учитываем NULL и пустые строки)
    return (
        (Q(picture1__isnull=False) & ~Q(picture1="")) |
        (Q(picture2__isnull=False) & ~Q(picture2=""))
    )


STATUS_FILTERS = {
    "new": Q(is_paid=False),
    "paid": Q(is_paid=True) & ~_docs_attached_q(),
    "docs_pending": Q(is_paid=True) & _docs_attached_q() & Q(scans_approved=False),
    "docs_verified": Q(is_paid=True) & Q(scans_approved=True) & Q(attestation_finished=False),
    "attestation": Q(is_paid=True) & Q(scans_approved=True) & Q(attestation_finished=True) & Q(is_sended=False),
    "sent": Q(is_paid=True) & Q(scans_approved=True) & Q(attestation_finished=True) & Q(is_sended=True),
}

def _compute_status_code(obj: UserReg) -> str:
    docs_attached = bool(obj.picture1) or bool(obj.picture2)

    if not obj.is_paid:
        return "new"
    if obj.is_paid and not docs_attached:
        return "paid"
    if obj.is_paid and docs_attached and not obj.scans_approved:
        return "docs_pending"
    if obj.is_paid and obj.scans_approved and not obj.attestation_finished:
        return "docs_verified"
    if obj.is_paid and obj.scans_approved and obj.attestation_finished and not obj.is_sended:
        return "attestation"
    return "sent"


def _resolve_course_name_field() -> str:
    """
    Пытаемся понять, как называется поле у модели Course: name или title.
    Если ни одного нет — сортируем по id курса.
    """
    CourseModel = UserReg._meta.get_field("course").remote_field.model
    try:
        CourseModel._meta.get_field("name")
        return "course__name"
    except Exception:
        pass
    try:
        CourseModel._meta.get_field("title")
        return "course__title"
    except Exception:
        pass
    return "course__id"


def _filtered_sorted_qs(request):
    status_param = (request.GET.get("status") or "").strip().lower()
    sort_param   = (request.GET.get("sort") or "").strip().lower()

    qs = UserReg.objects.select_related("user", "course")

    # фильтр по статусу
    if status_param:
        q = STATUS_FILTERS.get(status_param)
        if q is not None:
            qs = qs.filter(q)
        else:
            qs = qs.none()

    # сортировка по курсу
    if sort_param == "up":
        qs = qs.order_by('course__category')  # вторичный ключ для стабильности
    elif sort_param == "down":
        qs = qs.order_by("-course__category")
    else:
        qs = qs.order_by("-date_joined", "id")  # сортировка по умолчанию

    return qs, status_param, sort_param


# STATUS_LABELS, STATUS_FILTERS, _compute_status_code

def _docs_attached(obj: UserReg) -> bool:
    return bool(obj.picture1) or bool(obj.picture2)


@login_required
def check_users(request):
    if not request.user.is_staff:
        return render(request, '403.html')
    
    qs, status_param, sort_param = _filtered_sorted_qs(request)

    all_users = []
    items = []
    for obj in qs:
        code = _compute_status_code(obj)
        items.append(
            {
                "obj": obj,
                "status_code": code,
                "status_label": STATUS_LABELS[code],
            }
        )
        all_users.append(obj)

    print({
        'all_users': all_users,
    })
    return render(request, 'check_users_copy.html', {
        'all_users': all_users,
        'status': status_param
    })


def userregs_export_xlsx(request):
    qs, status_param, sort_param = _filtered_sorted_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "Заявки"

    headers = [
        "ID",
        "ФИО",
        "Курс",
        "Цена",
        "Оплачен",
        "Документы прикреплены",
        "Документы проверены",
        "Аттестация пройдена",
        "Отправлен почтой РФ",
        "Статус (ярлык)",
        "Дата регистрации",
        "Дата завершения",
        "Телефон/Email",
    ]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    ws.freeze_panes = "A2"

    def yn(v: bool) -> str:
        return "Да" if v else "Нет"

    for obj in qs.iterator():
        print(obj.course.category, obj.course.category)
        code = _compute_status_code(obj)
        row = [
            obj.id,
            obj.username,
            str(obj.course.content),
            str(obj.price_with_promocode()),
            yn(obj.is_paid),
            yn(_docs_attached(obj)),
            yn(obj.scans_approved),
            yn(obj.attestation_finished),
            yn(obj.is_sended),
            f"{STATUS_LABELS.get(code, code)}",
            timezone.localtime(obj.date_joined).strftime("%d.%m.%Y %H:%M") if obj.date_joined else "",
            timezone.localtime(obj.end_date).strftime("%d.%m.%Y %H:%M") if obj.end_date else "",
            (obj.phone_number or ""),
        ]
        print(row)
        ws.append(row)

    # Небольшие ширины колонок
    widths = [6, 35, 32, 10, 22, 20, 18, 20, 24, 20, 20, 24]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[chr(64 + i) if i <= 26 else f"A{chr(64 + i - 26)}"].width = w

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    filename = f"userregs_{status_param or 'all'}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    resp = HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp

def uc_pdf(request):

    file_name = 'Пользовательское соглашение.pdf'
    file_path = os.path.join(settings.MEDIA_ROOT, 'pdf_doc', file_name)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as pdf:  # Open the file in binary mode
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename={file_name}'
            return response
    else:
        raise Http404("File not found")


def pc_pdf(request):

    file_name = 'Политика конфиденциальности.pdf'
    file_path = os.path.join(settings.MEDIA_ROOT, 'pdf_doc', file_name)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as pdf:  # Open the file in binary mode
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename={file_name}'
            return response
    else:
        raise Http404("File not found")














def admin_panel(request):
    user = request.user if request.user.is_authenticated else None
    username = user.username if user else None

    if not user or not user.is_staff:
        return render(request, '403.html')  # Render a 403 Forbidden page or redirect


    courses = Course.objects.prefetch_related('coursetimetobeat_set').all()
    category = Category.objects.all()
    topic = Topic.objects.all()
    term_of_study = Term_of_study.objects.all()

    return render(request, 'admin_panel.html', {
        'courses': courses,
        'category': category,
        'topic': topic,
        'term_of_study': term_of_study,
        'username': username,
        'user': user,

    })

def add_course(request):
    user = request.user if request.user.is_authenticated else None
    username = user.username if user else None

    if not user or not user.is_staff:
        return render(request, '403.html')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_panel')  # or wherever you want to redirect
    else:
        form = CourseForm()

    return render(request, 'add_course.html', {
        'form': form,
        'username': username,
        'user': user,
        'admin_status': True
    })


def course_administration(request, course_id):
    user = request.user if request.user.is_authenticated else None
    admin_status = user.is_staff if user else False
    username = user.username if user else None

    if not user or not user.is_staff:
        return render(request, '403.html')

    course = get_object_or_404(Course, id=course_id)
    exercises = CourseExercise.objects.filter(course=course)
    time_prices = CourseTimeToBeat.objects.filter(course=course)
    tests = Test.objects.filter(course=course)

    dont_show_header = True

    return render(request, 'course_administration.html', {
        'course': course,
        'exercises': exercises,
        'time_prices': time_prices,
        'tests': tests,
        'username': username,
        'user': user,
        'admin_status': admin_status,
        'dont_show_header' : dont_show_header
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.forms import inlineformset_factory

def create_test_questions(request, test_id):
    user = request.user if request.user.is_authenticated else None
    admin_status = user.is_staff if user else False
    username = user.username if user else None

    if not user or not admin_status:
        return render(request, '403.html')

    test = get_object_or_404(Test, id=test_id)

    QuestionInlineFormSet = inlineformset_factory(
        Test, Question,
        form=QuestionForm,
        extra=0 if test.questions.exists() else test.questions_number or 1,
        can_delete=False
    )

    if request.method == 'POST':
        question_formset = QuestionInlineFormSet(request.POST, instance=test)

        if question_formset.is_valid():
            questions = question_formset.save(commit=False)

            for i, q in enumerate(questions, start=1):
                q.position = i
                q.test = test
                q.save()


            for q in question_formset.deleted_objects:
                q.delete()

            return redirect('course_administration', course_id=test.course.id)
    else:
        question_formset = QuestionInlineFormSet(instance=test)

    return render(request, 'create_test_questions.html', {
        'test': test,
        'question_formset': question_formset,
        'username': username,
        'user': user,
        'admin_status': admin_status,
    })



Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def create_payment(request, amount, user_reg_id):

    idempotence_key = str(uuid.uuid4())
    amount = f"{amount:.2f}"

    user_reg = get_object_or_404(UserReg, id=user_reg_id)
    if user_reg.promocode:
        if user_reg.promocode.is_available():
            percent_mul = 1 - user_reg.promocode.percent / 100
            amount = f"{float(amount) * percent_mul:.2f}"
    user = getattr(request, "user", None)
    email = getattr(user, "email", "noemail@example.com")
    full_name = user.username if user else None

    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": settings.YOOKASSA_RETURN_URL
        },
        "capture": True,
        "description": f"Оплата курса для пользователя {full_name}",
        "receipt": {
            "customer": {
                "full_name": full_name,
                "email": email
            },
            "items": [
                {
                    "description": "Оплата курса",
                    "quantity": 1.0,
                    "amount": {
                        "value": amount,
                        "currency": "RUB"
                    },
                    "vat_code": 1,
                    "payment_mode": "full_prepayment",
                    "payment_subject": "service"
                }
            ]
        }
    }, idempotence_key)

    PaymentLog.objects.create(
        payment_id=payment.id,
        status=payment.status,
        amount=amount,
        is_paid=False,
        user_reg=user_reg
    )

    return redirect(payment.confirmation.confirmation_url)


def payment_return(request):
    print("money")
    return redirect('profile_view')



@csrf_exempt
def yookassa_webhook(request):
    if request.method != "POST":
        return HttpResponseForbidden()

    data = json.loads(request.body)

    if data.get('event') == 'payment.succeeded':
        payment_id = data['object']['id']

        try:
            payment_log = PaymentLog.objects.get(payment_id=payment_id)
        except PaymentLog.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Payment not found'}, status=404)

        payment_log.status = 'succeeded'
        payment_log.is_paid = True
        payment_log.save()

        user_reg = payment_log.user_reg
        if user_reg:
            user_reg.is_paid = True
            user_reg.save()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'ignored'})
