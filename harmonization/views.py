from django.shortcuts import render, redirect
from .models import HarmonizedRecord
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .forms import ManualMatchForm


def harmonization_home(request):

    if not request.session.get('demo_logged_in'):
        return redirect('login')

    records = HarmonizedRecord.objects.select_related(
        'standardization_result',
        'standardization_result__source_record',
        'standardization_result__source_record__dataset_import',
        'property'
    ).all()

    context = {
        'records': records,
        'total_records': records.count(),
        'matched_records': records.filter(
            match_status='matched'
        ).count(),
        'unmatched_records': records.filter(
            match_status='unmatched'
        ).count(),
        'invalid_records': records.filter(
            match_status='invalid'
        ).count(),
    }

    return render(
        request,
        'harmonization/home.html',
        context
    )



def unmatched_records(request):

    if not request.session.get('demo_logged_in'):
        return redirect('login')

    records = HarmonizedRecord.objects.select_related(
        'standardization_result',
        'standardization_result__source_record',
        'standardization_result__source_record__dataset_import'
    ).filter(
        match_status='unmatched'
    )

    return render(
        request,
        'harmonization/unmatched.html',
        {'records': records}
    )


def unmatched_record_detail(request, record_id):


    if not request.session.get('demo_logged_in'):
        return redirect('login')

    record = get_object_or_404(
        HarmonizedRecord.objects.select_related(
            'standardization_result',
            'standardization_result__source_record',
            'standardization_result__source_record__dataset_import'
        ),
        id=record_id,
        match_status='unmatched'
    )

    return render(
        request,
        'harmonization/unmatched_detail.html',
        {'record': record}
    )

def manual_match(request, record_id):

    if not request.session.get('demo_logged_in'):
        return redirect('login')

    record = get_object_or_404(
        HarmonizedRecord,
        id=record_id,
        match_status='unmatched'
    )

    if request.method == 'POST':
        form = ManualMatchForm(request.POST)

        if form.is_valid():
            selected_property = form.cleaned_data['property']

            record.property = selected_property
            record.match_status = HarmonizedRecord.STATUS_MATCHED
            record.match_method = 'Manual Match'
            record.save()

            messages.success(
                request,
                f'Record successfully matched with {selected_property.parcel_id}.'
            )

            return redirect('unmatched_records')

    else:
        form = ManualMatchForm()

    return render(
        request,
        'harmonization/manual_match.html',
        {
            'record': record,
            'form': form,
        }
    )