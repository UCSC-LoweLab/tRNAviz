import re
import time

from django.core.management.base import BaseCommand
from django.db import connection, transaction


LOAD_ORDER = [
  'explorer_coord',
  'explorer_taxonomy',
  'explorer_trna',
  'explorer_consensus',
  'explorer_freq',
]

# Column type overrides. Unlisted columns are treated as str.
COLUMN_TYPES = {
  'explorer_coord': {
    'x': float, 'y': float, 'radius': float,
  },
  'explorer_taxonomy': {
    'id': int,
  },
  'explorer_trna': {
    'score': float, 'isoscore': float, 'isoscore_ac': float, 'GCcontent': float,
    'insertions': int, 'deletions': int, 'intron_length': int,
    'dloop': int, 'acloop': int, 'tpcloop': int, 'varm': int,
    'primary': bool,
  },
  'explorer_consensus': {
    'id': int,
  },
  'explorer_freq': {
    'id': int, 'total': int,
    'A': int, 'C': int, 'G': int, 'U': int, '-': int,
    'A:U': int, 'U:A': int, 'G:C': int, 'C:G': int, 'G:U': int, 'U:G': int, '-:-': int,
    'A:A': int, 'A:C': int, 'A:G': int, 'C:A': int, 'C:C': int, 'C:U': int,
    'G:A': int, 'G:G': int, 'U:C': int, 'U:U': int,
    'A:-': int, '-:A': int, 'C:-': int, '-:C': int, 'G:-': int, '-:G': int, 'U:-': int, '-:U': int,
  },
}

AUTO_INCREMENT_TABLES = {'explorer_taxonomy', 'explorer_consensus', 'explorer_freq'}

BATCH_SIZE = 10000


class Command(BaseCommand):
  help = 'Load data from a PostgreSQL pg_dump file into the MySQL database'

  def add_arguments(self, parser):
    parser.add_argument('dumpfile', help='Path to the pg_dump SQL file')
    parser.add_argument('--tables', default='',
      help='Comma-separated table names to load (e.g., taxonomy,trna)')
    parser.add_argument('--dry-run', action='store_true',
      help='Parse and count rows without inserting')
    parser.add_argument('--no-clear', action='store_true',
      help='Skip clearing tables before loading')

  def handle(self, *args, **options):
    dumpfile = options['dumpfile']
    dry_run = options['dry_run']
    no_clear = options['no_clear']

    tables_to_load = self._resolve_tables(options['tables'])
    if tables_to_load is None:
      return

    cursor = connection.cursor()

    if not no_clear and not dry_run:
      self._clear_tables(cursor, tables_to_load)

    self.stdout.write('Processing {}...'.format(dumpfile))
    loaded = self._stream_load(cursor, dumpfile, tables_to_load, dry_run)

    if not dry_run:
      self._update_sequences(cursor, loaded)

    self.stdout.write(self.style.SUCCESS('Done.'))

  def _resolve_tables(self, tables_arg):
    if not tables_arg:
      return set(LOAD_ORDER)
    result = set()
    for name in tables_arg.split(','):
      name = name.strip()
      full = 'explorer_{}'.format(name) if not name.startswith('explorer_') else name
      if full not in LOAD_ORDER:
        self.stderr.write(self.style.ERROR('Unknown table: {}'.format(name)))
        return None
      result.add(full)
    return result

  def _clear_tables(self, cursor, tables):
    for table in reversed(LOAD_ORDER):
      if table in tables:
        self.stdout.write('Clearing {}...'.format(table))
        cursor.execute('TRUNCATE TABLE `{}`'.format(table))
        self.stdout.write('  Truncated {}'.format(table))

  def _stream_load(self, cursor, dumpfile, tables, dry_run):
    loaded = set()
    copy_re = re.compile(r'^COPY public\.(explorer_\w+) \((.+)\) FROM stdin;$')

    with open(dumpfile, 'r', encoding='utf-8') as f:
      for line in f:
        match = copy_re.match(line.rstrip('\r\n'))
        if not match:
          continue

        table_name = match.group(1)
        if table_name not in tables:
          for data_line in f:
            if data_line.rstrip('\r\n') == '\\.':
              break
          continue

        columns = [c.strip().strip('"') for c in match.group(2).split(',')]
        types = COLUMN_TYPES.get(table_name, {})

        quoted_cols = ', '.join('`{}`'.format(c) for c in columns)
        placeholders = ', '.join(['%s'] * len(columns))
        insert_sql = 'INSERT INTO `{}` ({}) VALUES ({})'.format(table_name, quoted_cols, placeholders)

        self.stdout.write('Loading {} ({} columns)...'.format(table_name, len(columns)))
        start = time.time()
        row_count = 0
        batch = []

        with transaction.atomic():
          for data_line in f:
            stripped = data_line.rstrip('\r\n')
            if stripped == '\\.':
              break

            values = stripped.split('\t')
            row = []
            for col, val in zip(columns, values):
              if val == '\\N':
                row.append(None)
              elif col in types:
                t = types[col]
                if t is bool:
                  row.append(1 if val == 't' else 0)
                elif t is int:
                  row.append(int(val))
                else:
                  row.append(float(val))
              else:
                row.append(val)
            batch.append(row)
            row_count += 1

            if len(batch) >= BATCH_SIZE:
              if not dry_run:
                cursor.executemany(insert_sql, batch)
              batch = []
              if row_count % 500000 == 0:
                elapsed = time.time() - start
                self.stdout.write('  {:,} rows ({:.1f}s)'.format(row_count, elapsed))

          if batch and not dry_run:
            cursor.executemany(insert_sql, batch)

        elapsed = time.time() - start
        self.stdout.write(self.style.SUCCESS(
          '  {}: {:,} rows in {:.1f}s'.format(table_name, row_count, elapsed)
        ))
        loaded.add(table_name)

    return loaded

  def _update_sequences(self, cursor, loaded):
    for table in AUTO_INCREMENT_TABLES & loaded:
      cursor.execute('SELECT MAX(id) FROM `{}`'.format(table))
      max_id = cursor.fetchone()[0]
      if max_id is not None:
        cursor.execute(
          'ALTER TABLE `{}` AUTO_INCREMENT = %s'.format(table),
          [max_id + 1]
        )
        self.stdout.write('Updated auto_increment for {} to {}'.format(table, max_id + 1))
