# tRNAviz Handoff: Generating Test Data from Brian Lin's Code

## Context

This document is a handoff from a Claude Code session running on AWS to a Claude Code
session running on `hoag` (Lowe Lab, /projects/lowelab/). The goal is to find and use
Brian Lin's original data-preparation code to generate `genomes.tsv` and `trnas.tsv`
files for a test species, so we can validate the `add_species` management command in
the tRNAviz Django web application.

## What is tRNAviz?

tRNAviz is a Django web application for visualizing tRNA sequence features across the
tree of life. It stores tRNA genes with per-position base identity (using Sprinzl
numbering), computes consensus and frequency summaries at every taxonomic rank, and
displays them as interactive heatmaps and cloverleaf diagrams.

- **GitHub repo:** UCSC-LoweLab/tRNAviz
- **Live site:** trnaviz.ucsc.edu
- **Stack:** Django 5.2 / MySQL / Python 3

## What was done on the AWS instance

Recent commits on master (most recent first):

1. `d6a9ea8` - Fix iTOL tree visualization: client-side upload and root node crash
2. `f691a37` - Migrate from PostgreSQL/SQLite to MySQL backend
3. `4a16557` - Add database indexes for MySQL performance
4. `ceb03d9` - Add load_pgdump management command
5. `fb452ff` - Fix species distribution bug and add incremental `add_species` command
6. Earlier: Django 5.2 upgrade, security fixes, cloverleaf coordinates

The key new feature is `python manage.py add_species`, which can incrementally add or
remove species without reloading the entire database. It needs two input files.

## The two input files needed

### 1. `genomes.tsv` (tab-separated, one row per genome assembly)

Required columns:
```
dbname  taxid  name  domain  kingdom  subkingdom  phylum  subphylum  class  subclass  order  family  genus  species  assembly
```

- `dbname`: short identifier for the genome (e.g. "hg38", "sacCer3")
- `taxid`: NCBI Taxonomy ID for the assembly (note: this is often a strain-level taxid)
- `name`: organism/assembly display name
- `domain` through `assembly`: NCBI taxids for each taxonomic rank in the lineage
  (not names -- numeric NCBI taxids stored as strings, e.g. "2759" for Eukaryota)

### 2. `trnas.tsv` (tab-separated, one row per tRNA gene)

Columns:
```
seqname  isotype  anticodon  score  primary  best_model  isoscore  isoscore_ac
dbname  domain  kingdom  subkingdom  phylum  subphylum  class  subclass
order  family  genus  species  assembly
GCcontent  insertions  deletions  intron_length  dloop  acloop  tpcloop  varm
1:72  1  2:71  2  3:70  3  4:69  4  5:68  5  6:67  6  7:66  7
8  8:14  9  9:23  10:25  10  10:45  11:24  11  12:23  12  13:22  13
14  15  15:48  16  17  17a  18  18:55  19  19:56  20  20a  20b  21
22  22:46  23  24  25  26  26:44  27:43  27  28:42  28  29:41  29
30:40  30  31:39  31  32  33  34  35  36  37  38  39  40  41  42  43
44  45  V11:V21  V12:V22  V13:V23  V14:V24  V15:V25  V16:V26  V17:V27
V1  V2  V3  V4  V5  V11  V12  V13  V14  V15  V16  V17
V21  V22  V23  V24  V25  V26  V27
46  47  48  49:65  49  50:64  50  51:63  51  52:62  52  53:61  53
54  54:58  55  56  57  58  59  60  61  62  63  64  65  66  67  68
69  70  71  72  73  74  75  76
```

Key details:
- `seqname`: unique tRNA identifier (primary key), e.g. "hg38-tRNA-Ala-AGC-1-1"
- `isotype`: amino acid (Ala, Arg, ..., Val, fMet, iMet)
- `primary`: "True" or "False" (whether this is the primary/best prediction)
- Lineage columns: same numeric NCBI taxids as genomes.tsv
- Position columns use Sprinzl numbering. Single positions have values: A, C, G, U, or -
- Paired positions (e.g. "1:72") have values like "G:C", "A:U", "-:-", etc.
- `GCcontent`: float; `insertions`, `deletions`, `intron_length`, `dloop`, `acloop`,
  `tpcloop`, `varm`: integers

