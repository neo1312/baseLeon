from django.core.management.base import BaseCommand
from crm.models import Client, ClientTierStatus


class Command(BaseCommand):
    help = 'Recalculate all client tier statuses based on last 30 days of sales'

    def handle(self, *args, **options):
        clients = Client.objects.all()
        updated_count = 0
        
        for client in clients:
            try:
                tier_status = client.tier_status
                old_tier = tier_status.tier.get_name_display() if tier_status.tier else "None"
                tier_status.get_current_tier()
                new_tier = tier_status.tier.get_name_display() if tier_status.tier else "None"
                
                if old_tier != new_tier:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated {client.name}: {old_tier} → {new_tier} (Last 30 days: ${tier_status.last_30_days_sales:,.2f})"
                        )
                    )
                    updated_count += 1
                else:
                    self.stdout.write(
                        f"Unchanged {client.name}: {new_tier} (Last 30 days: ${tier_status.last_30_days_sales:,.2f})"
                    )
            except ClientTierStatus.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"No tier status for client: {client.name}")
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nTier recalculation complete. Updated: {updated_count} clients')
        )
