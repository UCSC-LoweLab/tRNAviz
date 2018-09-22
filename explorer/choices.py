from . import models

CLADES = tuple([(clade.taxid, '{} ({})'.format(clade.name, clade.rank)) for clade in models.Taxonomy.objects.order_by('name')])

ISOTYPES = (
  ('All', 'All isotypes'),
  ('Ala', 'Ala'),
  ('Arg', 'Arg'),
  ('Asn', 'Asn'),
  ('Asp', 'Asp'),
  ('Cys', 'Cys'),
  ('Gln', 'Gln'),
  ('Glu', 'Glu'),
  ('Gly', 'Gly'),
  ('His', 'His'),
  ('Ile', 'Ile'),
  ('iMet', 'iMet'),
  ('Leu', 'Leu'),
  ('Lys', 'Lys'),
  ('Met', 'Met'),
  ('Phe', 'Phe'),
  ('Pro', 'Pro'),
  ('Ser', 'Ser'),
  ('SeC', 'SeC'),
  ('Thr', 'Thr'),
  ('Trp', 'Trp'),
  ('Tyr', 'Tyr'),
  ('Val', 'Val'),
)

SINGLE_POSITIONS = (
  ('single', 'Single positions'),
  ('8', '8'),
  ('9', '9'),
  ('14', '14'),
  ('15', '15'),
  ('16', '16'),
  ('17', '17'),
  ('17a', '17a'),
  ('18', '18'),
  ('19', '19'),
  ('20', '20'),
  ('20a', '20a'),
  ('20b', '20b'),
  ('21', '21'),
  ('26', '26'),
  ('32', '32'),
  ('33', '33'),
  ('34', '34'),
  ('35', '35'),
  ('36', '36'),
  ('37', '37'),
  ('38', '38'),
  ('44', '44'),
  ('45', '45'),
  ('46', '46'),
  ('47', '47'),
  ('48', '48'),
  ('54', '54'),
  ('55', '55'),
  ('56', '56'),
  ('57', '57'),
  ('58', '58'),
  ('59', '59'),
  ('60', '60'),
  ('73', '73'),
)

PAIRED_POSITIONS = (
  ('paired', 'Paired positions'),
  ('1:72', '1:72'),
  ('2:71', '2:71'),
  ('3:70', '3:70'),
  ('4:69', '4:69'),
  ('5:68', '5:68'),
  ('6:67', '6:67'),
  ('7:66', '7:66'),
  ('10:25', '10:25'),
  ('11:24', '11:24'),
  ('12:23', '12:23'),
  ('13:22', '13:22'),
  ('27:43', '27:43'),
  ('28:42', '28:42'),
  ('29:41', '29:41'),
  ('30:40', '30:40'),
  ('31:39', '31:39'),
  ('49:65', '49:65'),
  ('50:64', '50:64'),
  ('51:63', '51:63'),
  ('52:62', '52:62'),
  ('53:61', '53:61'),
)

VARIABLE_ARM = (
  ('variable', 'Variable arm'),
  ('V1', 'V1'),
  ('V2', 'V2'),
  ('V3', 'V3'),
  ('V4', 'V4'),
  ('V5', 'V5'),
  ('V11:V21', 'V11:V21'),
  ('V12:V22', 'V12:V22'),
  ('V13:V23', 'V13:V23'),
  ('V14:V24', 'V14:V24'),
  ('V15:V25', 'V15:V25'),
  ('V16:V26', 'V16:V26'),
  ('V17:V27', 'V17:V27'),
)

TERTIARY_INTERACTIONS = (
  ('tertiary', 'Tertiary interactions'),
  ('8:14', '8:14'),
  ('9:23', '9:23'),
  ('10:45', '10:45'),
  ('15:48', '15:48'),
  ('18:55', '18:55'),
  ('19:56', '19:56'),
  ('22:46', '22:46'),
  ('26:44', '26:44'),
  ('54:58', '54:58'),
)

POSITIONS = SINGLE_POSITIONS + PAIRED_POSITIONS + VARIABLE_ARM + TERTIARY_INTERACTIONS

ISOTYPES_DISTINCT = (('', ''), ) + ISOTYPES[1:]
POSITIONS_DISTINCT = (('', ''), ) + SINGLE_POSITIONS[1:] + PAIRED_POSITIONS[1:] + VARIABLE_ARM[1:] + TERTIARY_INTERACTIONS[1:]

NUM_MODELS = (
  ('uni', 'Universal'),
  ('euk', 'Eukaryota'),
  ('bact', 'Bacteria'),
  ('arch', 'Archaea')
)