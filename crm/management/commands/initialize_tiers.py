from django.core.management.base import BaseCommand
from crm.models import ClientTier, Client, ClientTierStatus
from decimal import Decimal


class Command(BaseCommand):
    help = 'Initialize default client tiers and create tier statuses for existing clients'

    def handle(self, *args, **options):
        tiers_data = [
            {'name': 'gold', 'min_monthly_sales': Decimal('15000.00'), 'wallet_percentage': Decimal('3.00')},
            {'name': 'silver', 'min_monthly_sales': Decimal('5000.00'), 'wallet_percentage': Decimal('1.50')},
            {'name': 'bronze', 'min_monthly_sales': Decimal('1500.00'), 'wallet_percentage': Decimal('0.75')},
        ]

        # Create or update tiers
        for tier_data in tiers_data:
            tier, created = ClientTier.objects.update_or_create(
                name=tier_data['name'],
                defaults={
                    'min_monthly_sales': tier_data['min_monthly_sales'],
                    'wallet_percentage': tier_data['wallet_percentage']
                }
            )
            action = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{action} tier: {tier.get_name_display()} - "
                    f"Min Sales: ${tier.min_monthly_sales} - Reward: {tier.wallet_percentage}%"
                )
            )

        # Create tier statuses for all existing clients
        clients = Client.objects.all()
        created_count = 0
        
        for client in clients:
            tier_status, created = ClientTierStatus.objects.get_or_create(client=client)
            if created:
                created_count += 1
                tier_status.get_current_tier()  # Calculate initial tier
                self.stdout.write(
                    self.style.SUCCESS(f"Created tier status for client: {client.name}")
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created tier statuses for {created_count} clients')
        )
