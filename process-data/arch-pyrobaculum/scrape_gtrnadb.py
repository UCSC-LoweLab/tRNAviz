#!/usr/bin/env python3
"""Scrape GtRNAdb hand-checked alignments for Pyrobaculum species.

Fetches alignment pages, parses sequences (with lowercase introns),
strips lowercase (introns) and dots (alignment gaps) to produce mature
tRNA FASTA files. Maps GtRNAdb tRNA names back to tRNAscan-SE IDs from
.out files.

Output: data/tRNAs/{dbname}-tRNAs.fa for each species
"""

import os
import re
import sys
import time
import urllib.request

SPECIES = [
    {'dbname': 'pyrAer1',    'gtrnadb_dir': 'Pyro_aero_IM2'},
    {'dbname': 'pyroArse1',  'gtrnadb_dir': 'Pyro_arse_DSM_13514'},
    {'dbname': 'pyroCali1',  'gtrnadb_dir': 'Pyro_cali_JCM_11548'},
    {'dbname': 'pyroIsla1',  'gtrnadb_dir': 'Pyro_isla_DSM_4184'},
    {'dbname': 'pyroOgun2',  'gtrnadb_dir': 'Pyro_ogun_TE7'},
    {'dbname': 'pyro1860_1', 'gtrnadb_dir': 'Pyro_1860'},
    {'dbname': 'therNeut1',  'gtrnadb_dir': 'Pyro_neut_V24Sta'},
]


def fetch_alignment_html(gtrnadb_dir):
    """Fetch alignment HTML from GtRNAdb."""
    url = f'https://gtrnadb.org/genomes/archaea/{gtrnadb_dir}/{gtrnadb_dir}-align.html'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=30)
    return resp.read().decode()


def parse_gtrnadb_alignment(html):
    """Parse alignment HTML to extract tRNA names and sequences.

    Returns list of dicts with keys: name, isotype, anticodon, copy, gene,
    score, aligned_seq, mature_seq
    """
    trnas = []
    for line in html.split('\n'):
        m = re.search(r'(tRNA-(\w+)-(\w+)-(\d+)-(\d+))\s+Sc:\s+([\d.]+)', line)
        if not m:
            continue
        name = m.group(1)
        isotype = m.group(2)
        anticodon = m.group(3)
        copy_num = int(m.group(4))
        gene_num = int(m.group(5))
        score = float(m.group(6))

        # Strip HTML tags to get raw text
        text = re.sub(r'<[^>]+>', '', line).strip()
        # Sequence is everything before the tRNA name
        seq_part = text[:text.index(name)].strip()

        # Mature sequence: strip dots (gaps) and lowercase (introns)
        mature = re.sub(r'[a-z.]', '', seq_part)

        trnas.append({
            'name': name,
            'isotype': isotype,
            'anticodon': anticodon,
            'copy': copy_num,
            'gene': gene_num,
            'score': score,
            'aligned_seq': seq_part,
            'mature_seq': mature,
        })
    return trnas


def parse_out_file(out_path):
    """Parse .out file to get approved tRNAs with their tRNAscan-SE IDs.

    Returns list of dicts with keys: seqname, trna_number, isotype, anticodon,
    start, end, score, note, intron_start, intron_end
    """
    trnas = []
    with open(out_path) as f:
        for i, line in enumerate(f):
            if i < 3:  # skip header
                continue
            parts = line.strip().split('\t')
            if len(parts) < 14:
                continue
            seqname = parts[0].strip()
            trna_number = int(parts[1].strip())
            start = int(parts[2].strip())
            end = int(parts[3].strip())
            isotype = parts[4].strip()
            anticodon = parts[5].strip()
            intron_start = parts[6].strip()
            intron_end = parts[7].strip()
            score = float(parts[8].strip())
            note = parts[-1].strip() if len(parts) > 14 else ''

            # Build tRNAscan-SE ID
            tscan_id = f'{seqname}.trna{trna_number}-{isotype}{anticodon}'

            trnas.append({
                'tscan_id': tscan_id,
                'seqname': seqname,
                'trna_number': trna_number,
                'isotype': isotype,
                'anticodon': anticodon,
                'start': start,
                'end': end,
                'score': score,
                'note': note,
                'intron_start': intron_start,
                'intron_end': intron_end,
            })
    return trnas


def parse_ss_seqs(ss_path):
    """Parse .ss file to get Seq: lines for each tRNA (for matching)."""
    seqs = {}
    current_trna = None
    with open(ss_path) as f:
        for line in f:
            m = re.match(r'(\S+\.trna\d+)\s+\(', line)
            if m:
                current_trna = m.group(1)
            elif line.startswith('Seq:') and current_trna:
                seq = line.split(':', 1)[1].strip()
                seqs[current_trna] = seq.upper()  # uppercase for comparison
    return seqs


