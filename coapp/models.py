from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.utils.text import slugify as django_slugify
from datetime import timedelta, datetime
from django.core.validators import MaxValueValidator

def custom_slugify(value):

    translit_map = {
        'а': 'a', 'А': 'a', 'б': 'b', 'Б': 'b', 'в': 'v', 'В': 'v', 'г': 'g', 'Г': 'g',
        'д': 'd', 'Д': 'd', 'е': 'e', 'Е': 'e', 'ё': 'yo', 'Ё': 'yo', 'ж': 'zh', 'Ж': 'zh',
        'з': 'z', 'З': 'z', 'и': 'i', 'И': 'i', 'й': 'y', 'Й': 'y', 'к': 'k', 'К': 'k',
        'л': 'l', 'Л': 'l', 'м': 'm', 'М': 'm', 'н': 'n', 'Н': 'n', 'о': 'o', 'О': 'o',
        'п': 'p', 'П': 'p', 'р': 'r', 'Р': 'r', 'с': 's', 'С': 's', 'т': 't', 'Т': 't',
        'у': 'u', 'У': 'u', 'ф': 'f', 'Ф': 'f', 'х': 'kh', 'Х': 'kh', 'ц': 'ts', 'Ц': 'ts',
        'ч': 'ch', 'Ч': 'ch', 'ш': 'sh', 'Ш': 'sh', 'щ': 'shch', 'Щ': 'shch', 'ъ': '',
        'Ъ': '', 'ы': 'y', 'Ы': 'y', 'ь': '', 'Ь': '', 'э': 'e', 'Э': 'e', 'ю': 'yu', 'Ю': 'yu',
        'я': 'ya', 'Я': 'ya'
    }


    for cyrillic, latin in translit_map.items():
        value = value.replace(cyrillic, latin)


    return django_slugify(value)


class Course(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name="Курс")
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, verbose_name="Направление")
    # test_questions = models.PositiveIntegerField(verbose_name="Количество вопросов в тесте")
    content = models.TextField(blank=True, verbose_name="Тема")


    actual = models.BooleanField(default=True)
    blocks = models.PositiveIntegerField(verbose_name="Сколько блоков с материалами будет в этом курсе")
    pdf_1 = models.FileField(upload_to='pdfs/', verbose_name="договор (Формат PDF)", blank=True, null=True)
    pdf_2 = models.FileField(upload_to='pdfs/', verbose_name="учебный план (Формат PDF)", blank=True, null=True)
    pdf_3 = models.FileField(upload_to='pdfs/', verbose_name="программа обучения (Формат PDF)", blank=True, null=True)

    def __str__(self):
        return f"Course {self.id} - {self.content[:20]}"

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курс'
        ordering = ['id']


class CourseExercise(models.Model):
    name = models.CharField(max_length=100, verbose_name="Подпись которая будет отображаться с файлом")
    pdf_file = models.FileField(upload_to='pdfs/', verbose_name="Файл (Формат PDF)")
    course = models.ForeignKey('Course', on_delete=models.CASCADE, verbose_name="Курс к которому принадлежит документ")
    block_number = models.PositiveIntegerField(verbose_name="Номер блока")

    def __str__(self):
        return str(self.course)
    class Meta:
        verbose_name = "Материалы для курса"
        verbose_name_plural = "Материалы для курса"

class CourseTimeToBeat(models.Model):
    time = models.ForeignKey('Term_of_study', on_delete=models.CASCADE, verbose_name="Срок")
    price = models.PositiveIntegerField(verbose_name="Цена")
    course = models.ForeignKey('Course', on_delete=models.CASCADE, verbose_name="Курс к которому принадлежит документ")


    def __str__(self):
        return str(self.time) + ";   Цена: " + str(self.price)
    class Meta:
        verbose_name = "Сроки для курса"
        verbose_name_plural = "Сроки для курса"


class Test(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, verbose_name="Курс к которому принадлежит тест")
    block_number = models.PositiveIntegerField(verbose_name="Номер блока", null=True)
    questions_number = models.PositiveIntegerField(verbose_name="Количество вопросов", null=True)

    def __str__(self):
        return f"Тест для {self.course} - Блок {self.block_number}"

    class Meta:
        verbose_name = "свТест"
        verbose_name_plural = "Тесты"

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")
    position = models.PositiveIntegerField(verbose_name="Номер вопроса", default=1)
    question = models.CharField(max_length=200, default="Вопрос", verbose_name="Вопрос",)
    text_1 = models.CharField(max_length=200, verbose_name="Вариант ответа", default="Ответ 1")
    is_1correct = models.BooleanField(default=False, verbose_name="Правильный ответ")
    text_2 = models.CharField(max_length=200, verbose_name="Вариант ответа", default="Ответ 2")
    is_2correct = models.BooleanField(default=False, verbose_name="Правильный ответ")
    text_3 = models.CharField(max_length=200, verbose_name="Вариант ответа", default="Ответ 3")
    is_3correct = models.BooleanField(default=False, verbose_name="Правильный ответ")
    text_4 = models.CharField(max_length=200, verbose_name="Вариант ответа", default="Ответ 4")
    is_4correct = models.BooleanField(default=False, verbose_name="Правильный ответ")

    def __str__(self):
        return f"{self.test} — Вопрос {self.position}"

    class Meta:
        verbose_name = "Тесты: Вопрос"
        verbose_name_plural = "Тесты: Вопросы"


