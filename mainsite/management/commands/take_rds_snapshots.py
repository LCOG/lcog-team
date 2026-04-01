from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

import boto3
from botocore.exceptions import BotoCoreError, ClientError, ProfileNotFound

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Takes manual RDS snapshots for staging/production and prunes old manual snapshots.'

    REGION = 'us-west-2'
    RETENTION_DAYS = 90

    TARGETS = {
        'staging': {
            'instance_id': 'lcog-team-staging',
            'snapshot_prefix': 'staging-manual',
        },
        'production': {
            'instance_id': 'lcog-team-production-db',
            'snapshot_prefix': 'production-manual',
        },
    }

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--only-staging',
            action='store_true',
            help='Only run snapshot + cleanup for staging.',
        )
        group.add_argument(
            '--only-production',
            action='store_true',
            help='Only run snapshot + cleanup for production.',
        )
        group.add_argument(
            '--all',
            action='store_true',
            help='Run snapshot + cleanup for both staging and production.',
        )
        parser.add_argument(
            '--prune',
            action='store_true',
            help='Prune old snapshots.',
        )
        parser.add_argument(
            '--aws-profile',
            help='AWS named profile to use for credentials (for example: production-admin).',
        )

    def _build_snapshot_identifier(self, prefix, now_utc):
        return f"{prefix}-{now_utc.strftime('%Y%m%d-%H%M')}"

    def _initiate_snapshot(self, rds_client, instance_id, snapshot_identifier):
        rds_client.create_db_snapshot(
            DBSnapshotIdentifier=snapshot_identifier,
            DBInstanceIdentifier=instance_id,
        )

    def _wait_for_snapshot(self, rds_client, snapshot_identifier):
        waiter = rds_client.get_waiter('db_snapshot_available')
        waiter.wait(DBSnapshotIdentifier=snapshot_identifier)

    def _delete_old_manual_snapshots(self, rds_client, instance_id, cutoff_datetime):
        deleted_snapshot_ids = []
        paginator = rds_client.get_paginator('describe_db_snapshots')
        pages = paginator.paginate(
            DBInstanceIdentifier=instance_id,
            SnapshotType='manual',
        )

        for page in pages:
            for snapshot in page.get('DBSnapshots', []):
                snapshot_created_at = snapshot.get('SnapshotCreateTime')
                snapshot_id = snapshot.get('DBSnapshotIdentifier')

                if not snapshot_created_at or not snapshot_id:
                    continue
                if snapshot_created_at >= cutoff_datetime:
                    continue

                rds_client.delete_db_snapshot(DBSnapshotIdentifier=snapshot_id)
                deleted_snapshot_ids.append(snapshot_id)

        return deleted_snapshot_ids

    def _get_rds_client(self, aws_profile=None):
        if aws_profile:
            session = boto3.Session(profile_name=aws_profile)
            return session.client('rds', region_name=self.REGION)
        return boto3.client('rds', region_name=self.REGION)

    def handle(self, *args, **options):
        if options['only_staging']:
            selected_targets = ['staging']
        elif options['only_production']:
            selected_targets = ['production']
        elif options['all']:
            selected_targets = ['staging', 'production']
        else:
            selected_targets = []

        now_utc = datetime.now(timezone.utc)
        cutoff_datetime = now_utc - timedelta(days=self.RETENTION_DAYS)
        aws_profile = options.get('aws_profile')

        try:
            rds_client = self._get_rds_client(aws_profile=aws_profile)

            if aws_profile:
                self.stdout.write(f'Using AWS profile: {aws_profile}')

            # Kick off all snapshots before waiting on any of them
            snapshot_jobs = {}
            for target_name in selected_targets:
                target = self.TARGETS[target_name]
                snapshot_identifier = self._build_snapshot_identifier(
                    target['snapshot_prefix'],
                    now_utc,
                )
                self.stdout.write(f'Creating {target_name} snapshot: {snapshot_identifier}...')
                self._initiate_snapshot(rds_client, target['instance_id'], snapshot_identifier)
                snapshot_jobs[target_name] = snapshot_identifier

            # Poll each snapshot concurrently
            if snapshot_jobs:
                self.stdout.write(
                    f'Waiting for {len(snapshot_jobs)} snapshot(s) to become available...'
                )
                with ThreadPoolExecutor(max_workers=len(snapshot_jobs)) as executor:
                    futures = {
                        executor.submit(self._wait_for_snapshot, rds_client, snap_id): target_name
                        for target_name, snap_id in snapshot_jobs.items()
                    }
                    for future in as_completed(futures):
                        target_name = futures[future]
                        future.result()  # re-raises any exception from the waiter
                        self.stdout.write(self.style.SUCCESS(
                            f'Snapshot {snapshot_jobs[target_name]} is now available.'
                        ))

            if options['prune']:
                for target_name in selected_targets:
                    target = self.TARGETS[target_name]
                    deleted_snapshot_ids = self._delete_old_manual_snapshots(
                        rds_client,
                        target['instance_id'],
                        cutoff_datetime,
                    )

                    if deleted_snapshot_ids:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Deleted {len(deleted_snapshot_ids)} old {target_name} manual snapshot(s): "
                                f"{', '.join(deleted_snapshot_ids)}"
                            )
                        )
                    else:
                        self.stdout.write(
                            f"No old {target_name} manual snapshots older than {self.RETENTION_DAYS} days."
                        )

        except ProfileNotFound as exc:
            raise CommandError(f'AWS profile not found: {exc}') from exc
        except (BotoCoreError, ClientError) as exc:
            raise CommandError(f'RDS snapshot command failed: {exc}') from exc