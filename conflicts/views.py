from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from datasets.models import DatasetImport

from .forms import ConflictResolutionForm
from .models import Conflict, ConflictResolution
from .services import detect_conflicts


def _require_demo_login(request):
    if not request.session.get('demo_logged_in'):
        return redirect('login')
    return None


def conflict_dashboard(request):
    login_redirect = _require_demo_login(request)
    if login_redirect:
        return login_redirect

    if request.method == 'POST':
        result = detect_conflicts()
        messages.success(
            request,
            (
                f"Detection complete: {result['created']} new, "
                f"{result['reactivated']} reactivated, "
                f"{result['cleared']} cleared, "
                f"{result['active']} active conflicts."
            ),
        )
        return redirect('conflict_dashboard')

    conflicts = Conflict.objects.select_related(
        'property',
    ).prefetch_related(
        'values__standardization_result__source_record__dataset_import',
    )
    counts = conflicts.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status=Conflict.STATUS_PENDING)),
        resolved=Count('id', filter=Q(status=Conflict.STATUS_RESOLVED)),
        cleared=Count('id', filter=Q(status=Conflict.STATUS_CLEARED)),
    )
    field_labels = dict(Conflict.FIELD_CHOICES)
    conflicts_by_field = [
        {
            'label': field_labels.get(item['field_name'], item['field_name']),
            'count': item['count'],
        }
        for item in conflicts.values('field_name')
        .annotate(count=Count('id'))
        .order_by('field_name')
    ]

    return render(
        request,
        'conflicts/dashboard.html',
        {
            'conflicts': conflicts,
            'counts': counts,
            'conflicts_by_field': conflicts_by_field,
        },
    )


def conflict_detail(request, conflict_id):
    login_redirect = _require_demo_login(request)
    if login_redirect:
        return login_redirect

    conflict = get_object_or_404(
        Conflict.objects.select_related(
            'property',
            'resolution',
        ).prefetch_related(
            'values__standardization_result__source_record__dataset_import',
        ),
        pk=conflict_id,
    )
    department_labels = dict(DatasetImport.DEPARTMENT_CHOICES)
    values_by_department = {}

    for item in conflict.values.all():
        department = item.standardization_result.source_record.source_department
        values_by_department.setdefault(department, []).append(item)

    department_codes = [
        code for code, _ in DatasetImport.DEPARTMENT_CHOICES
    ]
    department_codes.extend(
        sorted(set(values_by_department) - set(department_codes))
    )
    departments = [
        {
            'label': department_labels.get(code, code),
            'values': values_by_department.get(code, []),
        }
        for code in department_codes
    ]

    return render(
        request,
        'conflicts/detail.html',
        {
            'conflict': conflict,
            'departments': departments,
        },
    )


def resolve_conflict(request, conflict_id):
    login_redirect = _require_demo_login(request)
    if login_redirect:
        return login_redirect

    conflict = get_object_or_404(
        Conflict.objects.prefetch_related(
            'values__standardization_result__source_record__dataset_import',
        ),
        pk=conflict_id,
    )
    if conflict.status != Conflict.STATUS_PENDING:
        messages.warning(
            request,
            'Only pending conflicts can be resolved.',
        )
        return redirect('conflict_detail', conflict_id=conflict.id)

    if request.method == 'POST':
        form = ConflictResolutionForm(request.POST, conflict=conflict)
        if form.is_valid():
            with transaction.atomic():
                conflict = Conflict.objects.select_for_update().get(
                    pk=conflict_id,
                )
                if conflict.status != Conflict.STATUS_PENDING:
                    messages.warning(
                        request,
                        'This conflict is no longer pending.',
                    )
                    return redirect(
                        'conflict_detail',
                        conflict_id=conflict.id,
                    )

                ConflictResolution.objects.create(
                    conflict=conflict,
                    resolved_value=form.cleaned_data['resolved_value'],
                    resolution_note=form.cleaned_data['resolution_note'],
                )
                conflict.status = Conflict.STATUS_RESOLVED
                conflict.save(update_fields=['status'])

            messages.success(request, 'Conflict resolution saved.')
            return redirect('conflict_detail', conflict_id=conflict.id)
    else:
        form = ConflictResolutionForm(conflict=conflict)

    return render(
        request,
        'conflicts/resolve.html',
        {
            'conflict': conflict,
            'form': form,
        },
    )