class CourseGrade(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='course_grades', verbose_name="Пользователь")
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='grades', verbose_name="Курс")

    test_grade_1 = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Оценка за первый блок")
    test_grade_2 = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Оценка за второй блок")
    test_grade_3 = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Оценка за третий блок")
    test_grade_4 = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Оценка за четвертый блок")
    test_grade_5 = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Оценка за пятый блок")
    test_grade_6 = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Оценка за шестой блок")

    class Meta:
        verbose_name = "Оценки за курс"
        verbose_name_plural = "Оценки за курсы"
    
    def __str__(self):
        return f"{self.user.email} - {self.course}"


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=100, unique=True, verbose_name="E-mail")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Личный кабинет"
        verbose_name_plural = "Личный кабинет"


class Promocode(models.Model):
    name = models.TextField(verbose_name="Название промокода вот")
    percent = models.PositiveIntegerField(verbose_name="Процент скидки промокода", validators=[MaxValueValidator(100),])
    expires_at = models.DateTimeField(verbose_name="Время окончания промокода")

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return f"{self.name} - {self.percent} - {self.expires_at}"
    
    def is_available(self):
        return datetime.now().replace(tzinfo=None) <= self.expires_at.replace(tzinfo=None)


class UserReg(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='registration_info')
    username = models.CharField(max_length=50, unique=False, verbose_name="Полные ФИО обучаемого")
    phone_number = models.CharField(max_length=100, verbose_name="Номер телефона или адрес электронной почты", blank=True)
    address = models.CharField(max_length=100, verbose_name="Адрес доставки", blank=True)
    birthdate = models.DateField(verbose_name="Дата вашего рождения", null=True)
    snils = models.CharField(max_length=100, verbose_name="СНИЛС(11 чисел)", blank=True)
    time_to_beat = models.ForeignKey('CourseTimeToBeat', on_delete=models.CASCADE, verbose_name="Срок курса",
                                     blank=True, null=True)
    GENDER_CHOICES = [
        ('male', 'Мужчина'),
        ('female', 'Женщина'),
    ]

    gender = models.CharField(
        max_length=6,
        choices=GENDER_CHOICES,
        verbose_name="Пол",
        blank=True,
        null=True
    )

    promocode = models.ForeignKey(Promocode, on_delete=models.SET_NULL, verbose_name="Промокод", null=True, blank=True)

    EDUCATION_CHOICES = [
        ('basic', 'Основное общее (5-9 классы)'),
        ('secondary', 'Среднее общее (10-11 классы)'),
        ('specialized', 'Среднее специальное образование'),
        ('higher', 'Высшее образование'),
    ]

    education = models.CharField(
        max_length=12,
        choices=EDUCATION_CHOICES,
        verbose_name="Уровень образования",
        blank=True,
        null=True
    )

    picture1 = models.ImageField(upload_to='profile_pictures/', blank=True, null=True,
                                 verbose_name="Диплом о высшем или среднем образовании (JPG/JPEG/PNG)")
    picture2 = models.ImageField(upload_to='profile_pictures/', blank=True, null=True,
                                 verbose_name="Документ о смене фамилии (JPG/JPEG/PNG)")

    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Дата регистрации")
    end_date = models.DateTimeField(verbose_name="Дата завершения")
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='purchased_by', blank=True, verbose_name="Курс")
    is_paid= models.BooleanField(default=False, verbose_name="Курс оплачен")

    is_approved = models.BooleanField(default=False, verbose_name="Введенные при регистрации данные проверены")
    scans_approved = models.BooleanField(default=False, verbose_name="Сканы документов проверены")

    is_sended= models.BooleanField(default=False, verbose_name="Отправили почтой диплом")
    recieved_docs = models.BooleanField(default=False, verbose_name="Получил диплом")
    attestation_finished = models.BooleanField(default=False, verbose_name="Аттестация пройдена")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Профиль к курсу"
        verbose_name_plural = "Профиль к курсу"

class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="Как будет выглядеть ссылка (Латиница; Не обязательно к заполнению, опционально.)")
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = custom_slugify(self.name)
            slug = base_slug
            counter = 1


            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "фильтрация:  Все курсы"
        verbose_name_plural = "фильтрация:  Все курсы"



class Topic(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="Как будет выглядеть ссылка (Латиница; Не обязательно к заполнению, опционально.)")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = custom_slugify(self.name)
            slug = base_slug
            counter = 1


            while Topic.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "фильтрация:  Направление"
        verbose_name_plural = "фильтрация:  Направление"





class Term_of_study(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название для вывода на главной странице")
    duration = models.DurationField(default=timedelta(hours=120), verbose_name="Продолжительность обучения")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "фильтрация:  Сроки обучения"
        verbose_name_plural = "фильтрация:  Сроки обучения"




class PaymentLog(models.Model):
    payment_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    user_reg = models.ForeignKey(UserReg, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Payment {self.payment_id} - {self.status}"
