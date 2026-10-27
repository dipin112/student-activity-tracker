import json
from decimal import Decimal, InvalidOperation

from django.db.models import Count, Sum
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .models import Activity


class SuperuserAuthenticationForm(AuthenticationForm):
    """Allow only Django superusers to sign in to the app dashboard."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_superuser:
            from django.core.exceptions import ValidationError

            raise ValidationError('This account does not have superuser access.', code='no_superuser')


class AdminLoginView(LoginView):
    template_name = 'Adminapp/admin_login.html'
    authentication_form = SuperuserAuthenticationForm
    # Keep the root URL on the login screen, including when an admin has an
    # active session. The dashboard remains available after signing in.
    redirect_authenticated_user = False
    next_page = reverse_lazy('dashboard')


@user_passes_test(lambda user: user.is_superuser, login_url='login')
def dashboard(request):
    """A simple server-rendered page for viewing the Django backend."""
    return render(request, 'Adminapp/dashboard.html')


def summary_data():
    totals = Activity.objects.aggregate(total_entries=Count('id'), total_hours=Sum('hours'))
    most_active = (
        Activity.objects.values('name').annotate(total_hours=Sum('hours'))
        .order_by('-total_hours', 'name').first()
    )
    return {
        'total_entries': totals['total_entries'],
        'total_hours': totals['total_hours'] or Decimal('0'),
        'most_active_user': most_active['name'] if most_active else None,
    }


@require_GET
def activities_page(request):
    return render(request, 'Adminapp/activities.html', {'activities': Activity.objects.all()})


@require_http_methods(['GET', 'POST'])
def activity_edit_page(request, activity_id):
    entry = get_object_or_404(Activity, pk=activity_id)
    errors = {}
    if request.method == 'POST':
        cleaned, errors = validate_activity_data(request.POST)
        if not errors:
            for field, value in cleaned.items():
                setattr(entry, field, value)
            entry.save()
            return redirect('activities_page')
    return render(request, 'Adminapp/activity_form.html', {'entry': entry, 'errors': errors})


@require_http_methods(['POST'])
def activity_delete_page(request, activity_id):
    get_object_or_404(Activity, pk=activity_id).delete()
    return redirect('activities_page')


@require_GET
def summary_page(request):
    return render(request, 'Adminapp/summary.html', summary_data())


def api_response(payload, status=200):
    """Return JSON and allow the separately hosted React dev server to call it."""
    response = JsonResponse(payload, status=status)
    response['Access-Control-Allow-Origin'] = 'http://localhost:5173'
    response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


def activity_as_dict(activity):
    return {
        'id': activity.id,
        'name': activity.name,
        'activity': activity.activity,
        'hours': float(activity.hours),
        'created_at': activity.created_at.isoformat(),
    }


def validate_activity_data(data, partial=False):
    """Return cleaned activity fields plus field-level validation errors."""
    cleaned, errors = {}, {}
    for field, max_length, label in (('name', 100, 'Student name'), ('activity', 150, 'Activity')):
        if field not in data and partial:
            continue
        value = str(data.get(field, '')).strip()
        if not value:
            errors[field] = f'{label} is required.'
        elif len(value) > max_length:
            errors[field] = f'{label} must be {max_length} characters or fewer.'
        else:
            cleaned[field] = value

    if 'hours' not in data and partial:
        return cleaned, errors
    try:
        hours = Decimal(str(data.get('hours')))
        if hours <= 0 or hours > Decimal('9999.99'):
            errors['hours'] = 'Hours must be greater than 0 and no more than 9999.99.'
        else:
            cleaned['hours'] = hours
    except (InvalidOperation, TypeError, ValueError):
        errors['hours'] = 'Hours must be a valid number.'
    return cleaned, errors


def json_body(request):
    try:
        return json.loads(request.body), None
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, api_response({'error': 'Request body must be valid JSON.'}, 400)


@csrf_exempt
@require_http_methods(['GET', 'POST', 'OPTIONS'])
def activities(request):
    if request.method == 'OPTIONS':
        return api_response({})

    if request.method == 'GET':
        return api_response({'activities': [activity_as_dict(item) for item in Activity.objects.all()]})

    data, error_response = json_body(request)
    if error_response:
        return error_response
    cleaned, errors = validate_activity_data(data)

    if errors:
        return api_response({'error': 'Please correct the highlighted fields.', 'fields': errors}, 400)

    entry = Activity.objects.create(**cleaned)
    return api_response({'activity': activity_as_dict(entry)}, 201)


@csrf_exempt
@require_http_methods(['GET', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'])
def activity_detail(request, activity_id):
    if request.method == 'OPTIONS':
        return api_response({})
    try:
        entry = Activity.objects.get(pk=activity_id)
    except Activity.DoesNotExist:
        return api_response({'error': 'Activity not found.'}, 404)

    if request.method == 'GET':
        return api_response({'activity': activity_as_dict(entry)})
    if request.method == 'DELETE':
        entry.delete()
        return api_response({}, 204)

    data, error_response = json_body(request)
    if error_response:
        return error_response
    cleaned, errors = validate_activity_data(data, partial=request.method == 'PATCH')
    if errors:
        return api_response({'error': 'Please correct the highlighted fields.', 'fields': errors}, 400)
    for field, value in cleaned.items():
        setattr(entry, field, value)
    entry.save()
    return api_response({'activity': activity_as_dict(entry)})


@require_GET
def summary(request):
    data = summary_data()
    data['total_hours'] = float(data['total_hours'])
    return api_response(data)
