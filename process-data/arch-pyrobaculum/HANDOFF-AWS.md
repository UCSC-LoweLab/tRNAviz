# Pyrobaculum tRNAviz Loading — AWS Handoff

## Goal
Add 7 Pyrobaculum species (Crenarchaeota) to the tRNAviz Django web app.

## What's Already Done

### Files staged at ~/ClaudeCode/tRNAviz/process-data/arch-pyrobaculum/

1. **data/{out,ss,iso}/** — tRNAscan-SE output for 7 species (21 files):
   - pyrAer1-tRNAs.{out,ss,iso} — Pyrobaculum aerophilum str. IM2
   - pyroArse1-tRNAs.{out,ss,iso} — Pyrobaculum arsenaticum DSM 13514
   - pyroCali1-tRNAs.{out,ss,iso} — Pyrobaculum calidifontis JCM 11548
   - pyroIsla1-tRNAs.{out,ss,iso} — Pyrobaculum islandicum DSM 4184
   - pyroOgun2-tRNAs.{out,ss,iso} — Pyrobaculum oguniense TE7
   - pyro1860_1-tRNAs.{out,ss,iso} — Pyrobaculum sp. 1860 (P. ferrireducens)
   - therNeut1-tRNAs.{out,ss,iso} — Thermoproteus neutrophilus V24Sta (P. neutrophilum)

2. **genomes.tsv** — Tab-delimited genome metadata with NCBI taxonomy IDs:
   - 15 columns: dbname, taxid, name, domain, kingdom, subkingdom, phylum, subphylum, class, subclass, order, family, genus, species, assembly
   - Taxonomy uses numeric NCBI taxids (matching existing tRNAviz convention)
   - Phylum 28889 = Crenarchaeota (old taxonomy, matches existing DB entries)
   - Verify: `awk -F'\t' '{print NF}' genomes.tsv | sort -u` should return 15

3. **sstofa3** — Modified Perl script (chmod +x) that strips non-canonical introns
   - Original from https://github.com/UCSC-LoweLab/tRNAviz-data/blob/master/sstofa3
   - Added in the mature tRNA (else) block after canonical intron handling:
     ```perl
     # Strip non-canonical intron bases (lowercase chars in Seq line)
     $Seq =~ s/[a-z]//g;
     $SeqLen = length($Seq);
     ```
   - This removes non-canonical BHB introns that appear as lowercase letters in .ss Seq: lines
   - Only affects mature tRNA output ($mature=1); pre-tRNA output unchanged

## Non-canonical Intron Background

Pyrobaculum tRNAs have non-canonical introns that tRNAscan-SE does NOT detect as introns. In .ss files they appear in two ways:

**Canonical introns** (detected by tRNAscan-SE):
- Annotated with "Possible intron: X-Y" line
- Shown in [brackets] on Pre: line, spliced out of Seq: line
- Already handled by original sstofa3

**Non-canonical introns** (NOT detected, Pyrobaculum-specific):
- NO "Possible intron" annotation, NO Pre: line
- Appear as lowercase letters embedded in the Seq: line
- Example from pyroCali1 Leu-CAG: `GCGGGGGTGCCCGAGCCaGGTcaAAGGGGCAGGGTTCAGGTCCCTGTGGCGCAGGCCTgCGTGGGTTCAAATCCCACCCCCCGCA`
- The `a`, `ca`, `g` are non-canonical intron bases
- The modified sstofa3 strips these when producing mature tRNA sequences

## Remaining Tasks

### Task 1: Run parse-tRNAs.py to generate trnas.tsv

parse-tRNAs.py is from the tRNAviz-data pipeline (https://github.com/UCSC-LoweLab/tRNAviz-data).
It may already be installed on this machine. Check:
- ~/ClaudeCode/tRNAviz/ or nearby
- /projects/lowelab/users/blin/tRNAviz/

The archaeal covariance model needed for numbering:
- /projects/lowelab/users/blin/tRNAviz/process-data/arch/arch-num-041017.cm

Expected command (run from ~/ClaudeCode/tRNAviz/process-data/arch-pyrobaculum/):
```bash
python3 /path/to/parse-tRNAs.py -d arch -g genomes.tsv -n /projects/lowelab/users/blin/tRNAviz/process-data/arch/arch-num-041017.cm -o trnas.tsv
```

IMPORTANT: parse-tRNAs.py calls sstofa3 internally. Make sure:
- The modified sstofa3 is in the PATH or working directory
- OR patch parse-tRNAs.py to call ./sstofa3 instead of just sstofa3
- Check how parse-tRNAs.py invokes sstofa3 (subprocess call? system()?) and ensure it finds the modified version

parse-tRNAs.py constructs file paths from dbname:
- data/out/{dbname}-tRNAs.out
- data/ss/{dbname}-tRNAs.ss
- data/iso/{dbname}-tRNAs.iso

These are already in place at the correct relative paths.

### Task 2: Verify trnas.tsv output

After parse-tRNAs.py runs, check that:
- All 7 species produced tRNA entries
- Pyrobaculum tRNAs with non-canonical introns have correct (shorter) mature sequences
- Compare a known Pyrobaculum Leu-CAG tRNA length — should be ~76-78 bp mature, not 85 bp

### Task 3: Load into tRNAviz via add_species

The tRNAviz Django app should have a management command for loading species. Check:
```bash
cd ~/ClaudeCode/tRNAviz
python manage.py --help | grep -i species
# or
python manage.py add_species --help
```

This will load genomes.tsv and trnas.tsv into the Django database.

### Task 4: Verify in tRNAviz

After loading, verify the Pyrobaculum species appear correctly in the tRNAviz web interface, especially:
- Species show up under Archaea > Crenarchaeota > Thermoprotei
- tRNA sequences display correctly
- Non-canonical intron tRNAs have proper mature sequences

## Reference: Taxonomy IDs Used

| Rank | Taxid | Name |
|------|-------|------|
| domain | 2157 | Archaea |
| phylum | 28889 | Crenarchaeota |
| class | 183924 | Thermoprotei |
| order | 2266 | Thermoproteales |
| family | 2267 | Thermoproteaceae |
| genus | 2276 | Pyrobaculum |

| dbname | taxid | species taxid | name |
|--------|-------|---------------|------|
| pyrAer1 | 178306 | 13773 | P. aerophilum str. IM2 |
| pyroArse1 | 340102 | 121277 | P. arsenaticum DSM 13514 |
| pyroCali1 | 410359 | 181486 | P. calidifontis JCM 11548 |
| pyroIsla1 | 384616 | 2277 | P. islandicum DSM 4184 |
| pyroOgun2 | 99007 | 99007 | P. oguniense TE7 |
| pyro1860_1 | 1104324 | 1104324 | P. sp. 1860 (P. ferrireducens) |
| therNeut1 | 444157 | 70771 | T. neutrophilus V24Sta (P. neutrophilum) |
