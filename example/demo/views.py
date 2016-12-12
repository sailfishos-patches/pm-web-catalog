from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage

from example.demo.models import *
from example.demo.forms import *


def model_form_upload(request):
    if request.method == 'POST':
        project_form = ProjectForm(request.POST, prefix="prj")
        file_form = FileForm(request.POST, request.FILES, prefix="fls")
        screenshot_form = ScreenshotForm(request.POST, request.FILES, prefix="scr")
        if project_form.is_valid() and file_form.is_valid() and screenshot_form.is_valid():
            project = project_form.save(commit=False)
            file = file_form.save(commit=False)
            file.project = project.name
            project.save()
            file.save()
            screenshots = request.FILES.getlist('scr-screenshot')
            for screenshot in screenshots:
                instance = ScreenshotsModel(
                    project=project.name,
                    filename=screenshot.name,
                    screenshot=screenshot
                )
                instance.save()
            return redirect('view_user_projects', request.user.username)
    else:
        project_form = ProjectForm(initial={'author': request.user.username}, prefix="prj")
        file_form = FileForm(initial={'author': request.user.username}, prefix="fls")
        screenshot_form = ScreenshotForm(prefix="scr")
    return render(request, 'model_form_upload.html', {
        'project_form': project_form,
        'file_form': file_form,
        'screenshot_form': screenshot_form,
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
        screenshots_objects = ScreenshotsModel.objects.filter(project=project)
        return render(request, 'view_project.html', {
            'project': item,
            'files': files,
            'screenshots': screenshots_objects,
        })
    except:
        return redirect('view_projects')


def delete_project(request, project):
    try:
        item = ProjectsModel.objects.get(name=project)
    except:
        return redirect('view_user_projects', request.user.username)
    if request.method == 'POST':
        if request.user.is_authenticated and request.user.username == item.author or request.user.is_staff:
            files = FilesModel.objects.filter(project=project)
            screenshots = ScreenshotsModel.objects.filter(project=project)
            fs = FileSystemStorage()
            if fs.exists(files.values()[0]['document']):
                fs.delete(files.values()[0]['document'])
            for screenshot in screenshots.values():
                if fs.exists(screenshot['screenshot']):
                    fs.delete(screenshot['screenshot'])
            item.delete()
            files.delete()
            screenshots.delete()
        return redirect('view_user_projects', request.user.username)
    return render(request, 'delete_project.html', {
        'project': item,
    })


def edit_project(request, project):
    item = ProjectsModel.objects.get(name=project)
    files = FilesModel.objects.filter(project=project)
    screenshots_objects = ScreenshotsModel.objects.filter(project=project)
    project_form = ProjectEditForm(instance=item)
    upload_form = FileForm(initial={'author': request.user.username, 'project': project})
    screenshot_form = ScreenshotForm(initial={'project': project})
    if request.user.is_authenticated and (request.user.username == item.author or request.user.is_staff) and request.method == 'POST':
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
            project_form = ProjectEditForm(request.POST, request.FILES, instance=item)
            if project_form.is_valid():
                project_form.save()
                return redirect('view_project', project)
        elif 'file-upload' in request.POST:
            upload_form = FileForm(request.POST, request.FILES)
            if upload_form.is_valid():
                upload_form.save()
                return redirect('edit_project', project)
        elif 'screenshot-upload' in request.POST:
            screenshot_form = ScreenshotForm(request.POST, request.FILES)
            if screenshot_form.is_valid():
                screenshots = request.FILES.getlist('screenshot')
                for screenshot in screenshots:
                    instance = ScreenshotsModel(
                        project=project,
                        filename=screenshot.name,
                        screenshot=screenshot
                    )
                    instance.save()
                return redirect('edit_project', project)
        elif 'screenshot-delete' in request.POST:
            screenshot_object = ScreenshotsModel.objects.get(id=request.POST.get('screenshotid'))
            screenshot_object.delete()
            fs = FileSystemStorage()
            if fs.exists(screenshot_object.screenshot.name):
                fs.delete(screenshot_object.screenshot.name)
            screenshots_objects = ScreenshotsModel.objects.filter(project=project)
    return render(request, 'edit_project.html', {
        'files_forms': [FileEditForm(instance=file) for file in files],
        'project_form': project_form,
        'upload_form': upload_form,
        'screenshots': screenshots_objects,
        'screenshot_form': screenshot_form,
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
        if action == 'activation' or action == 'deactivation':
            version = attrs.get('version') if 'version' in attrs else ''
            files_query = FilesModel.objects.filter(project=project, version=version)
            count = 0
            status &= files_query.exists()
            if status:
                file_item = files_query.get()
                project_item = project_query.get()
                if action == 'activation':
                    file_item.activations += 1
                    project_item.total_activations += 1
                elif action == 'deactivation':
                    file_item.activations -= 1
                    project_item.total_activations -= 1
                file_item.save()
                project_item.save()
                count = file_item.activations
            objects = {'status': status, 'name': project, 'version': version, 'count': count}
        else:
            rating = 0
            if status:
                project_item = project_query.get()
                if action == 'upvote':
                    project_item.rating += 1
                    if 'twice' in attrs:
                        project_item.rating += 1
                    project_item.save()
                elif action == 'downvote':
                    project_item.rating -= 1
                    if 'twice' in attrs:
                        project_item.rating -= 1
                    project_item.save()
                rating = project_item.rating
            objects = {'status': status, 'project': project, 'rating': rating}
        return JsonResponse(objects)
    else:
        version = False
        if 'version' in attrs:
            version = attrs.pop('version')
        project_query = ProjectsModel.objects.filter(**attrs)
        status = project_query.exists()
        objects = {}
        if status and project_query.count() == 1:
            objects = project_query.values()[0]
            if version:
                files = FilesModel.objects.filter(project=objects['name'], version=version)
                if files.exists() and files.count() == 1:
                    objects['version'] = version
                    objects['compatible'] = files.values()[0]['compatible']
                objects.pop('total_activations')
                objects.pop('rating')
            else:
                files = FilesModel.objects.filter(project=objects['name']).values()
                screenshots = ScreenshotsModel.objects.filter(project=objects['name']).values()
                objects['files'] = list(files)
                objects['screenshots'] = list(screenshots)
        return JsonResponse(objects, safe=False)


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


def api_easter(request):
    text = '''
Case study: Sailfish Watch

Sailfish OS is known for smartphones, but it also forms an excellent base for many very different kinds of embedded devices. Sailfish OS is no longer the new kid on the block, and every port strengthens the operating system’s capability to scale. So far the operating system has been productized to four different devices including Jolla smartphone, Jolla Tablet, Intex Aqua Fish and Turing Phone, and ported to dozens of other phones and tablets by the Sailfish community.

Last month we did a quick exercise aiming to see how far we could get in a few weeks in porting Sailfish OS to a new kind of mobile device, an Android smartwatch. Compared to the competition, Sailfish OS’s interaction paradigm is particularly suited for small screens, it being gesture-driven and designed to maximize display estate available for the user content. We also had the watch demo with us as a teaser in Slush 2016 this week, to emphasize to journalists, partners and other people how versatile platform Sailfish OS is. And naturally an implementation like this, could fit nicely also into our licensing strategy.

Sailfish Watch

We inferred technical and design inspiration help from an existing smartwatch OS called Asteroid OS, led by Florent Revest, which shares a lot of the same core Mer and Nemo libraries with Sailfish OS, and goes to show how important and valuable support from the open source community is for us. Compatibility layer libHybris gives us quick access to existing Android hardware, and prototyping features is a breeze on top of the high-level QML APIs to the home screen, connectivity, profiles, power management, display, clock, calendar, weather and settings backends also powering features running on Sailfish OS smartphones. In addition Sailfish UI layer provides a toolkit of scalable common components, gestures, layouts, animations, icons, fonts and localization enablers for creating fluid and beautiful user experience.

The main view is reserved for showing time as smartwatch is still a watch and a fashion accessory as well as a tech gadget.

Homescreen is organized in familiar Sailfish-style horizontal carousel with Events on the left, the main view on the center and fitness view promoted as the super app on the right.

Similarities with other Sailfish devices don’t end there. Apps can always be accessed from the bottom of the screen no matter where you are and ambiences from the top. The most important setting shortcuts are integrated right into Events.

Fitness and health tracking is arguably the most important feature in the current generation of wearables. In the fitness view you can track your daily activity levels. Tapping a progress circle turns the watch into a dedicated step or a calorie counter. With more time it could be extended to comprehensive health suite.

The watch is paired with Sailfish smartphone, which forwards calls and message notifications to the watch. User gets notified with a gentle vibration on the wrist, can quickly glance incoming events, easily dismiss incoming calls with a simple gesture, or transfer the call to his/her hands-free. In the prototype the connectivity is routed through WLAN as the low-power Bluetooth would have required a bit more porting time.

Device configuration and user preferences should automatically be transferred from the smartphone, but we implemented time and date settings as a proof-of-concept to see how easy it is to port traditional Sailfish views to a small screen. In a productized version the date picker of course would naturally be redesigned, but the ported one was already surprisingly usable.

A final note related to Sailfish OS / Jolla products: if you are a Sailfish community member or a just a fan, you can be sure that we will continue to push for new Sailfish devices for our community. More info about that in the near future!
'''
    objects = {"status": True, "text": text}
    return JsonResponse(objects)
