"""Management command to incrementally add or remove a species from tRNAviz.

Usage:
  python manage.py add_species genomes.tsv trnas.tsv [--skip-ncbi] [--dry-run]
  python manage.py add_species --remove 933801 [--dry-run]
"""

import csv
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from explorer.models import Taxonomy, tRNA as tRNAModel, Consensus, Freq
from explorer.load_utils import (
    RANKS, RANK_TO_FIELD, ISOTYPES, SUMMARY_SINGLE_POSITIONS, SUMMARY_PAIRED_POSITIONS,
    PAIRED_FEATURE_MAP, pos_to_field, tsv_col_to_field, fetch_ncbi_names,
    determine_single_consensus, determine_paired_consensus,
)


GENOMES_REQUIRED_COLS = {
    'dbname', 'taxid', 'name', 'domain', 'kingdom', 'subkingdom', 'phylum',
    'subphylum', 'class', 'subclass', 'order', 'family', 'genus', 'species', 'assembly',
}


def load_trna_dataframe_for_taxid(taxid, rank):
    """Load tRNA data into a DataFrame for a specific taxid at a given rank."""
    field = RANK_TO_FIELD.get(rank, rank)
    single_fields = [pos_to_field(p) for p in SUMMARY_SINGLE_POSITIONS]
    paired_fields = [pos_to_field(p) for p in SUMMARY_PAIRED_POSITIONS]
    columns = ['isotype'] + single_fields + paired_fields
    qs = tRNAModel.objects.filter(**{field: taxid}).values_list(*columns)
    return pd.DataFrame(list(qs), columns=columns)


def recompute_freq_for_taxid(taxid, rank, df):
    """Recompute Freq records for a single taxid from the given DataFrame."""
    freq_objects = []
    for isotype in ISOTYPES + ['All']:
        iso_df = df if isotype == 'All' else df[df['isotype'] == isotype]
        if len(iso_df) == 0:
            continue

        for pos in SUMMARY_SINGLE_POSITIONS:
            fn = pos_to_field(pos)
            if fn not in iso_df.columns:
                continue
            counts = iso_df[fn].value_counts()
            freq_objects.append(Freq(
                taxid=taxid, isotype=isotype, position=pos, total=len(iso_df),
                A=int(counts.get('A', 0)), C=int(counts.get('C', 0)),
                G=int(counts.get('G', 0)), U=int(counts.get('U', 0)),
                Absent=int(counts.get('-', 0)),
            ))

        for pos in SUMMARY_PAIRED_POSITIONS:
            fn = pos_to_field(pos)
            if fn not in iso_df.columns:
                continue
            counts = iso_df[fn].value_counts()
            kwargs = {'taxid': taxid, 'isotype': isotype, 'position': pos,
                      'total': len(iso_df)}
            for pair_str, attr in PAIRED_FEATURE_MAP.items():
                kwargs[attr] = int(counts.get(pair_str, 0))
            freq_objects.append(Freq(**kwargs))

    return freq_objects


def recompute_consensus_for_taxid(taxid, rank, df):
    """Recompute Consensus records for a single taxid from the given DataFrame."""
    cons_objects = []
    for isotype in ISOTYPES + ['All']:
        iso_df = df if isotype == 'All' else df[df['isotype'] == isotype]
        if len(iso_df) == 0:
            continue

        n = len(iso_df)
        cons_kwargs = {'taxid': taxid, 'isotype': isotype, 'datatype': 'Consensus'}
        near_kwargs = {'taxid': taxid, 'isotype': isotype, 'datatype': 'Near-consensus'}

        for pos in SUMMARY_SINGLE_POSITIONS:
            fn = pos_to_field(pos)
            if fn not in iso_df.columns:
                cons_kwargs[fn] = None
                near_kwargs[fn] = None
                continue
            counts = dict(iso_df[fn].value_counts())
            cons_kwargs[fn] = determine_single_consensus(counts, n, 0.5)
            near_kwargs[fn] = determine_single_consensus(counts, n, 0.25)

        for pos in SUMMARY_PAIRED_POSITIONS:
            fn = pos_to_field(pos)
            if fn not in iso_df.columns:
                cons_kwargs[fn] = None
                near_kwargs[fn] = None
                continue
            counts = dict(iso_df[fn].value_counts())
            cons_kwargs[fn] = determine_paired_consensus(counts, n, 0.5)
            near_kwargs[fn] = determine_paired_consensus(counts, n, 0.25)

        cons_objects.append(Consensus(**cons_kwargs))
        cons_objects.append(Consensus(**near_kwargs))

    return cons_objects


