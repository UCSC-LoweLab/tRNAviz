#!/usr/bin/env python3
"""Find assembly taxids from euk-20211230-genomes.tsv that are NOT in the
tRNAviz production database, count their tRNAs, and print the 10 smallest
as good test candidates."""

import csv
import os
import sys
from collections import Counter

# ------------------------------------------------------------------
# 1. Bootstrap Django
# ------------------------------------------------------------------
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tRNAviz.settings')

import django
django.setup()

from explorer.models import Taxonomy

# ------------------------------------------------------------------
# 2. Read genomes.tsv  (assembly taxids + metadata)
# ------------------------------------------------------------------
GENOMES_FILE = os.path.join(PROJECT_DIR, 'process-data', 'euk-20211230-genomes.tsv')
TRNAS_FILE   = os.path.join(PROJECT_DIR, 'process-data', 'euk-20211230-trnas.tsv')

file_species = {}   # taxid -> {dbname, name}
with open(GENOMES_FILE, newline='') as fh:
    reader = csv.DictReader(fh, delimiter='\t')
    for row in reader:
        taxid = row['taxid'].strip()
        file_species[taxid] = {
            'dbname': row['dbname'].strip(),
            'name':   row['name'].strip(),
        }

print(f"Genomes file: {len(file_species)} species (assembly taxids)")

# ------------------------------------------------------------------
# 3. Query the database for existing assembly taxids
# ------------------------------------------------------------------
# The Taxonomy model stores rows at every rank. Assembly-level rows
# have rank = 'assembly' (or the taxid appears in the assembly field).
# We look for all taxids that exist at the assembly rank.
existing_assembly_taxids = set(
    Taxonomy.objects.filter(
        taxid__in=list(file_species.keys())
    ).values_list('taxid', flat=True)
)

print(f"Database: {len(existing_assembly_taxids)} of those taxids already present in Taxonomy table")

# ------------------------------------------------------------------
# 4. Compute the set difference
# ------------------------------------------------------------------
new_taxids = set(file_species.keys()) - existing_assembly_taxids
print(f"New (not in DB): {len(new_taxids)} assembly taxids\n")

if not new_taxids:
    print("All assembly taxids from the file are already in the database.")
    sys.exit(0)

# ------------------------------------------------------------------
# 5. Count tRNA rows per dbname in the tRNAs file
# ------------------------------------------------------------------
# Build a lookup: dbname -> taxid (for the new species only)
new_dbnames = {}
for taxid in new_taxids:
    dbname = file_species[taxid]['dbname']
    new_dbnames[dbname] = taxid

trna_counts = Counter()
with open(TRNAS_FILE, newline='') as fh:
    reader = csv.DictReader(fh, delimiter='\t')
    for row in reader:
        dbname = row['dbname'].strip()
        if dbname in new_dbnames:
            trna_counts[dbname] += 1

# ------------------------------------------------------------------
# 6. Build result list, sorted by tRNA count ascending
# ------------------------------------------------------------------
results = []
for taxid in new_taxids:
    info = file_species[taxid]
    count = trna_counts.get(info['dbname'], 0)
    results.append((info['dbname'], taxid, info['name'], count))

results.sort(key=lambda r: r[3])   # sort by tRNA count

# ------------------------------------------------------------------
# 7. Print the 10 smallest as test candidates
# ------------------------------------------------------------------
print("=" * 90)
print(f"{'dbname':<40} {'taxid':<12} {'tRNAs':>6}  name")
print("-" * 90)
for dbname, taxid, name, count in results[:10]:
    print(f"{dbname:<40} {taxid:<12} {count:>6}  {name}")
print("=" * 90)

# Also print full list
print(f"\nAll {len(results)} new species (sorted by tRNA count):")
print(f"{'dbname':<40} {'taxid':<12} {'tRNAs':>6}  name")
print("-" * 90)
for dbname, taxid, name, count in results:
    print(f"{dbname:<40} {taxid:<12} {count:>6}  {name}")
print(f"\ntRNA count range: {results[0][3]} - {results[-1][3]}")
