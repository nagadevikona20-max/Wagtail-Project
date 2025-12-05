from django.urls import path, reverse
from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin.menu import MenuItem

# Import snippet viewsets to register them
from . import wagtail_snippet_viewsets


@hooks.register('register_admin_menu_item')
def register_unified_dashboard_menu_item():
    """
    Add a menu item to the Wagtail admin for the Unified Dashboard.
    """
    return MenuItem(
        'Dashboard',
        reverse('media_enhancements:unified_dashboard'),
        icon_name='view',
        order=199
    )


# Menu items for snippets are now handled by wagtail_snippet_viewsets.py


@hooks.register('insert_global_admin_css')
def global_admin_css():
    """
    Add custom CSS to the Wagtail admin.
    """
    from django.utils.safestring import mark_safe
    return mark_safe(
        '<style>'
        '.media-enhancement-badge { '
        '    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
        '    color: white; '
        '    padding: 2px 8px; '
        '    border-radius: 3px; '
        '    font-size: 11px; '
        '} '
        '</style>'
    )


@hooks.register('insert_global_admin_js')
def global_admin_js():
    """
    Add custom JavaScript to enhance the admin experience.
    """
    from django.utils.safestring import mark_safe
    return mark_safe(
        '''
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Rich Media Library Enhancements Loaded');
            
            // Add visual indicators for custom fields
            const copyrightFields = document.querySelectorAll('[name*="copyright"]');
            copyrightFields.forEach(field => {
                if (field.value) {
                    field.style.borderLeft = '3px solid #28a745';
                }
            });
        });
        </script>
        '''
    )


@hooks.register('construct_image_chooser_queryset')
def show_my_uploaded_images_only(images, request):
    """
    Optionally filter images in the chooser.
    This example shows all images, but you can customize it.
    """
    # Example: Only show images uploaded by the current user
    # return images.filter(uploaded_by_user=request.user)
    return images


@hooks.register('after_create_image')
def log_image_creation(request, image):
    """
    Hook that runs after an image is created.
    """
    print(f"New image uploaded: {image.title} by {request.user}")


@hooks.register('after_create_document')
def log_document_creation(request, document):
    """
    Hook that runs after a document is created.
    """
    print(f"New document uploaded: {document.title} by {request.user}")
