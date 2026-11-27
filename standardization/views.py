
from django.shortcuts import render, get_object_or_404

from .models import StandardizationResult


def standardization_home(request):
    results = StandardizationResult.objects.select_related(
        'source_record',
        'source_record__dataset_import'
    ).all()

    context = {
        'results': results,
        'total_records': results.count(),
        'valid_records': results.filter(is_valid=True).count(),
        'invalid_records': results.filter(is_valid=False).count(),
    }

    return render(request, 'standardization/home.html', context)


def standardization_detail(request, result_id):
    result = get_object_or_404(
        StandardizationResult.objects.select_related(
            'source_record',
            'source_record__dataset_import'
        ),
        id=result_id
    )

    return render(
        request,
        'standardization/detail.html',
        {'result': result}
    )
