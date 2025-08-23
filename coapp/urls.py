from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *


urlpatterns = [
    path('', home, name='home'),

    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('deleteacc/', deleteacc, name='deleteacc'),
    path('profile_view/', profile_view, name='profile_view'),
    path('course/<int:course_id>/', course_view, name='course_view'),
    path('register/<int:course_id>/', register, name='register'),
    path('register_user_reg/<int:course_id>/', register_user_reg, name='register_user_reg'),
    path('purchase_course/<int:course_id>/', purchase_course, name='purchase_course'),
    path('media/pdfs/<str:file_name>', pdf_view, name='pdf_view'),

    path('upload_files/<int:course_id>/', upload_files, name='upload_files'),
    path('tests/<int:course_id>/<int:block_number>/', take_test, name='take_test'),
    path('files/<int:course_id>/', course_files, name='course_files'),
    path('buy_course/', buy_course, name='buy_course'),

    path('add_course/', add_course, name='add_course'),

    path('check_users/', check_users, name='check_users'),
    path("check_users/export-xlsx/", userregs_export_xlsx, name="userregs_export_xlsx"),

    path('uc_pdf/', uc_pdf, name='uc_pdf'),
    path('pc_pdf/', pc_pdf, name='pc_pdf'),
    path('admin_panel/', admin_panel, name='admin_panel'),
    path('course_administration/<int:course_id>/', course_administration, name='course_administration'),

    path('test/<int:test_id>/create/', create_test_questions, name='create_test_questions'),

    path("payment/create/<int:amount>/<int:user_reg_id>/", create_payment, name="create_payment"),

    path("payment/return/", payment_return, name="payment_return"),
    path("payment/webhook/", yookassa_webhook, name="yookassa_webhook"),

    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="password_reset_form.html",
            # email_template_name="password_reset_email.txt",
            # html_email_template_name="password_reset_email.html",  # опционально
            # subject_template_name="password_reset_subject.txt",
            success_url="/password-reset/done/",
            from_email="tanya22022002@yandex.ru",  # поменяйте
        ),
        name="password_reset",
    ),

    # Сообщение «письмо отправлено»
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_reset_done.html"
        ),
        name="password_reset_done",
    ),

    # Переход по ссылке из письма: ввод нового пароля
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html",
            success_url="/reset/complete/",
        ),
        name="password_reset_confirm",
    ),

    # Готово
    path(
        "reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

]