def recompute_aggregates(affected_taxids, stdout):
    """Delete old Freq/Consensus and recompute for each affected taxid."""
    total_freq = 0
    total_cons = 0

    for taxid in affected_taxids:
        tax_qs = Taxonomy.objects.filter(taxid=taxid)
        if not tax_qs.exists():
            continue
        tax = tax_qs.first()
        rank = tax.rank

        df = load_trna_dataframe_for_taxid(taxid, rank)

        Freq.objects.filter(taxid=taxid).delete()
        Consensus.objects.filter(taxid=taxid).delete()

        if len(df) == 0:
            continue

        freq_objects = recompute_freq_for_taxid(taxid, rank, df)
        if freq_objects:
            Freq.objects.bulk_create(freq_objects)
            total_freq += len(freq_objects)

        cons_objects = recompute_consensus_for_taxid(taxid, rank, df)
        if cons_objects:
            Consensus.objects.bulk_create(cons_objects)
            total_cons += len(cons_objects)

        stdout.write(f'  Recomputed taxid {taxid} ({tax.name}): '
                     f'{len(freq_objects)} freq, {len(cons_objects)} consensus')

    return total_freq, total_cons


def collect_lineage_taxids(genomes_rows):
    """Collect all unique taxids at every rank level from genome rows."""
    taxids = set()
    for row in genomes_rows:
        for rank in RANKS:
            val = row.get(rank, '').strip()
            if val:
                taxids.add(val)
    return taxids


