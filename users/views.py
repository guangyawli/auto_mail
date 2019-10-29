#from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.models import User
import xlrd
from .models import Tcourse, Emails, MailServer, Tprofile
from django.http import HttpResponse, HttpResponseRedirect
from users.forms import UploadExcelForm
# Email
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template import loader
from tset1.settings import STATIC_ROOT
import datetime


def ximport(request):
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            wb = xlrd.open_workbook(filename=None, file_contents=request.FILES['excel'].read())
            table = wb.sheets()[0]
            row = table.nrows
            for i in range(1, row):
                col = table.row_values(i)
                if not User.objects.filter(username=col[3], email=col[4]).exists():
                    tmp_user = User.objects.create(username=col[3], email=col[4])
                else:
                    tmp_user = User.objects.get(username=col[3], email=col[4])

                if not Tcourse.objects.filter(dash_id=col[0]).exists():
                    tmp_course = Tcourse.objects.create(dash_id=col[0], course_id=col[1], course_name=col[2])
                else:
                    tmp_course = Tcourse.objects.get(dash_id=col[0], course_id=col[1])

                if tmp_user not in Tcourse.objects.get(course_id=col[1]).tstaff.all():
                    Tcourse.objects.get(course_id=col[1]).tstaff.add(tmp_user)

            err_msg = 'import data ok'
            return render(request, "ihome.html", locals())
        else:
            err_msg = 'invalid file type'
            return render(request, "ihome.html", locals())

    return render(request, "uploadfile.html", locals())


def send_mails(request):
    if request.user.is_staff is False:
        return HttpResponse(' No permission ! ')
    else:
        tmp_server = MailServer.objects.get(id=1)

        conn = get_connection()
        conn.username = tmp_server.m_user  # username
        conn.password = tmp_server.m_password  # password
        conn.host = tmp_server.m_server  # mail server
        conn.open()

        all_courses = Tcourse.objects.all()
        print(datetime.date.today())
        for courses in all_courses:
            tmp_users = courses.tstaff.all()

            target_mails = []
            for tmp_user in tmp_users:
                target_mails.append(tmp_user.email)

            print(target_mails)
            print(courses.course_id)

            test_from = Emails.objects.get(e_status='default').e_from
            test_title = Emails.objects.get(e_status='default').e_title

            # for_cancel_url = 'http://'+request.get_host()+'/cancel_inform'
            # print(for_cancel_url)
            context = {'insight_url': 'https://insights.openedu.tw/courses/',
                       'course_id': courses.course_id,
                       'course_name': courses.course_name
                       }
            print(courses.course_name)
            email_template_name = 'insight_dash.html'
            t = loader.get_template(email_template_name)

            mail_list = target_mails

            subject, from_email, to = test_title, test_from, mail_list
            html_content = t.render(dict(context))  # str(test_content)
            msg = EmailMultiAlternatives(subject, html_content, from_email, bcc=to)
            msg.attach_alternative(html_content, "text/html")
            msg.attach_file(STATIC_ROOT+'insights_readme.pdf')
            conn.send_messages([msg, ])  # send_messages发送邮件

        conn.close()

        err_msg = 'send mail ok'
        return render(request, "ihome.html", locals())


def send_mails_ii(request):
    # if request.user.is_staff is False:
    #     return HttpResponse(' No permission ! ')
    # else:
    #     tmp_users = User.objects.all()
    #     target_mails = []
    #     for tmp_user in tmp_users:
    #         target_mails.append(tmp_user.email)
    #
    #     # print(target_mails)
    #     test_from = Emails.objects.get(e_status='default').e_from
    #     test_title = Emails.objects.get(e_status='default').e_title
    #     test_content = Emails.objects.get(e_status='default').e_content
    #
    #     mail_list = target_mails
    #
    #     tmp_server = MailServer.objects.get(id=1)
    #
    #     conn = get_connection()
    #     conn.username = tmp_server.m_user              # username
    #     conn.password = tmp_server.m_password          # password
    #     conn.host = tmp_server.m_server                # mail server
    #     conn.open()
    #
    #     subject, from_email, to = test_title, test_from, mail_list
    #     html_content = str(test_content)
    #     msg = EmailMultiAlternatives(subject, html_content, from_email, bcc=to)
    #     msg.attach_alternative(html_content, "text/html")
    #
    #     conn.send_messages([msg, ])  # send_messages发送邮件
    #     conn.close()

        err_msg = '此功能停用，請洽管理員'
        return render(request, "ihome.html", locals())


def home(request):
    return render(request, "ihome.html", locals())


def cancel_inform(request):
    return HttpResponse('此功能停用，請洽管理員')

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
