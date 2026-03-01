import requests
from django.core.management.base import BaseCommand
from users.models import Opportunity
from django.utils import timezone

class Command(BaseCommand):
    help = 'Checks open opportunities and automatically closes them if the original link is dead (404/timeout).'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting Dead-Link Checker...'))
        
        # Only check trials that are currently marked as open and have a link
        open_opportunities = Opportunity.objects.filter(is_open=True).exclude(link='')
        
        if not open_opportunities.exists():
            self.stdout.write(self.style.WARNING('No open opportunities with links found.'))
            return

        closed_count = 0
        checked_count = 0
        
        # Use a standard browser user-agent to avoid being instantly blocked by strict bot protections
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        for opp in open_opportunities:
            checked_count += 1
            url = opp.link.strip()
            
            try:
                # We only need the headers to check status, so we use a HEAD request when possible
                # However, some cheap web servers block HEAD, so we use a GET with a fast timeout
                response = requests.get(url, headers=headers, timeout=10)
                
                # If the page returns a 404 (Not Found) or 410 (Gone), it means the trial was removed
                if response.status_code in [404, 410]:
                    self.stdout.write(self.style.WARNING(f'Closing dead link ({response.status_code}): {url}'))
                    opp.is_open = False
                    opp.save()
                    closed_count += 1
                else:
                    self.stdout.write(f'Link OK ({response.status_code}): {url}')
                    
            except requests.exceptions.Timeout:
                # If it times out, the site might just be slow today, so we don't close it immediately.
                self.stdout.write(self.style.ERROR(f'Timeout, keeping alive for now: {url}'))
            except requests.exceptions.RequestException as e:
                # For DNS failures or complete connection refusals, it's dead.
                self.stdout.write(self.style.ERROR(f'Connection failed, closing link: {url}'))
                opp.is_open = False
                opp.save()
                closed_count += 1

        self.stdout.write(self.style.SUCCESS(f'\nFinished! Checked {checked_count} links. Auto-closed {closed_count} dead trials.'))
