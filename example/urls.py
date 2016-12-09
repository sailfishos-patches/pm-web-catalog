from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from example.demo import views


admin.autodiscover()

urlpatterns = [
    url(r'^accounts/', include('allauth.urls')),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    url(r'^accounts/profile/$', TemplateView.as_view(template_name='profile.html')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^usage/$', TemplateView.as_view(template_name='helpme_page.html'), name='helpme_page'),
    url(r'^projects/$', views.view_projects, name='view_projects'),
    url(r'^projects/(.*)$', views.view_user_projects, name='view_user_projects'),
    url(r'^upload/$', views.model_form_upload, name='model_form_upload'),
    url(r'^project/(.+)/delete$', views.delete_project, name='delete_project'),
    url(r'^project/(.+)/edit$', views.edit_project, name='edit_project'),
    url(r'^project/(.*)$', views.view_project, name='view_project'),
# API
    url(r'^api/projects$', views.api_projects),
    url(r'^api/project$', views.api_project),
    url(r'^api/files$', views.api_files),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
