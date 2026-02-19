import re

taxids = []
dbname = None
taxid = None
dirname = None
for line in open('genome-info-db-euk-20210907'):
  if line == '\n' and taxid not in taxids and taxid is not None and dbname is not None:
    print('{}\t{}\t{}'.format(dirname, dbname, taxid))
    taxids.append(taxid)
    dbname = None
    taxid = None
    dirname = None
  elif line[0:7] == 'Org_abr':
    dirname = line.strip().split()[-1]
  elif line[0:7] == 'DB_name':
    dbname = line.strip().split()[-1]
  elif line[0:6] == 'Tax_ID':
    taxid_line = line.split()
    if len(taxid_line) > 1:
      taxid = taxid_line[1][:-1]
  elif line[0:8] == 'Trna_abr' and dbname is None:
    dbname = line.strip().split()[1].split('-tRNAs')[0]
    
