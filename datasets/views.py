from django.shortcuts import redirect, render

from .forms import DatasetUploadForm
from .models import DatasetImport, ImportedRecord
from .services import process_dataset_import


def dataset_home(request):
    if not request.session.get('demo_logged_in'):
        return redirect('login')

    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            department = form.cleaned_data['source_department']
            uploaded_file = form.cleaned_data['source_file']
            file_extension = uploaded_file.name.rsplit('.', 1)[-1].lower()

            dataset_import = DatasetImport.objects.create(
                source_department=department,
                original_filename=uploaded_file.name,
                file_format=file_extension.upper(),
                source_file=uploaded_file,
            )
            process_dataset_import(dataset_import)
            form = DatasetUploadForm()
            success_message = 'Dataset uploaded successfully.'
        else:
            success_message = None
    else:
        form = DatasetUploadForm()
        success_message = None

    return render(request, 'datasets/home.html', {
        'form': form,
        'imports': DatasetImport.objects.all(),
        'success_message': success_message,
    })


def dataset_detail(request, import_id):
    if not request.session.get('demo_logged_in'):
        return redirect('login')

    dataset_import = DatasetImport.objects.filter(id=import_id).first()
    if dataset_import is None:
        from django.http import Http404
        raise Http404

    return render(request, 'datasets/detail.html', {
        'dataset_import': dataset_import,
        'records': dataset_import.records.all(),
    })
