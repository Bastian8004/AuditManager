from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils.timezone import now
from .forms import *
from .models import *
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, auth
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from email.utils import make_msgid
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from email.utils import make_msgid
import os

def error_404_view(request, exception):
    assert isinstance(request, HttpRequest)
    return render(request, '404.html', None, None, 404)


def anonymous_required(function=None, redirect_url=None):

   if not redirect_url:
       redirect_url = 'audit_list'

   actual_decorator = user_passes_test(
       lambda u: u.is_anonymous,
       login_url=redirect_url
   )

   if function:
       return actual_decorator(function)
   return actual_decorator

User = get_user_model()

@anonymous_required

def login(request):
    context = {}
    if request.method == 'GET':
        form = UserLoginForm()
        context['form'] = form
        return render(request, 'login.html', context)

    if request.method == 'POST':
        form = UserLoginForm(request.POST)

        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user:
            request.session['user_id'] = user.id
            auth.login(request, user)
            return redirect('audit_list')
        else:
            context['form'] = form
            messages.error(request, 'Invalid Credentials')
            return redirect('login')


    return render(request, 'login.html', context)

@login_required
def logout(request):
    auth.logout(request)
    return redirect('login')


def audit_list(request):
    audits = Audit.objects.all().order_by('-created_at')
    return render(request, 'Audit/audit.html', {'audits': audits})


def audit_detail(request, pk):
    audit = get_object_or_404(Audit, pk=pk)
    inspections = Inspection.objects.filter(audit=audit).order_by('-created_at')

    return render(request, 'Audit/audit_detail.html', {
        'audit': audit,
        'inspections': inspections,
    })



def audit_new(request):
    DynamicRequirementFormSet = inlineformset_factory(
        Audit,
        Requirement,
        fields=('text',),
        extra=1,
        can_delete=True
    )

    if request.method == 'POST':
        form = AuditForm(request.POST)
        formset = DynamicRequirementFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            audit = form.save()
            formset.instance = audit
            formset.save()
            return redirect('audit_list')
    else:
        form = AuditForm()
        formset = DynamicRequirementFormSet()

    return render(request, 'Audit/audit_new.html', {
        'form': form,
        'formset': formset,
    })


def audit_edit(request, pk):
    audit = get_object_or_404(Audit, pk=pk)

    DynamicRequirementFormSet = inlineformset_factory(
        Audit,
        Requirement,
        fields=('text',),
        extra=0,
        can_delete=True
    )

    if request.method == 'POST':
        form = AuditForm(request.POST, instance=audit)
        formset = DynamicRequirementFormSet(request.POST, instance=audit, prefix='requirements')

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.instance = audit
            formset.save()
            return redirect('audit_list')
    else:
        form = AuditForm(instance=audit)
        formset = DynamicRequirementFormSet(instance=audit)

    return render(request, 'Audit/audit_edit.html', {
        'form': form,
        'formset': formset,
        'audit': audit,
    })

def audit_delete(request, pk):
    audit = get_object_or_404(Audit, pk=pk)
    audit.delete()
    return redirect(reverse('audit_list'))


def audit_inspection_new(request, audit_pk):
    audit = get_object_or_404(Audit, pk=audit_pk)
    inspection = Inspection(audit=audit, user=request.user if request.user.is_authenticated else None)

    InspectionResultFormSetFactory = inlineformset_factory(
        Inspection,
        InspectionResult,
        fields=['is_met', 'comment', 'image'],
        extra=audit.requirements.count(),  # ← teraz już działa
        can_delete=False,
    )

    if request.method == 'POST':
        form = InspectionForm(request.POST, instance=inspection)
        formset = InspectionResultFormSetFactory(request.POST, request.FILES, instance=inspection)

        if form.is_valid() and formset.is_valid():
            inspection = form.save()
            formset.instance = inspection

            for form_instance, requirement in zip(formset.forms, audit.requirements.all()):
                result = form_instance.save(commit=False)
                result.inspection = inspection
                result.requirement = requirement
                if result.is_met is None:  # dodatkowa asekuracja
                    result.is_met = False
                result.save()

            return redirect('audit_detail', pk=audit.pk)

    else:
        form = InspectionForm(instance=inspection)
        formset = InspectionResultFormSetFactory(instance=inspection, queryset=InspectionResult.objects.none())

        for formset_form, requirement in zip(formset.forms, audit.requirements.all()):
            formset_form.instance.requirement = requirement

    return render(request, 'Inspection/audit_inspection_new.html', {
        'form': form,
        'formset': formset,
        'audit': audit,
    })

