from django.db import models
import numpy

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
  ('Val', 'Val')
)

class Taxonomy(models.Model):
  name = models.CharField(max_length = 150)
  rank = models.CharField(max_length = 20)
  taxid = models.CharField(max_length = 10)
  domain = models.CharField(max_length = 20)
  kingdom = models.CharField(max_length = 10, blank = True, null = True)
  subkingdom = models.CharField(max_length = 10, blank = True, null = True)
  phylum = models.CharField(max_length = 10, blank = True, null = True)
  subphylum = models.CharField(max_length = 10, blank = True, null = True)
  taxclass = models.CharField('class', db_column = 'class', max_length = 10, blank = True, null = True)
  subclass = models.CharField(max_length = 10, blank = True, null = True)
  order = models.CharField(max_length = 10, blank = True, null = True)
  family = models.CharField(max_length = 10, blank = True, null = True)
  genus = models.CharField(max_length = 10, blank = True, null = True)
  species = models.CharField(max_length = 10, blank = True, null = True)
  assembly = models.CharField(max_length = 10, blank = True, null = True)

  def __str__(self):
    return '{} ({})'.format(self.name, self.rank)


class tRNA(models.Model):
  seqname = models.CharField(primary_key = True, max_length = 200)
  isotype = models.CharField(max_length = 5, choices = ISOTYPES)
  anticodon = models.CharField(max_length = 3)
  score = models.FloatField()
  primary = models.BooleanField()
  best_model = models.CharField(max_length = 5, choices = ISOTYPES)
  isoscore = models.FloatField()
  isoscore_ac = models.FloatField()
  dbname = models.CharField(max_length = 150)
  domain = models.CharField(max_length = 20)
  kingdom = models.CharField(max_length = 10, blank = True, null = True)
  subkingdom = models.CharField(max_length = 10, blank = True, null = True)
  phylum = models.CharField(max_length = 10, blank = True, null = True)
  subphylum = models.CharField(max_length = 10, blank = True, null = True)
  taxclass = models.CharField('class', db_column = 'class', max_length = 10, blank = True, null = True)
  subclass = models.CharField(max_length = 10, blank = True, null = True)
  order = models.CharField(max_length = 10, blank = True, null = True)
  family = models.CharField(max_length = 10, blank = True, null = True)
  genus = models.CharField(max_length = 10, blank = True, null = True)
  species = models.CharField(max_length = 10, blank = True, null = True)
  assembly = models.CharField(max_length = 10, blank = True, null = True)

  GCcontent = models.FloatField()
  insertions = models.IntegerField()
  deletions = models.IntegerField()
  intron_length = models.IntegerField()
  dloop = models.IntegerField()
  acloop = models.IntegerField()
  tpcloop = models.IntegerField()
  varm = models.IntegerField()

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
  p8_14 = models.CharField('8:14', default = '-:-', max_length = 3)
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
  taxid = models.CharField(max_length = 10)
  isotype = models.CharField(max_length = 5)

  p1_72 = models.CharField('1:72', default = '', max_length = 20, blank = True, null = True)
  p1 = models.CharField('1', default = '', max_length = 20, blank = True, null = True)
  p2_71 = models.CharField('2:71', default = '', max_length = 20, blank = True, null = True)
  p2 = models.CharField('2', default = '', max_length = 20, blank = True, null = True)
  p3_70 = models.CharField('3:70', default = '', max_length = 20, blank = True, null = True)
  p3 = models.CharField('3', default = '', max_length = 20, blank = True, null = True)
  p4_69 = models.CharField('4:69', default = '', max_length = 20, blank = True, null = True)
  p4 = models.CharField('4', default = '', max_length = 20, blank = True, null = True)
  p5_68 = models.CharField('5:68', default = '', max_length = 20, blank = True, null = True)
  p5 = models.CharField('5', default = '', max_length = 20, blank = True, null = True)
  p6_67 = models.CharField('6:67', default = '', max_length = 20, blank = True, null = True)
  p6 = models.CharField('6', default = '', max_length = 20, blank = True, null = True)
  p7_66 = models.CharField('7:66', default = '', max_length = 20, blank = True, null = True)
  p7 = models.CharField('7', default = '', max_length = 20, blank = True, null = True)
  p8 = models.CharField('8', default = '', max_length = 20, blank = True, null = True)
  p8_14 = models.CharField('8:14', default = '', max_length = 20, blank = True, null = True)
  p9 = models.CharField('9', default = '', max_length = 20, blank = True, null = True)
  p9_23 = models.CharField('9:23', default = '', max_length = 20, blank = True, null = True)
  p10_25 = models.CharField('10:25', default = '', max_length = 20, blank = True, null = True)
  p10 = models.CharField('10', default = '', max_length = 20, blank = True, null = True)
  p10_45 = models.CharField('10:45', default = '', max_length = 20, blank = True, null = True)
  p11_24 = models.CharField('11:24', default = '', max_length = 20, blank = True, null = True)
  p11 = models.CharField('11', default = '', max_length = 20, blank = True, null = True)
  p12_23 = models.CharField('12:23', default = '', max_length = 20, blank = True, null = True)
  p12 = models.CharField('12', default = '', max_length = 20, blank = True, null = True)
  p13_22 = models.CharField('13:22', default = '', max_length = 20, blank = True, null = True)
  p13 = models.CharField('13', default = '', max_length = 20, blank = True, null = True)
  p14 = models.CharField('14', default = '', max_length = 20, blank = True, null = True)
  p15 = models.CharField('15', default = '', max_length = 20, blank = True, null = True)
  p15_48 = models.CharField('15:48', default = '', max_length = 20, blank = True, null = True)
  p16 = models.CharField('16', default = '', max_length = 20, blank = True, null = True)
  p17 = models.CharField('17', default = '', max_length = 20, blank = True, null = True)
  p17a = models.CharField('17a', default = '', max_length = 20, blank = True, null = True)
  p18 = models.CharField('18', default = '', max_length = 20, blank = True, null = True)
  p18_55 = models.CharField('18:55', default = '', max_length = 20, blank = True, null = True)
  p19 = models.CharField('19', default = '', max_length = 20, blank = True, null = True)
  p19_56 = models.CharField('19:56', default = '', max_length = 20, blank = True, null = True)
  p20 = models.CharField('20', default = '', max_length = 20, blank = True, null = True)
  p20a = models.CharField('20a', default = '', max_length = 20, blank = True, null = True)
  p20b = models.CharField('20b', default = '', max_length = 20, blank = True, null = True)
  p21 = models.CharField('21', default = '', max_length = 20, blank = True, null = True)
  p22 = models.CharField('22', default = '', max_length = 20, blank = True, null = True)
  p22_46 = models.CharField('22:46', default = '', max_length = 20, blank = True, null = True)
  p23 = models.CharField('23', default = '', max_length = 20, blank = True, null = True)
  p24 = models.CharField('24', default = '', max_length = 20, blank = True, null = True)
  p25 = models.CharField('25', default = '', max_length = 20, blank = True, null = True)
  p26 = models.CharField('26', default = '', max_length = 20, blank = True, null = True)
  p26_44 = models.CharField('26:44', default = '', max_length = 20, blank = True, null = True)
  p27_43 = models.CharField('27:43', default = '', max_length = 20, blank = True, null = True)
  p27 = models.CharField('27', default = '', max_length = 20, blank = True, null = True)
  p28_42 = models.CharField('28:42', default = '', max_length = 20, blank = True, null = True)
  p28 = models.CharField('28', default = '', max_length = 20, blank = True, null = True)
  p29_41 = models.CharField('29:41', default = '', max_length = 20, blank = True, null = True)
  p29 = models.CharField('29', default = '', max_length = 20, blank = True, null = True)
  p30_40 = models.CharField('30:40', default = '', max_length = 20, blank = True, null = True)
  p30 = models.CharField('30', default = '', max_length = 20, blank = True, null = True)
  p31_39 = models.CharField('31:39', default = '', max_length = 20, blank = True, null = True)
  p31 = models.CharField('31', default = '', max_length = 20, blank = True, null = True)
  p32 = models.CharField('32', default = '', max_length = 20, blank = True, null = True)
  p33 = models.CharField('33', default = '', max_length = 20, blank = True, null = True)
  p34 = models.CharField('34', default = '', max_length = 20, blank = True, null = True)
  p35 = models.CharField('35', default = '', max_length = 20, blank = True, null = True)
  p36 = models.CharField('36', default = '', max_length = 20, blank = True, null = True)
  p37 = models.CharField('37', default = '', max_length = 20, blank = True, null = True)
  p38 = models.CharField('38', default = '', max_length = 20, blank = True, null = True)
  p39 = models.CharField('39', default = '', max_length = 20, blank = True, null = True)
  p40 = models.CharField('40', default = '', max_length = 20, blank = True, null = True)
  p41 = models.CharField('41', default = '', max_length = 20, blank = True, null = True)
  p42 = models.CharField('42', default = '', max_length = 20, blank = True, null = True)
  p43 = models.CharField('43', default = '', max_length = 20, blank = True, null = True)
  p44 = models.CharField('44', default = '', max_length = 20, blank = True, null = True)
  p45 = models.CharField('45', default = '', max_length = 20, blank = True, null = True)
  pV11_V21 = models.CharField('V11:V21', default = '', max_length = 20, blank = True, null = True)
  pV12_V22 = models.CharField('V12:V22', default = '', max_length = 20, blank = True, null = True)
  pV13_V23 = models.CharField('V13:V23', default = '', max_length = 20, blank = True, null = True)
  pV14_V24 = models.CharField('V14:V24', default = '', max_length = 20, blank = True, null = True)
  pV15_V25 = models.CharField('V15:V25', default = '', max_length = 20, blank = True, null = True)
  pV16_V26 = models.CharField('V16:V26', default = '', max_length = 20, blank = True, null = True)
  pV17_V27 = models.CharField('V17:V27', default = '', max_length = 20, blank = True, null = True)
  pV1 = models.CharField('V1', default = '', max_length = 20, blank = True, null = True)
  pV2 = models.CharField('V2', default = '', max_length = 20, blank = True, null = True)
  pV3 = models.CharField('V3', default = '', max_length = 20, blank = True, null = True)
  pV4 = models.CharField('V4', default = '', max_length = 20, blank = True, null = True)
  pV5 = models.CharField('V5', default = '', max_length = 20, blank = True, null = True)
  pV11 = models.CharField('V11', default = '', max_length = 20, blank = True, null = True)
  pV12 = models.CharField('V12', default = '', max_length = 20, blank = True, null = True)
  pV13 = models.CharField('V13', default = '', max_length = 20, blank = True, null = True)
  pV14 = models.CharField('V14', default = '', max_length = 20, blank = True, null = True)
  pV15 = models.CharField('V15', default = '', max_length = 20, blank = True, null = True)
  pV16 = models.CharField('V16', default = '', max_length = 20, blank = True, null = True)
  pV17 = models.CharField('V17', default = '', max_length = 20, blank = True, null = True)
  pV21 = models.CharField('V21', default = '', max_length = 20, blank = True, null = True)
  pV22 = models.CharField('V22', default = '', max_length = 20, blank = True, null = True)
  pV23 = models.CharField('V23', default = '', max_length = 20, blank = True, null = True)
  pV24 = models.CharField('V24', default = '', max_length = 20, blank = True, null = True)
  pV25 = models.CharField('V25', default = '', max_length = 20, blank = True, null = True)
  pV26 = models.CharField('V26', default = '', max_length = 20, blank = True, null = True)
  pV27 = models.CharField('V27', default = '', max_length = 20, blank = True, null = True)
  p46 = models.CharField('46', default = '', max_length = 20, blank = True, null = True)
  p47 = models.CharField('47', default = '', max_length = 20, blank = True, null = True)
  p48 = models.CharField('48', default = '', max_length = 20, blank = True, null = True)
  p49_65 = models.CharField('49:65', default = '', max_length = 20, blank = True, null = True)
  p49 = models.CharField('49', default = '', max_length = 20, blank = True, null = True)
  p50_64 = models.CharField('50:64', default = '', max_length = 20, blank = True, null = True)
  p50 = models.CharField('50', default = '', max_length = 20, blank = True, null = True)
  p51_63 = models.CharField('51:63', default = '', max_length = 20, blank = True, null = True)
  p51 = models.CharField('51', default = '', max_length = 20, blank = True, null = True)
  p52_62 = models.CharField('52:62', default = '', max_length = 20, blank = True, null = True)
  p52 = models.CharField('52', default = '', max_length = 20, blank = True, null = True)
  p53_61 = models.CharField('53:61', default = '', max_length = 20, blank = True, null = True)
  p53 = models.CharField('53', default = '', max_length = 20, blank = True, null = True)
  p54 = models.CharField('54', default = '', max_length = 20, blank = True, null = True)
  p54_58 = models.CharField('54:58', default = '', max_length = 20, blank = True, null = True)
  p55 = models.CharField('55', default = '', max_length = 20, blank = True, null = True)
  p56 = models.CharField('56', default = '', max_length = 20, blank = True, null = True)
  p57 = models.CharField('57', default = '', max_length = 20, blank = True, null = True)
  p58 = models.CharField('58', default = '', max_length = 20, blank = True, null = True)
  p59 = models.CharField('59', default = '', max_length = 20, blank = True, null = True)
  p60 = models.CharField('60', default = '', max_length = 20, blank = True, null = True)
  p61 = models.CharField('61', default = '', max_length = 20, blank = True, null = True)
  p62 = models.CharField('62', default = '', max_length = 20, blank = True, null = True)
  p63 = models.CharField('63', default = '', max_length = 20, blank = True, null = True)
  p64 = models.CharField('64', default = '', max_length = 20, blank = True, null = True)
  p65 = models.CharField('65', default = '', max_length = 20, blank = True, null = True)
  p66 = models.CharField('66', default = '', max_length = 20, blank = True, null = True)
  p67 = models.CharField('67', default = '', max_length = 20, blank = True, null = True)
  p68 = models.CharField('68', default = '', max_length = 20, blank = True, null = True)
  p69 = models.CharField('69', default = '', max_length = 20, blank = True, null = True)
  p70 = models.CharField('70', default = '', max_length = 20, blank = True, null = True)
  p71 = models.CharField('71', default = '', max_length = 20, blank = True, null = True)
  p72 = models.CharField('72', default = '', max_length = 20, blank = True, null = True)
  p73 = models.CharField('73', default = '', max_length = 20, blank = True, null = True)
  
  def __str__(self):
    return 'Consensus for {} - {}'.format(self.taxid, self.isotype)


