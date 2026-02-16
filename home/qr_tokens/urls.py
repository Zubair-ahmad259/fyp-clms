from django.urls import path
from . import views

urlpatterns = [

    # Main dashboard
    path('', views.token_dashboard, name='token_dashboard'),

    # Token types (leave, complaint, fee, etc.)
    path('types/', views.token_types, name='token_types'),

    # Create token
    path('create/', views.create_token, name='create_token'),

    # Student tokens list
    path('my-tokens/', views.student_tokens, name='student_tokens'),

    # View single token
    path('view/<int:pk>/', views.view_token, name='view_token'),

    # Teacher dashboard
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),

    # Statistics
    path('statistics/', views.token_statistics, name='token_statistics'),
]