def audit_inspection_edit(request, audit_pk, pk):

    audit = get_object_or_404(Audit, pk=audit_pk)
    inspection = get_object_or_404(Inspection, pk=pk, audit=audit)

    InspectionResultFormSetFactory = inlineformset_factory(
        Inspection,
        InspectionResult,
        fields=['is_met', 'comment', 'image'],
        extra=0,
        can_delete=False,
    )

    if request.method == 'POST':
        form = InspectionForm(request.POST, instance=inspection)
        formset = InspectionResultFormSetFactory(request.POST, request.FILES, instance=inspection)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('audit_inspection_detail', audit_pk=audit.pk, pk=inspection.pk)

    else:
        form = InspectionForm(instance=inspection)
        formset = InspectionResultFormSetFactory(instance=inspection)

    return render(request, 'Inspection/audit_inspection_edit.html', {
        'form': form,
        'formset': formset,
        'audit': audit,
        'inspection': inspection,
    })


def audit_inspection_delete(request, audit_pk, pk):
    inspection = get_object_or_404(Inspection, pk=pk)
    audit = inspection.audit
    inspection.delete()
    return redirect('audit_detail', pk=audit.pk)


def audit_inspection_detail(request, audit_pk, pk):
    inspection = get_object_or_404(Inspection, pk=pk)
    audit = get_object_or_404(Audit, pk=audit_pk)
    return render(request, 'Inspection/audit_inspection_detail.html', {
        'inspection': inspection,
        'audit_pk': audit_pk,  # jeśli chcesz przekazać do szablonu
        'audit':audit,
    })

def finish_inspection(request, audit_pk, pk):
    inspection = get_object_or_404(Inspection, pk=pk, audit__pk=audit_pk)
    inspection.completed_at = now()
    inspection.save()
    return redirect('audit_inspection_detail', audit_pk=audit_pk, pk=pk)


def send_inspection_report(request, audit_pk, pk):
    inspection = get_object_or_404(Inspection, pk=pk, audit__pk=audit_pk)

    results = inspection.results.all()
    image_cid_map = {}

    for result in results:
        if result.image and result.image.name and os.path.exists(result.image.path):
            cid = make_msgid(domain="auditmanager.local")[1:-1]  # bez <>
            image_cid_map[result.pk] = cid
            result.image_cid = cid
        else:
            result.image_cid = None

    html_content = render_to_string('Inspection/email_report.html', {
        'audit': inspection.audit,
        'inspection': inspection,
        'results': results,
    })

    email = EmailMultiAlternatives(
        subject=f"Inspection report for {inspection.audit.name}",
        body="This is the plain text version of the report.",
        from_email='auditmanager.brueggen@gmail.com',
        to=['sebastian.paszkowski@brueggen.com'],
    )
    email.attach_alternative(html_content, "text/html")

    # Attach inline images
    for result in results:
        if result.image and result.image_cid:
            with open(result.image.path, 'rb') as img_file:
                mime_img = MIMEImage(img_file.read())
                mime_img.add_header('Content-ID', f'<{result.image_cid}>')
                mime_img.add_header('Content-Disposition', 'inline', filename=os.path.basename(result.image.name))
                email.attach(mime_img)

    email.send()

    messages.success(request, 'Inspection report sent successfully.')
    return redirect('audit_inspection_detail', audit_pk=audit_pk, pk=pk)