class Freq(models.Model):
  taxid = models.CharField(max_length = 10)
  isotype = models.CharField(max_length = 5)
  position = models.CharField(max_length = 10)
  total = models.IntegerField(default = 0)
  A = models.IntegerField(default = 0)
  C = models.IntegerField(default = 0)
  G = models.IntegerField(default = 0)
  U = models.IntegerField(default = 0)
  absent = models.IntegerField(default = 0, db_column = '-')
  AU = models.IntegerField('A:U', db_column = 'A:U', default = 0)
  UA = models.IntegerField('U:A', db_column = 'U:A', default = 0)
  GC = models.IntegerField('G:C', db_column = 'G:C', default = 0)
  CG = models.IntegerField('C:G', db_column = 'C:G', default = 0)
  GU = models.IntegerField('G:U', db_column = 'G:U', default = 0)
  UG = models.IntegerField('U:G', db_column = 'U:G', default = 0)
  MM = models.IntegerField('-:-', db_column = '-:-', default = 0)
  AA = models.IntegerField('A:A', db_column = 'A:A', default = 0)
  AC = models.IntegerField('A:C', db_column = 'A:C', default = 0)
  AG = models.IntegerField('A:G', db_column = 'A:G', default = 0)
  CA = models.IntegerField('C:A', db_column = 'C:A', default = 0)
  CC = models.IntegerField('C:C', db_column = 'C:C', default = 0)
  CU = models.IntegerField('C:U', db_column = 'C:U', default = 0)
  GA = models.IntegerField('G:A', db_column = 'G:A', default = 0)
  GG = models.IntegerField('G:G', db_column = 'G:G', default = 0)
  UC = models.IntegerField('U:C', db_column = 'U:C', default = 0)
  UU = models.IntegerField('U:U', db_column = 'U:U', default = 0)
  AM = models.IntegerField('A:-', db_column = 'A:-', default = 0)
  MA = models.IntegerField('-:A', db_column = '-:A', default = 0)
  CM = models.IntegerField('C:-', db_column = 'C:-', default = 0)
  MC = models.IntegerField('-:C', db_column = '-:C', default = 0)
  GM = models.IntegerField('G:-', db_column = 'G:-', default = 0)
  MG = models.IntegerField('-:G', db_column = '-:G', default = 0)
  UM = models.IntegerField('U:-', db_column = 'U:-', default = 0)
  MU = models.IntegerField('-:U', db_column = '-:U', default = 0)
  
  def __str__(self):
    return 'Freqs for {} - {}'.format(self.taxid, self.position)

class Coord(models.Model):
  position = models.CharField(primary_key = True, max_length = 5)
  x = models.FloatField()
  y = models.FloatField()
  radius = models.FloatField()

  def __str__(self):
    return '{} - ({}, {})'.format(self.position, self.x, self.y)