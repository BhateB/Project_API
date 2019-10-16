from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

OWNERS = [
    'niti.p@consultadd.com',
    'nisha.k@consultadd.com',
    'shruti.u@consultadd.com'
    'bharat.b@consultadd.com',
    'siddharth.g@consultadd.com',
]


@shared_task
def send_email(mail_data):
    from_email = 'hire@consultadd.com'
    body = render_to_string(mail_data["template"], mail_data["context"])
    msg = EmailMultiAlternatives(subject=mail_data["subject"],
                                 body=body,
                                 from_email=from_email,
                                 to=mail_data["to"], )

    body = render_to_string(mail_data["template"], mail_data["context"])
    msg.attach_alternative(body, 'text/html')
    msg.send()


@shared_task
def send_email_attachment(mail_data):
    from_email = 'hire@consultadd.com'
    body = render_to_string(mail_data["template"], mail_data["context"])
    msg = EmailMultiAlternatives(subject=mail_data["subject"],
                                 body=body,
                                 from_email=from_email,
                                 to=mail_data["to"], )

    body = render_to_string(mail_data["template"], mail_data["context"])
    msg.attach_alternative(body, 'text/html')
    msg.attach_file(mail_data["attachments"])
    msg.send()


@shared_task
def send_email_attachment_multiple(mail_data):
    from_email = 'hire@consultadd.com'
    body = render_to_string(mail_data["template"], mail_data["context"])
    msg = EmailMultiAlternatives(subject=mail_data["subject"],
                                 body=body,
                                 from_email=from_email,
                                 to=mail_data["to"], )

    body = render_to_string(mail_data["template"], mail_data["context"])
    msg.attach_alternative(body, 'text/html')
    for i in mail_data["attachments"]:
        msg.attach_file(i)
    msg.send()
