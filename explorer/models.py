from django.db import models


class Taxonomy(models.Model):
  taxid = models.CharField(primary_key = True, max_length = 10)
  assembly = models.CharField(max_length = 100)
  varietas = models.CharField(max_length = 100)
  species = models.CharField(max_length = 100)
  genus = models.CharField(max_length = 50)
  subclass = models.CharField(max_length = 50)
  taxclass = models.CharField('class', db_column = 'class', max_length = 50)
  order = models.CharField(max_length = 50)
  subphylum = models.CharField(max_length = 50)
  phylum = models.CharField(max_length = 50)
  subkingdom = models.CharField(max_length = 50)
  kingdom = models.CharField(max_length = 50)
  domain = models.CharField(max_length = 10)

  def __str__(self):
    return '{} ({})'.format(self.assembly, self.taxid)

# Create your models here.
class tRNA(models.Model):
  seqname = models.CharField(primary_key = True, max_length = 100)
  ISOTYPES = (
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
    ('Und', 'Und'),
    ('Val', 'Val')
  )

  isotype = models.CharField(max_length = 3, choices = ISOTYPES)
  anticodon = models.CharField(max_length = 3)
  score = models.FloatField()
  primary = models.BooleanField()
  best_model = models.CharField(max_length = 3, choices = ISOTYPES)
  isoscore = models.FloatField()
  isoscore_ac = models.FloatField()
  dbname = models.CharField(max_length = 100)
  assembly = models.CharField(max_length = 100)
  varietas = models.CharField(max_length = 100)
  species = models.CharField(max_length = 100)
  genus = models.CharField(max_length = 50)
  subclass = models.CharField(max_length = 50)
  taxclass = models.CharField('class', db_column = 'class', max_length = 50)
  order = models.CharField(max_length = 50)
  subphylum = models.CharField(max_length = 50)
  phylum = models.CharField(max_length = 50)
  subkingdom = models.CharField(max_length = 50)
  kingdom = models.CharField(max_length = 50)
  domain = models.CharField(max_length = 10)
  taxid = models.CharField(max_length = 10)

  stemGC = models.FloatField()
  insertions = models.IntegerField()
  deletions = models.IntegerField()
  dloop = models.IntegerField()
  acloop = models.IntegerField()
  tpcloop = models.IntegerField()
  varm = models.IntegerField()
  intron_length = models.IntegerField()

  p1_72 = models.CharField('1:72', default = '-:-', max_length = 3)
  p1 = models.CharField('1', default = '-', max_length = 1)
  p2_71 = models.CharField('2:71', default = '-:-', max_length = 3)
  p2 = models.CharField('2', default = '-', max_length = 1)
  p3_70 = models.CharField('3:70', default = '-:-', max_length = 3)
  p3 = models.CharField('3', default = '-', max_length = 1)
  p4_69 = models.CharField('4:69', default = '-:-', max_length = 3)
  p4 = models.CharField('4', default = '-', max_length = 1)
  p5_68 = models.CharField('5:68', default = '-:-', max_length = 3)
  p5 = models.CharField('5', default = '-', max_length = 1)
  p6_67 = models.CharField('6:67', default = '-:-', max_length = 3)
  p6 = models.CharField('6', default = '-', max_length = 1)
  p7_66 = models.CharField('7:66', default = '-:-', max_length = 3)
  p7 = models.CharField('7', default = '-', max_length = 1)
  p8 = models.CharField('8', default = '-', max_length = 1)
  p8_14 = models.CharField('8:14', default = '-:-', max_length = 1)
  p9 = models.CharField('9', default = '-', max_length = 1)
  p9_23 = models.CharField('9:23', default = '-:-', max_length = 3)
  p10_25 = models.CharField('10:25', default = '-:-', max_length = 3)
  p10 = models.CharField('10', default = '-', max_length = 1)
  p10_45 = models.CharField('10:45', default = '-:-', max_length = 3)
  p11_24 = models.CharField('11:24', default = '-:-', max_length = 3)
  p11 = models.CharField('11', default = '-', max_length = 1)
  p12_23 = models.CharField('12:23', default = '-:-', max_length = 3)
  p12 = models.CharField('12', default = '-', max_length = 1)
  p13_22 = models.CharField('13:22', default = '-:-', max_length = 3)
  p13 = models.CharField('13', default = '-', max_length = 1)
  p14 = models.CharField('14', default = '-', max_length = 1)
  p15 = models.CharField('15', default = '-', max_length = 1)
  p15_48 = models.CharField('15:48', default = '-:-', max_length = 3)
  p16 = models.CharField('16', default = '-', max_length = 1)
  p17 = models.CharField('17', default = '-', max_length = 1)
  p17a = models.CharField('17a', default = '-', max_length = 1)
  p18 = models.CharField('18', default = '-', max_length = 1)
  p18_55 = models.CharField('18:55', default = '-:-', max_length = 3)
  p19 = models.CharField('19', default = '-', max_length = 1)
  p19_56 = models.CharField('19:56', default = '-:-', max_length = 3)
  p20 = models.CharField('20', default = '-', max_length = 1)
  p20a = models.CharField('20a', default = '-', max_length = 1)
  p20b = models.CharField('20b', default = '-', max_length = 1)
  p21 = models.CharField('21', default = '-', max_length = 1)
  p22 = models.CharField('22', default = '-', max_length = 1)
  p22_46 = models.CharField('22:46', default = '-:-', max_length = 3)
  p23 = models.CharField('23', default = '-', max_length = 1)
  p24 = models.CharField('24', default = '-', max_length = 1)
  p25 = models.CharField('25', default = '-', max_length = 1)
  p26 = models.CharField('26', default = '-', max_length = 1)
  p26_44 = models.CharField('26:44', default = '-:-', max_length = 3)
  p27_43 = models.CharField('27:43', default = '-:-', max_length = 3)
  p27 = models.CharField('27', default = '-', max_length = 1)
  p28_42 = models.CharField('28:42', default = '-:-', max_length = 3)
  p28 = models.CharField('28', default = '-', max_length = 1)
  p29_41 = models.CharField('29:41', default = '-:-', max_length = 3)
  p29 = models.CharField('29', default = '-', max_length = 1)
  p30_40 = models.CharField('30:40', default = '-:-', max_length = 3)
  p30 = models.CharField('30', default = '-', max_length = 1)
  p31_39 = models.CharField('31:39', default = '-:-', max_length = 3)
  p31 = models.CharField('31', default = '-', max_length = 1)
  p32 = models.CharField('32', default = '-', max_length = 1)
  p33 = models.CharField('33', default = '-', max_length = 1)
  p34 = models.CharField('34', default = '-', max_length = 1)
  p35 = models.CharField('35', default = '-', max_length = 1)
  p36 = models.CharField('36', default = '-', max_length = 1)
  p37 = models.CharField('37', default = '-', max_length = 1)
  p38 = models.CharField('38', default = '-', max_length = 1)
  p39 = models.CharField('39', default = '-', max_length = 1)
  p40 = models.CharField('40', default = '-', max_length = 1)
  p41 = models.CharField('41', default = '-', max_length = 1)
  p42 = models.CharField('42', default = '-', max_length = 1)
  p43 = models.CharField('43', default = '-', max_length = 1)
  p44 = models.CharField('44', default = '-', max_length = 1)
  p45 = models.CharField('45', default = '-', max_length = 1)
  pV11_V21 = models.CharField('V11:V21', default = '-:-', max_length = 3)
  pV12_V22 = models.CharField('V12:V22', default = '-:-', max_length = 3)
  pV13_V23 = models.CharField('V13:V23', default = '-:-', max_length = 3)
  pV14_V24 = models.CharField('V14:V24', default = '-:-', max_length = 3)
  pV15_V25 = models.CharField('V15:V25', default = '-:-', max_length = 3)
  pV16_V26 = models.CharField('V16:V26', default = '-:-', max_length = 3)
  pV17_V27 = models.CharField('V17:V27', default = '-:-', max_length = 3)
  pV1 = models.CharField('V1', default = '-', max_length = 1)
  pV2 = models.CharField('V2', default = '-', max_length = 1)
  pV3 = models.CharField('V3', default = '-', max_length = 1)
  pV4 = models.CharField('V4', default = '-', max_length = 1)
  pV5 = models.CharField('V5', default = '-', max_length = 1)
  pV11 = models.CharField('V11', default = '-', max_length = 1)
  pV12 = models.CharField('V12', default = '-', max_length = 1)
  pV13 = models.CharField('V13', default = '-', max_length = 1)
  pV14 = models.CharField('V14', default = '-', max_length = 1)
  pV15 = models.CharField('V15', default = '-', max_length = 1)
  pV16 = models.CharField('V16', default = '-', max_length = 1)
  pV17 = models.CharField('V17', default = '-', max_length = 1)
  pV21 = models.CharField('V21', default = '-', max_length = 1)
  pV22 = models.CharField('V22', default = '-', max_length = 1)
  pV23 = models.CharField('V23', default = '-', max_length = 1)
  pV24 = models.CharField('V24', default = '-', max_length = 1)
  pV25 = models.CharField('V25', default = '-', max_length = 1)
  pV26 = models.CharField('V26', default = '-', max_length = 1)
  pV27 = models.CharField('V27', default = '-', max_length = 1)
  p46 = models.CharField('46', default = '-', max_length = 1)
  p47 = models.CharField('47', default = '-', max_length = 1)
  p48 = models.CharField('48', default = '-', max_length = 1)
  p49_65 = models.CharField('49:65', default = '-:-', max_length = 3)
  p49 = models.CharField('49', default = '-', max_length = 1)
  p50_64 = models.CharField('50:64', default = '-:-', max_length = 3)
  p50 = models.CharField('50', default = '-', max_length = 1)
  p51_63 = models.CharField('51:63', default = '-:-', max_length = 3)
  p51 = models.CharField('51', default = '-', max_length = 1)
  p52_62 = models.CharField('52:62', default = '-:-', max_length = 3)
  p52 = models.CharField('52', default = '-', max_length = 1)
  p53_61 = models.CharField('53:61', default = '-:-', max_length = 3)
  p53 = models.CharField('53', default = '-', max_length = 1)
  p54 = models.CharField('54', default = '-', max_length = 1)
  p54_58 = models.CharField('54:58', default = '-:-', max_length = 3)
  p55 = models.CharField('55', default = '-', max_length = 1)
  p56 = models.CharField('56', default = '-', max_length = 1)
  p57 = models.CharField('57', default = '-', max_length = 1)
  p58 = models.CharField('58', default = '-', max_length = 1)
  p59 = models.CharField('59', default = '-', max_length = 1)
  p60 = models.CharField('60', default = '-', max_length = 1)
  p61 = models.CharField('61', default = '-', max_length = 1)
  p62 = models.CharField('62', default = '-', max_length = 1)
  p63 = models.CharField('63', default = '-', max_length = 1)
  p64 = models.CharField('64', default = '-', max_length = 1)
  p65 = models.CharField('65', default = '-', max_length = 1)
  p66 = models.CharField('66', default = '-', max_length = 1)
  p67 = models.CharField('67', default = '-', max_length = 1)
  p68 = models.CharField('68', default = '-', max_length = 1)
  p69 = models.CharField('69', default = '-', max_length = 1)
  p70 = models.CharField('70', default = '-', max_length = 1)
  p71 = models.CharField('71', default = '-', max_length = 1)
  p72 = models.CharField('72', default = '-', max_length = 1)
  p73 = models.CharField('73', default = '-', max_length = 1)
  p74 = models.CharField('74', default = '-', max_length = 1)
  p75 = models.CharField('75', default = '-', max_length = 1)
  p76 = models.CharField('76', default = '-', max_length = 1)

  def __str__(self):
    return self.seqname

  class Meta:
    verbose_name = 'tRNA'



class Consensus(models.Model):
  consensus = models.CharField(max_length = 20)
  position = models.CharField(max_length = 10)
  isotype = models.CharField(max_length = 3)
  clade = models.CharField(max_length = 50)
  rank = models.CharField(max_length = 20)

  def __str__(self):
    return '{} - {} ({} {})'.format(self.position, self.consensus, self.rank, self.clade)