class Command(BaseCommand):
    help = 'Incrementally add or remove a species from tRNAviz'

    def add_arguments(self, parser):
        parser.add_argument('genomes_tsv', nargs='?', help='Path to genomes.tsv file')
        parser.add_argument('trnas_tsv', nargs='?', help='Path to tRNAs.tsv file')
        parser.add_argument('--remove', metavar='TAXID',
                            help='Remove an assembly by its taxid instead of adding')
        parser.add_argument('--skip-ncbi', action='store_true',
                            help='Skip NCBI Entrez name lookup')
        parser.add_argument('--dry-run', action='store_true',
                            help='Validate inputs without modifying the database')

    def handle(self, *args, **options):
        if options['remove']:
            self._handle_remove(options['remove'], options['dry_run'])
        else:
            if not options['genomes_tsv'] or not options['trnas_tsv']:
                raise CommandError('Both genomes_tsv and trnas_tsv are required for adding species')
            self._handle_add(options['genomes_tsv'], options['trnas_tsv'],
                             options['skip_ncbi'], options['dry_run'])

    def _handle_add(self, genomes_path, trnas_path, skip_ncbi, dry_run):
        self.stdout.write('=== Adding species ===')

        # Step 1: Parse genomes.tsv
        self.stdout.write(f'Reading {genomes_path}...')
        genomes_rows = []
        taxon_info = {}
        assembly_names = {}

        with open(genomes_path, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            headers = set(reader.fieldnames or [])
            missing = GENOMES_REQUIRED_COLS - headers
            if missing:
                raise CommandError(f'genomes.tsv missing columns: {missing}')

            for row in reader:
                genomes_rows.append(row)
                for rank in RANKS:
                    taxid = row.get(rank, '').strip()
                    if not taxid or taxid in taxon_info:
                        continue

                    lineage = {}
                    for r in RANKS:
                        field = RANK_TO_FIELD[r]
                        val = row.get(r, '').strip()
                        lineage[field] = val if val else None
                        if r == rank:
                            break
                    below = False
                    for r in RANKS:
                        if below:
                            lineage[RANK_TO_FIELD[r]] = None
                        if r == rank:
                            below = True

                    taxon_info[taxid] = {'rank': rank, 'lineage': lineage}
                    if rank == 'assembly':
                        assembly_names[taxid] = row['name']

        self.stdout.write(f'  Found {len(genomes_rows)} assemblies, '
                          f'{len(taxon_info)} unique taxa')

        # Step 2: Check for duplicate assemblies
        assembly_taxids = [tid for tid, d in taxon_info.items() if d['rank'] == 'assembly']
        existing = set(Taxonomy.objects.filter(
            taxid__in=assembly_taxids, rank='assembly'
        ).values_list('taxid', flat=True))
        if existing:
            raise CommandError(f'Assemblies already exist in DB: {existing}')

        # Step 3: Parse tRNAs.tsv
        self.stdout.write(f'Reading {trnas_path}...')
        trna_records = []
        with open(trnas_path, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                kwargs = {}
                for col, value in row.items():
                    field = tsv_col_to_field(col)
                    if field == 'primary':
                        value = (value == 'True')
                    elif field in ('score', 'isoscore', 'isoscore_ac', 'GCcontent'):
                        value = float(value)
                    elif field in ('insertions', 'deletions', 'intron_length',
                                   'dloop', 'acloop', 'tpcloop', 'varm'):
                        value = int(value)
                    elif value == '':
                        value = None
                    kwargs[field] = value
                trna_records.append(kwargs)

        self.stdout.write(f'  Parsed {len(trna_records)} tRNA records')

        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                '\n[DRY RUN] Validation passed. No changes made.'))
            return

        # Step 4: Apply all mutations atomically
        with transaction.atomic():
            # Insert Taxonomy entries (skip taxids that already exist)
            existing_taxids = set(Taxonomy.objects.filter(
                taxid__in=list(taxon_info.keys())
            ).values_list('taxid', flat=True))
            new_taxids = set(taxon_info.keys()) - existing_taxids

            # Fetch NCBI names for new non-assembly taxids
            if not skip_ncbi:
                need_names = [tid for tid in new_taxids
                              if taxon_info[tid]['rank'] != 'assembly']
                if need_names:
                    self.stdout.write(f'  Fetching {len(need_names)} names from NCBI...')
                    ncbi_names = fetch_ncbi_names(need_names)
                else:
                    ncbi_names = {}
            else:
                ncbi_names = {}

            tax_objects = []
            for taxid in new_taxids:
                data = taxon_info[taxid]
                if data['rank'] == 'assembly':
                    name = assembly_names.get(taxid, taxid)
                else:
                    name = ncbi_names.get(taxid, f'Taxon {taxid}')
                tax_objects.append(Taxonomy(
                    taxid=taxid, rank=data['rank'], name=name, **data['lineage']
                ))

            if tax_objects:
                Taxonomy.objects.bulk_create(tax_objects)
                self.stdout.write(f'  Created {len(tax_objects)} new Taxonomy entries '
                                  f'(skipped {len(existing_taxids)} existing)')

            # Insert tRNA records
            trna_objects = [tRNAModel(**kwargs) for kwargs in trna_records]
            batch_size = 5000
            for i in range(0, len(trna_objects), batch_size):
                tRNAModel.objects.bulk_create(trna_objects[i:i+batch_size])
            self.stdout.write(f'  Created {len(trna_objects)} tRNA records')

            # Recompute Freq/Consensus for all affected taxids
            affected_taxids = collect_lineage_taxids(genomes_rows)
            self.stdout.write(f'  Recomputing aggregates for {len(affected_taxids)} taxids...')
            total_freq, total_cons = recompute_aggregates(affected_taxids, self.stdout)

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created {len(tax_objects)} taxonomy, {len(trna_objects)} tRNAs, '
            f'{total_freq} freq, {total_cons} consensus records'))

    def _handle_remove(self, assembly_taxid, dry_run):
        self.stdout.write(f'=== Removing assembly {assembly_taxid} ===')

        # Step 1: Look up the assembly
        try:
            assembly_tax = Taxonomy.objects.get(taxid=assembly_taxid, rank='assembly')
        except Taxonomy.DoesNotExist:
            raise CommandError(f'No assembly found with taxid {assembly_taxid}')

        self.stdout.write(f'  Found: {assembly_tax.name}')

        # Step 2: Collect full lineage taxids
        lineage_taxids = set()
        for rank in RANKS:
            field = RANK_TO_FIELD[rank]
            val = getattr(assembly_tax, field, None)
            if val:
                lineage_taxids.add(val)

        trna_count = tRNAModel.objects.filter(assembly=assembly_taxid).count()
        self.stdout.write(f'  Found {trna_count} tRNA records for this assembly')
        self.stdout.write(f'  Lineage has {len(lineage_taxids)} taxids to recompute')

        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                '\n[DRY RUN] Validation passed. No changes made.'))
            return

        with transaction.atomic():
            # Step 3: Delete tRNA records
            deleted_trnas, _ = tRNAModel.objects.filter(assembly=assembly_taxid).delete()
            self.stdout.write(f'  Deleted {deleted_trnas} tRNA records')

            # Step 4: Delete assembly's own Taxonomy/Freq/Consensus
            Freq.objects.filter(taxid=assembly_taxid).delete()
            Consensus.objects.filter(taxid=assembly_taxid).delete()
            assembly_tax.delete()
            self.stdout.write(f'  Deleted assembly taxonomy/freq/consensus')

            # Step 5: Clean up orphaned ancestor Taxonomy entries
            ancestor_taxids = lineage_taxids - {assembly_taxid}
            orphaned = []
            for taxid in ancestor_taxids:
                tax_qs = Taxonomy.objects.filter(taxid=taxid)
                if not tax_qs.exists():
                    continue
                tax = tax_qs.first()
                field = RANK_TO_FIELD.get(tax.rank, tax.rank)
                if not tRNAModel.objects.filter(**{field: taxid}).exists():
                    Freq.objects.filter(taxid=taxid).delete()
                    Consensus.objects.filter(taxid=taxid).delete()
                    tax.delete()
                    orphaned.append(taxid)

            if orphaned:
                self.stdout.write(f'  Removed {len(orphaned)} orphaned ancestor taxa')

            # Step 6: Recompute for remaining affected ancestors
            remaining = ancestor_taxids - set(orphaned)
            if remaining:
                self.stdout.write(f'  Recomputing aggregates for {len(remaining)} ancestor taxids...')
                total_freq, total_cons = recompute_aggregates(remaining, self.stdout)
            else:
                total_freq = total_cons = 0

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Removed assembly {assembly_taxid}, '
            f'recomputed {total_freq} freq + {total_cons} consensus records'))
