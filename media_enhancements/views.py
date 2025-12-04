from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import CustomImage, CustomDocument, Category


# Removed media_gallery view - replaced by unified_dashboard


@login_required
def image_detail(request, image_id):
    """
    Display detailed information about a specific image.
    """
    image = get_object_or_404(CustomImage, id=image_id)
    
    context = {
        'image': image,
        'categories': image.categories.all(),
        'tags': image.tags.all(),
    }
    
    return render(request, 'media_enhancements/image_detail.html', context)


@login_required
def document_detail(request, document_id):
    """
    Display detailed information about a specific document.
    """
    document = get_object_or_404(CustomDocument, id=document_id)
    
    context = {
        'document': document,
        'tags': document.tags.all(),
    }
    
    return render(request, 'media_enhancements/document_detail.html', context)


@login_required
@require_http_methods(["GET"])
def media_stats_api(request):
    """
    API endpoint to get media statistics.
    """
    stats = {
        'total_images': CustomImage.objects.count(),
        'total_documents': CustomDocument.objects.count(),
        'total_categories': Category.objects.count(),
        'images_by_category': list(
            Category.objects.annotate(
                image_count=Count('customimage')
            ).values('name', 'image_count')
        ),
        'recent_uploads': {
            'images': list(
                CustomImage.objects.order_by('-created_at')[:5].values(
                    'id', 'title', 'created_at'
                )
            ),
            'documents': list(
                CustomDocument.objects.order_by('-created_at')[:5].values(
                    'id', 'title', 'created_at'
                )
            ),
        }
    }
    
    return JsonResponse(stats)


# Removed category_media view - category filtering now in unified_dashboard