def match_gtrnadb_to_tscan(gtrnadb_trnas, out_trnas, ss_seqs):
    """Match GtRNAdb tRNAs to tRNAscan-SE IDs.

    Strategy: group both by (isotype, anticodon). For single matches, map
    directly. For duplicates, compare mature sequences.
    """
    # Normalize isotype names: iMet->iMet, Ile2->Ile2 (GtRNAdb uses these)
    # GtRNAdb uses Sup for suppressor tRNAs

    # Group GtRNAdb entries by (isotype, anticodon)
    gtrnadb_groups = {}
    for t in gtrnadb_trnas:
        key = (t['isotype'], t['anticodon'])
        gtrnadb_groups.setdefault(key, []).append(t)

    # Group .out entries by (isotype, anticodon), preserving genomic order
    out_groups = {}
    for t in out_trnas:
        key = (t['isotype'], t['anticodon'])
        out_groups.setdefault(key, []).append(t)

    matches = []
    unmatched_gtrnadb = []

    for key, gtrnadb_list in gtrnadb_groups.items():
        out_list = out_groups.get(key, [])

        if len(gtrnadb_list) == 1 and len(out_list) == 1:
            # Simple 1:1 match
            matches.append((gtrnadb_list[0], out_list[0]))
        elif len(gtrnadb_list) == len(out_list):
            # Same count - match by sequence similarity
            remaining_out = list(out_list)
            for gt in gtrnadb_list:
                best_match = None
                best_score = -1
                for ot in remaining_out:
                    # Compare mature seq to .ss Seq (uppercased)
                    trnascan_base_id = f'{ot["seqname"]}.trna{ot["trna_number"]}'
                    ss_seq = ss_seqs.get(trnascan_base_id, '')
                    # Simple match score: count matching chars
                    score = sum(a == b for a, b in zip(gt['mature_seq'], ss_seq))
                    if score > best_score:
                        best_score = score
                        best_match = ot
                if best_match:
                    matches.append((gt, best_match))
                    remaining_out.remove(best_match)
        elif len(out_list) == 0:
            # No matching tRNAs in .out (could be filtered/pseudo)
            for gt in gtrnadb_list:
                unmatched_gtrnadb.append(gt)
        else:
            # Different counts - match what we can by sequence
            remaining_out = list(out_list)
            for gt in gtrnadb_list:
                best_match = None
                best_score = -1
                for ot in remaining_out:
                    trnascan_base_id = f'{ot["seqname"]}.trna{ot["trna_number"]}'
                    ss_seq = ss_seqs.get(trnascan_base_id, '')
                    score = sum(a == b for a, b in zip(gt['mature_seq'], ss_seq))
                    if score > best_score:
                        best_score = score
                        best_match = ot
                if best_match and best_score > len(gt['mature_seq']) * 0.5:
                    matches.append((gt, best_match))
                    remaining_out.remove(best_match)
                else:
                    unmatched_gtrnadb.append(gt)

    return matches, unmatched_gtrnadb


def write_fasta(matches, out_path):
    """Write matched tRNAs as FASTA with sstofa3-compatible headers.

    Header format: >chr.trnaN-IsotypeAnticodon (start-end) Isotype (Anticodon) len bp Sc: score
    """
    with open(out_path, 'w') as f:
        for gt, ot in matches:
            seq = gt['mature_seq']
            length = len(seq)
            coord = f'{ot["start"]}-{ot["end"]}'
            header = (f'{ot["tscan_id"]} ({coord}) '
                      f'{ot["isotype"]} ({ot["anticodon"]}) '
                      f'{length} bp Sc: {ot["score"]}')
            f.write(f'>{header}\n')
            f.write(f'{seq}\n')


def main():
    for sp in SPECIES:
        dbname = sp['dbname']
        gdir = sp['gtrnadb_dir']
        print(f'Processing {dbname} ({gdir})...', file=sys.stderr, end='', flush=True)

        # Fetch GtRNAdb alignment
        html = fetch_alignment_html(gdir)
        gtrnadb_trnas = parse_gtrnadb_alignment(html)
        print(f' {len(gtrnadb_trnas)} GtRNAdb tRNAs', file=sys.stderr, end='', flush=True)

        # Parse .out and .ss files
        out_path = f'data/out/{dbname}-tRNAs.out'
        ss_path = f'data/ss/{dbname}-tRNAs.ss'
        out_trnas = parse_out_file(out_path)
        ss_seqs = parse_ss_seqs(ss_path)
        print(f', {len(out_trnas)} .out entries', file=sys.stderr, end='', flush=True)

        # Match
        matches, unmatched = match_gtrnadb_to_tscan(gtrnadb_trnas, out_trnas, ss_seqs)
        print(f', {len(matches)} matched', file=sys.stderr, end='', flush=True)
        if unmatched:
            print(f', {len(unmatched)} unmatched GtRNAdb', file=sys.stderr, end='', flush=True)

        # Write FASTA
        out_fasta = f'data/tRNAs/{dbname}-tRNAs.fa'
        write_fasta(matches, out_fasta)
        print(f' -> {out_fasta}', file=sys.stderr, flush=True)

        # Be polite to the server
        time.sleep(1)

    print('Done!', file=sys.stderr)


if __name__ == '__main__':
    main()
