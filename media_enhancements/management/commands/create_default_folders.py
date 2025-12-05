"""
Management command to create default media folders
"""
from django.core.management.base import BaseCommand
from media_enhancements.models import MediaFolder


class Command(BaseCommand):
    help = 'Creates default media folders with icons and descriptions'

    def handle(self, *args, **options):
        folders_data = [
            {
                'name': 'Banners',
                'description': 'Marketing banners and promotional images',
                'icon': 'fa-flag',
                'color': '#FF6B9D',
                'order': 1
            },
            {
                'name': 'Products',
                'description': 'Product images and media',
                'icon': 'fa-box',
                'color': '#4A90E2',
                'order': 2
            },
            {
                'name': 'Campaigns',
                'description': 'Marketing campaign assets',
                'icon': 'fa-bullhorn',
                'color': '#50E3C2',
                'order': 3
            },
            {
                'name': 'Social Media',
                'description': 'Social media posts and graphics',
                'icon': 'fa-share-alt',
                'color': '#9013FE',
                'order': 4
            },
            {
                'name': 'Logos',
                'description': 'Company and brand logos',
                'icon': 'fa-copyright',
                'color': '#F5A623',
                'order': 5
            },
            {
                'name': 'Videos',
                'description': 'Video content and recordings',
                'icon': 'fa-video',
                'color': '#4A90E2',
                'order': 6
            },
            {
                'name': 'Audio',
                'description': 'Audio files and music',
                'icon': 'fa-music',
                'color': '#50E3C2',
                'order': 7
            },
            {
                'name': 'Documents',
                'description': 'PDFs and other documents',
                'icon': 'fa-file-alt',
                'color': '#FF6B9D',
                'order': 8
            },
        ]

        created_count = 0
        for folder_data in folders_data:
            folder, created = MediaFolder.objects.get_or_create(
                name=folder_data['name'],
                parent=None,
                defaults={
                    'description': folder_data['description'],
                    'icon': folder_data['icon'],
                    'color': folder_data['color'],
                    'order': folder_data['order']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created folder: {folder.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Folder already exists: {folder.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {created_count} new folders!'
            )
        )
