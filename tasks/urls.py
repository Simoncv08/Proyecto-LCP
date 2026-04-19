from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('logout/', views.signout),
    path('signin/', views.signin, name='signin'),
    path('events/', views.events, name='events'),
    path('event/create/', views.create_event, name='create_event'),
    path('event/<int:evento_id>/edit/', views.edit_event, name='edit_event'),
    path('event/<int:evento_id>/delete/',
         views.eliminar_evento, name='delete_event'),
    path('productos/<int:evento_id>/', views.productos_por_evento),
    path('estudiantes/', views.estudiantes, name='estudiantes'),
    path('estudiantes/create/', views.create_estudiante, name='create_estudiante'),
    path('api/estudiantes/', views.estudiantes_filtrados, name='estudiantes_filtrados'),
    path('estudiantes/importar/', views.importar_estudiantes, name='importar_estudiantes'),
    path('estudiantes/<int:estudiante_id>/eliminar/', views.eliminar_estudiante, name='eliminar_estudiante'),
    path('estudiantes/<int:estudiante_id>/editar/',   views.editar_estudiante,   name='editar_estudiante'),
]
