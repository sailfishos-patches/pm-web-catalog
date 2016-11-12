from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError

from example.demo.models import *
from example.demo.forms import *
from example.demo.filehandler import *


def model_form_upload(request):
    if request.method == 'POST':
        project_form = ProjectForm(request.POST, prefix="prj")
        file_form = FileForm(request.POST, request.FILES, prefix="fls")
        if project_form.is_valid() and file_form.is_valid():
            project = project_form.save(commit=False)
            file = file_form.save(commit=False)
            file.project = project.name
            project.save()
            file.save()
            return redirect('view_user_projects', request.user.username)
    else:
        project_form = ProjectForm(initial={'author': request.user.username}, prefix="prj")
        file_form = FileForm(initial={'author': request.user.username}, prefix="fls")
    return render(request, 'model_form_upload.html', {
        'project_form': project_form,
        'file_form': file_form,
    })


def view_projects(request):
    projects = ProjectsModel.objects.all()
    return render(request, 'view_projects.html', {
        'documents': projects,
    })


def view_user_projects(request, user):
    projects = ProjectsModel.objects.filter(author=user)
    return render(request, 'view_projects.html', {
        'documents': projects,
        'author': user
    })


def view_project(request, project):
    try:
        item = ProjectsModel.objects.get(name=project)
        files = FilesModel.objects.filter(project=project)
        return render(request, 'view_project.html', {
            'project': item,
            'files': files,
        })
    except:
        return redirect('view_projects')


def delete_project(request, project):
    try:
        item = ProjectsModel.objects.get(name=project)
    except:
        return redirect('view_user_projects', request.user.username)
    if request.method == 'POST':
        if request.user.is_authenticated and request.user.username == item.author:
            files = FilesModel.objects.filter(project=project)
            item.delete()
            files.delete()
        return redirect('view_user_projects', request.user.username)
    return render(request, 'delete_project.html', {
        'project': item,
    })


def edit_project(request, project):
    item = ProjectsModel.objects.get(name=project)
    files = FilesModel.objects.filter(project=project)
    project_form = ProjectEditForm(instance=item)
    upload_form = FileForm(initial={'author': request.user.username, 'project': project})
    if request.user.is_authenticated and request.user.username == item.author and request.method == 'POST':
        if 'file-edit' in request.POST:
            file_form = FileForm(request.POST, instance=FilesModel.objects.get(id=request.POST.get('fileid')))
            if file_form.is_valid():
                file_form.save()
                item.save()
                return redirect('view_project', project)
        elif 'file-delete' in request.POST:
            file_object = FilesModel.objects.get(id=request.POST.get('fileid'))
            file_object.delete()
            fs = FileSystemStorage()
            if fs.exists(file_object.document.name):
                fs.delete(file_object.document.name)
        elif 'project-edit' in request.POST:
            project_form = ProjectEditForm(request.POST, instance=item)
            if project_form.is_valid():
                project_form.save()
                return redirect('view_project', project)
        elif 'file-upload' in request.POST:
            upload_form = FileForm(request.POST, request.FILES)
            if upload_form.is_valid():
                uploaded = upload_form.save()
                valid, message, content = ArchiveVerifier(uploaded.document.name).is_valid()
                if not valid:
                    uploaded.delete()
                    fs = FileSystemStorage()
                    if fs.exists(uploaded.document.name):
                        fs.delete(uploaded.document.name)
                    return render(request, 'upload_error.html', {
                        'project': item,
                        'message': message,
                        'content': content,
                    })
                return redirect('edit_project', project)
    return render(request, 'edit_project.html', {
        'files_forms': [FileEditForm(instance=file) for file in files],
        'project_form': project_form,
        'upload_form': upload_form
    })


def api_projects(request):
    attrs = getattr(request, request.method).dict()
    version = ''
    if 'version' in attrs:
        version = attrs.pop('version')
    if version:
        files = FilesModel.objects.filter(compatible__contains=version).values()
        names = set()
        [names.add(file['project']) for file in files]
        attrs['name__in'] = names
    objects = ProjectsModel.objects.filter(**attrs)
    return JsonResponse(list(objects.values()), safe=False)


def api_project(request):
    attrs = getattr(request, request.method).dict()
    if 'action' in attrs:
        action = attrs.get('action') if 'action' in attrs else ''
        project = attrs.get('name') if 'name' in attrs else ''
        project_query = ProjectsModel.objects.filter(name=project)
        status = project_query.exists()
        rating = 0
        if status:
            project_item = project_query.get()
            if action == 'upvote':
                project_item.rating += 1
                project_item.save()
            elif action == 'downvote':
                project_item.rating -= 1
                project_item.save()
            rating = project_item.rating
        return JsonResponse({'status': status, 'project': project, 'rating': rating})
    else:
        project_query = ProjectsModel.objects.filter(**attrs)
        status = project_query.exists()
        objects = {}
        if status and project_query.count() == 1:
            objects = project_query.values()[0]
            files = FilesModel.objects.filter(project=objects['name']).values()
            objects['files'] = list(files)
        return JsonResponse(objects, safe=False)


def api_rating(request):
    attrs = getattr(request, request.method)
    action = attrs.get('action') if 'action' in attrs else ''
    project = attrs.get('project') if 'project' in attrs else ''
    project_query = ProjectsModel.objects.filter(name=project)
    status = project_query.exists()
    rating = 0
    if status:
        project_item = project_query.get()
        if action == 'upvote':
            project_item.rating += 1
            project_item.save()
        elif action == 'downvote':
            project_item.rating -= 1
            project_item.save()
        rating = project_item.rating
    return JsonResponse({'status': status, 'project': project, 'rating': rating})


def api_files(request):
    attrs = getattr(request, request.method).dict()
    if 'action' in attrs:
        action = attrs.get('action') if 'action' in attrs else ''
        filename = attrs.get('file') if 'file' in attrs else ''
        files_query = FilesModel.objects.filter(document=filename)
        status = files_query.exists()
        count = 0
        if status:
            file_item = files_query.get()
            if action == 'activation':
                file_item.activations += 1
                file_item.save()
                try:
                    project = ProjectsModel.objects.get(name=file_item.project)
                    project.total_activations += 1
                    project.save()
                except:
                    pass
            elif action == 'deactivation':
                file_item.activations -= 1
                file_item.save()
                try:
                    project = ProjectsModel.objects.get(name=file_item.project)
                    project.total_activations -= 1
                    project.save()
                except:
                    pass
            count = file_item.activations
        objects = {'status': status, 'file': filename, 'count': count}
    else:
        version = ''
        if 'version' in attrs:
            version = attrs.pop('version')
        if version:
            attrs['compatible__contains'] = version
        files = FilesModel.objects.filter(**attrs)
        objects = list(files.values())
    return JsonResponse(objects, safe=False)