## Your task on hoag

### Step 1: Find Brian Lin's data preparation code

Brian Lin was the original developer of tRNAviz. His code for generating the TSV files
from tRNAscan-SE output is likely somewhere under `/projects/lowelab/`. Look for:

- A directory named something like `tRNAviz`, `trnaviz`, `tRNA-viz`, or `trna_viz`
  in Brian's home directory or project space
- Python scripts that read tRNAscan-SE output (`.out` files, `.ss` secondary structure
  files, or `.iso` isotype-specific files) and produce TSV/CSV with the column structure
  described above
- Look for files containing keywords like: `sprinzl`, `alignment`, `position`, `isotype`,
  `genomes.tsv`, `trnas.tsv`, `trnascan`, `GtRNAdb`
- His username may be `blin` or `brianlin` or similar

Likely locations to search:
```
/projects/lowelab/users/blin/
/projects/lowelab/users/brianlin/
/home/blin/
/projects/lowelab/tRNAviz/
/projects/lowelab/GtRNAdb/
```

### Step 2: Understand the data pipeline

Once you find the code, map out the pipeline:
1. What input does it take? (tRNAscan-SE output files, genome metadata, NCBI taxonomy)
2. How does it map tRNA sequences to Sprinzl positions? (likely via covariance model
   alignment or structure-based mapping)
3. How does it construct the lineage taxid columns?
4. How does it compute `GCcontent`, loop sizes (`dloop`, `acloop`, `tpcloop`), and
   variable arm length (`varm`)?

### Step 3: Generate test data for one species

Pick a small, well-characterized genome that is NOT already in the tRNAviz database.
Good candidates:
- A newly sequenced yeast (check what's already in tRNAviz first)
- A small bacterial genome
- Any organism with tRNAscan-SE results readily available on the lab disk

Generate the two TSV files (`genomes.tsv` and `trnas.tsv`) using Brian's pipeline,
or by adapting it.

### Step 4: Validate the files

Quick sanity checks:
- `genomes.tsv` should have all 15 required columns, with numeric taxids in the
  lineage columns
- `trnas.tsv` `seqname` values must be unique (it's the primary key)
- Paired position values should be in "X:Y" format (e.g., "G:C", "-:-")
- Single position values should be single characters (A, C, G, U, or -)
- The `assembly` taxid in `trnas.tsv` must match a row in `genomes.tsv`

### Step 5: Test the add_species command

If you have access to the tRNAviz repo and a running dev instance:
```bash
# Dry run first
python manage.py add_species genomes.tsv trnas.tsv --dry-run

# If that passes, add for real
python manage.py add_species genomes.tsv trnas.tsv --skip-ncbi

# Test removal round-trip
python manage.py add_species --remove <assembly_taxid> --dry-run
```

## Reference: tRNAviz Django model structure

The tRNA model has ~130 position fields using Sprinzl numbering. Field naming convention:
- Single positions: `p8`, `p9`, `p14`, `p17a`, `pV1`, etc.
- Paired positions: `p1_72`, `p10_25`, `pV11_V21`, etc.

The TSV column-to-field mapping is in `explorer/load_utils.py:tsv_col_to_field()`:
- TSV column `class` maps to Django field `taxclass` (reserved word)
- Position columns like `1:72` map to `p1_72` (prefix `p`, colon becomes underscore)

## Known issue: Dependabot vulnerability

GitHub is flagging a moderate vulnerability in Biopython. This is not urgent and we
are waiting for an upstream fix. No action needed.

## Contact

This handoff was prepared by Todd Lowe's Claude Code session on AWS.
The tRNAviz GitHub repo is at: github.com/UCSC-LoweLab/tRNAviz
