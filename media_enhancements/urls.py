from django.urls import path
from django.shortcuts import redirect
from . import views
from .unified_dashboard import (
    unified_dashboard, video_detail, audio_detail,
    create_folder, move_media, delete_folder, rename_folder
)
from .image_editor_views import image_editor_view, apply_edit, preview_edit, batch_process

app_name = 'media_enhancements'

urlpatterns = [
    # Unified Dashboard
    path('dashboard/', unified_dashboard, name='unified_dashboard'),
    
    # Redirect old gallery to unified dashboard
    path('gallery/', lambda request: redirect('media_enhancements:unified_dashboard'), name='gallery'),
    
    # Detail Views
    path('image/<int:image_id>/', views.image_detail, name='image_detail'),
    path('document/<int:document_id>/', views.document_detail, name='document_detail'),
    path('video/<int:video_id>/', video_detail, name='video_detail'),
    path('audio/<int:audio_id>/', audio_detail, name='audio_detail'),
    
    # Image Editor
    path('editor/<int:image_id>/', image_editor_view, name='image_editor'),
    path('editor/<int:image_id>/apply/', apply_edit, name='apply_edit'),
    path('editor/<int:image_id>/preview/', preview_edit, name='preview_edit'),
    path('editor/batch/', batch_process, name='batch_process'),
    
    # Category View - redirect to unified dashboard
    path('category/<slug:category_slug>/', lambda request, category_slug: redirect('media_enhancements:unified_dashboard'), name='category_media'),
    
    # Folder Management
    path('folder/create/', create_folder, name='create_folder'),
    path('folder/<int:folder_id>/delete/', delete_folder, name='delete_folder'),
    path('folder/<int:folder_id>/rename/', rename_folder, name='rename_folder'),
    path('media/move/', move_media, name='move_media'),
    
    # API
    path('api/stats/', views.media_stats_api, name='media_stats_api'),
]
