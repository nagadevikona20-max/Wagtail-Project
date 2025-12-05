"""
Unified Dashboard for All Media Types
Displays Images, Videos, Audio, and Documents in a single view
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from itertools import chain
from operator import attrgetter
from datetime import datetime

from .models import CustomImage, CustomDocument, Video, Audio, Category, MediaFolder
from wagtail.images.models import Image
from wagtail.documents.models import Document


class UnifiedMediaItem:
    """
    Standardized wrapper for all media types.
    Converts different media models into a unified format.
    """

    def __init__(self, obj):
        self.original_object = obj
        self.media_type = self._get_media_type(obj)
        self.id = obj.id
        self.title = obj.title
        self.created_at = self._get_created_at(obj)
        self.file_url = self._get_file_url(obj)
        self.thumbnail_url = self._get_thumbnail_url(obj)
        self.file_size = self._get_file_size(obj)
        self.categories = self._get_categories(obj)
        self.tags = self._get_tags(obj)
        self.folder = self._get_folder(obj)
        self.metadata = self._get_metadata(obj)
        self.detail_url = self._get_detail_url(obj)
        self.icon = self._get_icon()
        self.color = self._get_color()

    def _get_media_type(self, obj):
        """Determine the media type."""
        class_name = obj.__class__.__name__
        if class_name in ['CustomImage', 'Image']:
            return 'image'
        elif class_name in ['CustomDocument', 'Document']:
            return 'document'
        elif class_name == 'Video':
            return 'video'
        elif class_name == 'Audio':
            return 'audio'
        return 'unknown'

    def _get_created_at(self, obj):
        """Get creation timestamp."""
        return getattr(obj, 'created_at', None)

    def _get_file_url(self, obj):
        """Get file URL."""
        if hasattr(obj, 'file') and obj.file:
            return obj.file.url
        return None

    def _get_thumbnail_url(self, obj):
        """Get thumbnail URL."""
        if self.media_type == 'image':
            return obj.file.url if obj.file else None
        elif hasattr(obj, 'thumbnail') and obj.thumbnail:
            return obj.thumbnail.url
        return None

    def _get_file_size(self, obj):
        """Get file size."""
        if hasattr(obj, 'file') and obj.file:
            try:
                return obj.file.size
            except:
                return 0
        return 0

    def _get_categories(self, obj):
        """Get categories."""
        if hasattr(obj, 'categories'):
            return obj.categories.all()
        return []

    def _get_tags(self, obj):
        """Get tags."""
        if hasattr(obj, 'tags'):
            return obj.tags.all()
        return []

    def _get_folder(self, obj):
        """Get folder."""
        return getattr(obj, 'folder', None)

    def _get_metadata(self, obj):
        """Get type-specific metadata."""
        metadata = {}

        if self.media_type == 'image':
            metadata['dimensions'] = f"{obj.width}×{obj.height}px" if hasattr(
                obj, 'width') else None
            metadata['copyright'] = getattr(obj, 'copyright_holder', None)

        elif self.media_type == 'document':
            metadata['version'] = getattr(obj, 'document_version', None)
            metadata['department'] = getattr(obj, 'department', None)
            metadata['expiry_date'] = getattr(obj, 'expiry_date', None)

        elif self.media_type == 'video':
            metadata['duration'] = getattr(obj, 'duration', None)
            metadata['resolution'] = getattr(obj, 'resolution', None)
            metadata['director'] = getattr(obj, 'director', None)

        elif self.media_type == 'audio':
            metadata['duration'] = getattr(obj, 'duration', None)
            metadata['artist'] = getattr(obj, 'artist', None)
            metadata['album'] = getattr(obj, 'album', None)
            metadata['genre'] = getattr(obj, 'genre', None)

        return {k: v for k, v in metadata.items() if v}

    def _get_detail_url(self, obj):
        """Get detail page URL."""
        if self.media_type == 'image':
            return f'/media/image/{obj.id}/'
        elif self.media_type == 'document':
            return f'/media/document/{obj.id}/'
        elif self.media_type == 'video':
            return f'/media/video/{obj.id}/'
        elif self.media_type == 'audio':
            return f'/media/audio/{obj.id}/'
        return '#'

    def _get_icon(self):
        """Get Font Awesome icon for media type."""
        icons = {
            'image': 'fa-image',
            'document': 'fa-file-alt',
            'video': 'fa-video',
            'audio': 'fa-music',
        }
        return icons.get(self.media_type, 'fa-file')

    def _get_color(self):
        """Get color scheme for media type."""
        colors = {
            'image': '#667eea',
            'document': '#f5576c',
            'video': '#4facfe',
            'audio': '#43e97b',
        }
        return colors.get(self.media_type, '#6c757d')


def unified_dashboard(request):
    """
    Unified dashboard view showing all media types together.
    """
    # Get filter parameters
    media_type_filter = request.GET.get('type', 'all')
    category_slug = request.GET.get('category')
    folder_id = request.GET.get('folder')
    search_query = request.GET.get('q')
    sort_by = request.GET.get('sort', '-created_at')

    # Get current folder and breadcrumbs
    current_folder = None
    breadcrumbs = []
    subfolders = []

    if folder_id:
        try:
            current_folder = MediaFolder.objects.get(id=folder_id)
            breadcrumbs = current_folder.get_breadcrumbs()
            subfolders = current_folder.get_children()
        except MediaFolder.DoesNotExist:
            pass
    else:
        # Root level - get top-level folders
        subfolders = MediaFolder.objects.filter(
            parent=None).order_by('order', 'name')

    # Fetch all media types (including both custom and default Wagtail models)
    custom_images = CustomImage.objects.all()
    default_images = Image.objects.all()
    custom_documents = CustomDocument.objects.all()
    default_documents = Document.objects.all()
    videos = Video.objects.all()
    audio_files = Audio.objects.all()

    # Combine custom and default
    images = list(chain(custom_images, default_images))
    documents = list(chain(custom_documents, default_documents))

    # Apply folder filter (only for custom models that have folder field)
    if current_folder:
        custom_images = custom_images.filter(folder=current_folder)
        custom_documents = custom_documents.filter(folder=current_folder)
        videos = videos.filter(folder=current_folder)
        audio_files = audio_files.filter(folder=current_folder)
        # Default images/documents don't have folder field, so include all
        images = list(chain(custom_images, default_images))
        documents = list(chain(custom_documents, default_documents))
    elif folder_id is None:
        # Show only items without folder at root level
        custom_images = custom_images.filter(folder__isnull=True)
        custom_documents = custom_documents.filter(folder__isnull=True)
        videos = videos.filter(folder__isnull=True)
        audio_files = audio_files.filter(folder__isnull=True)
        # Include all default images/documents at root
        images = list(chain(custom_images, default_images))
        documents = list(chain(custom_documents, default_documents))

    # Apply category filter (only for models with categories)
    if category_slug:
        custom_images = custom_images.filter(categories__slug=category_slug)
        videos = videos.filter(categories__slug=category_slug)
        audio_files = audio_files.filter(categories__slug=category_slug)
        # Rebuild combined lists
        images = list(chain(custom_images, default_images))
        documents = list(chain(custom_documents, default_documents))

    # Apply search filter
    if search_query:
        custom_images = custom_images.filter(
            Q(title__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
        default_images = default_images.filter(title__icontains=search_query)
        custom_documents = custom_documents.filter(
            Q(title__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
        default_documents = default_documents.filter(
            title__icontains=search_query)
        videos = videos.filter(
            Q(title__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
        audio_files = audio_files.filter(
            Q(title__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
        # Rebuild combined lists
        images = list(chain(custom_images, default_images))
        documents = list(chain(custom_documents, default_documents))

    # Apply media type filter
    if media_type_filter == 'image':
        all_media = images
    elif media_type_filter == 'document':
        all_media = documents
    elif media_type_filter == 'video':
        all_media = list(videos)
    elif media_type_filter == 'audio':
        all_media = list(audio_files)
    else:
        # Combine all media types
        all_media = list(chain(images, documents, videos, audio_files))

    # Sort combined results
    if sort_by == '-created_at':
        all_media.sort(key=lambda x: getattr(
            x, 'created_at', datetime.min), reverse=True)
    elif sort_by == 'created_at':
        all_media.sort(key=lambda x: getattr(x, 'created_at', datetime.min))
    elif sort_by == 'title':
        all_media.sort(key=lambda x: x.title.lower())
    elif sort_by == '-title':
        all_media.sort(key=lambda x: x.title.lower(), reverse=True)

    # Convert to unified format
    unified_items = [UnifiedMediaItem(item) for item in all_media]

    # Pagination
    paginator = Paginator(unified_items, 24)  # 24 items per page
    page = request.GET.get('page', 1)
    media_page = paginator.get_page(page)

    # Get statistics
    stats = {
        'total': len(unified_items),
        'images': len(images),
        'documents': len(documents),
        'videos': videos.count(),
        'audio': audio_files.count(),
    }

    # Get categories
    categories = Category.objects.all()

    context = {
        'media_items': media_page,
        'stats': stats,
        'categories': categories,
        'current_folder': current_folder,
        'breadcrumbs': breadcrumbs,
        'subfolders': subfolders,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_type': media_type_filter,
        'sort_by': sort_by,
    }

    return render(request, 'media_enhancements/unified_dashboard.html', context)


@login_required
def video_detail(request, video_id):
    """Detail view for a video."""
    from django.shortcuts import get_object_or_404
    video = get_object_or_404(Video, id=video_id)

    context = {
        'video': video,
        'categories': video.categories.all(),
        'tags': video.tags.all(),
    }

    return render(request, 'media_enhancements/video_detail.html', context)


@login_required
def audio_detail(request, audio_id):
    """Detail view for an audio file."""
    from django.shortcuts import get_object_or_404
    audio = get_object_or_404(Audio, id=audio_id)

    context = {
        'audio': audio,
        'categories': audio.categories.all(),
        'tags': audio.tags.all(),
    }

    return render(request, 'media_enhancements/audio_detail.html', context)


@login_required
def create_folder(request):
    """Create a new folder."""
    from django.shortcuts import redirect
    from django.contrib import messages
    from django.utils.text import slugify

    if request.method == 'POST':
        name = request.POST.get('name')
        parent_id = request.POST.get('parent_id')
        description = request.POST.get('description', '')

        if name:
            parent = None
            if parent_id:
                try:
                    parent = MediaFolder.objects.get(id=parent_id)
                except MediaFolder.DoesNotExist:
                    pass

            folder = MediaFolder.objects.create(
                name=name,
                slug=slugify(name),
                description=description,
                parent=parent,
                created_by=request.user
            )

            messages.success(request, f'Folder "{name}" created successfully.')

            # Redirect back to the parent folder or root
            if parent:
                return redirect(f'/media/dashboard/?folder={parent.id}')
            else:
                return redirect('/media/dashboard/')
        else:
            messages.error(request, 'Folder name is required.')

    return redirect('/media/dashboard/')


@login_required
def move_media(request):
    """Move media item to a different folder."""
    from django.shortcuts import redirect
    from django.contrib import messages
    from django.http import JsonResponse

    if request.method == 'POST':
        media_type = request.POST.get('media_type')
        media_id = request.POST.get('media_id')
        folder_id = request.POST.get('folder_id')

        # Get the media object
        media_obj = None
        if media_type == 'image':
            try:
                media_obj = CustomImage.objects.get(id=media_id)
            except CustomImage.DoesNotExist:
                pass
        elif media_type == 'document':
            try:
                media_obj = CustomDocument.objects.get(id=media_id)
            except CustomDocument.DoesNotExist:
                pass
        elif media_type == 'video':
            try:
                media_obj = Video.objects.get(id=media_id)
            except Video.DoesNotExist:
                pass
        elif media_type == 'audio':
            try:
                media_obj = Audio.objects.get(id=media_id)
            except Audio.DoesNotExist:
                pass

        if media_obj:
            # Get the folder
            folder = None
            if folder_id and folder_id != 'null':
                try:
                    folder = MediaFolder.objects.get(id=folder_id)
                except MediaFolder.DoesNotExist:
                    pass

            # Move the media
            media_obj.folder = folder
            media_obj.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Media moved successfully.'})
            else:
                messages.success(request, 'Media moved successfully.')
                return redirect(request.META.get('HTTP_REFERER', '/media/dashboard/'))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Media not found.'})
            else:
                messages.error(request, 'Media not found.')

    return redirect('/media/dashboard/')


@login_required
def delete_folder(request, folder_id):
    """Delete a folder if it's empty."""
    from django.shortcuts import redirect, get_object_or_404
    from django.contrib import messages

    folder = get_object_or_404(MediaFolder, id=folder_id)

    if folder.can_delete():
        parent = folder.parent
        folder_name = folder.name
        folder.delete()
        messages.success(
            request, f'Folder "{folder_name}" deleted successfully.')

        if parent:
            return redirect(f'/media/dashboard/?folder={parent.id}')
        else:
            return redirect('/media/dashboard/')
    else:
        messages.error(
            request, 'Cannot delete folder. It must be empty and not a system folder.')
        return redirect(f'/media/dashboard/?folder={folder_id}')


@login_required
def rename_folder(request, folder_id):
    """Rename a folder."""
    from django.shortcuts import redirect, get_object_or_404
    from django.contrib import messages
    from django.utils.text import slugify

    folder = get_object_or_404(MediaFolder, id=folder_id)

    if request.method == 'POST':
        new_name = request.POST.get('name')
        if new_name:
            folder.name = new_name
            folder.slug = slugify(new_name)
            folder.save()
            messages.success(request, f'Folder renamed to "{new_name}".')
        else:
            messages.error(request, 'Folder name is required.')

    return redirect(f'/media/dashboard/?folder={folder_id}')
