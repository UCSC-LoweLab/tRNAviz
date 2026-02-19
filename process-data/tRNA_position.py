import re

class Position:
  def __init__(self, position, sprinzl, index=-1, paired=False):
    self.position = position
    self.sprinzl = sprinzl
    self.index = index
    self.paired = paired
  
  def __str__(self):
    return "Position {} (Sprinzl: {})".format(self.position, self.sprinzl)

class Region:
  def __init__(self, lower, upper, name):
    self.lower = lower
    self.upper = upper
    self.name = name
  
  def __str__(self):
    return "Region {} ({} ~ {})".format(self.name, self.lower, self.upper)

def annotate_positions(ss):
  loop_indices = []
  # We want to be able to track stem-loop insertions, but the regular expression will also pick up "interregion" stretches
  # so, we need to remove "interregion" stretches
  for i, indices in enumerate([r.span() for r in re.finditer('([\(\.]+\()|(<[<\.]+<)|[_\.]+|>[>\.]+>|\)[\)\.]+', ss)]):
    left, right = indices
    if re.search('[\(<_>\)]', ss[left:right]): loop_indices.append(indices)
  regions = ['acceptor', 'dstem', 'dloop', 'dstem', 'acstem', 'acloop', 'acstem', 'vstem', 'vloop', 'vstem', 'tpcstem', 'tpcloop', 'tpcstem', 'acceptor']
  regions = [Region(indices[0], indices[1], name) for indices, name in zip(loop_indices, regions[:])]
  region = regions[0]
  positions = []
  region_index = 0 # index to be used to iterate through regions list
  region_numbering = 0 # base numbering within a region
  insert_index = 0 # tracks base insertions
  sprinzl_positions = ['1:72', '2:71', '3:70', '4:69', '5:68', '6:67', '7:66', '8', '9', '10:25', '11:24', '12:23', '13:22', '14', '15', '16', '17', '17a', '18', '19', '20', '20a', '20b', '21', '22:13', '23:12', '24:11', '25:10', '26', '27:43', '28:42', '29:41', '30:40', '31:39', '32', '33', '34', '35', '36', '37', '38', '39:31', '40:30', '41:29', '42:28', '43:27', '44', '45', 'V11:V21', 'V12:V22', 'V13:V23', 'V14:V24', 'V15:V25', 'V16:V26', 'V17:V27', 'V1', 'V2', 'V3', 'V4', 'V5', 'V27:V17', 'V26:V16', 'V25:V15', 'V24:V14', 'V23:V13', 'V22:V12', 'V21:V11', '46', '47', '48', '49:65', '50:64', '51:63', '52:62', '53:61', '54', '55', '56', '57', '58', '59', '60', '61:53', '62:52', '63:51', '64:50', '65:49', '66:7', '67:6', '68:5', '69:4', '70:3', '71:2', '72:1', '73', '74', '75', '76']
  sprinzl_index = 0
  sprinzl_insert_index = 0 # number of consecutive inserts at a sprinzl position
  reverse_bp_index = 1 # number of bases to backtrack when trying to match a base
  for position in range(len(ss)):
    if region_index < len(regions):
      region = regions[region_index]
    if ss[position] == '.':
      insert_index += 1
      sprinzl_insert_index += 1
      sprinzl = '{}i{}'.format(sprinzl_positions[sprinzl_index - 1].split(':')[0], sprinzl_insert_index)
      positions.append(Position(position=str(position + 1), sprinzl=sprinzl, index=len(positions), paired=False))
    else:
      if position < region.lower: # before the next region starts (or if it's the last region), annotate as single bases
        positions.append(Position(position=str(position + 1), sprinzl=sprinzl_positions[sprinzl_index], index=len(positions), paired=False))
      elif position == region.lower: # start of region: begin region numbering at 1
        insert_index = 0
        if ss[position] == "(":
          while ss[regions[-1].upper - reverse_bp_index] == ".": reverse_bp_index += 1
          paired_base = regions[-1].upper - reverse_bp_index
          positions.append(Position(position='{}:{}'.format(position + 1, paired_base + 1), sprinzl=sprinzl_positions[sprinzl_index], index=len(positions), paired=True))
          region_numbering += 1
        elif ss[position] == "<":
          while ss[regions[region_index + 2].upper - reverse_bp_index] == '.': reverse_bp_index += 1
          paired_base = regions[region_index + 2].upper - reverse_bp_index
          positions.append(Position(position='{}:{}'.format(position + 1, paired_base + 1), sprinzl=sprinzl_positions[sprinzl_index], index=len(positions), paired=True))
          region_numbering += 1
        elif ss[position] in [')', '>']:
          pass
        else:
          positions.append(Position(position=str(position + 1), sprinzl=sprinzl_positions[sprinzl_index], index=len(positions), paired=False))
      elif position > region.lower and position <= region.upper - 1: # inside region: increment region numbering normally
        # find paired base, or skip if base is the opposite strand
        if ss[position] == "(":
          while ss[regions[-1].upper - region_numbering - reverse_bp_index] == ".": reverse_bp_index += 1
          paired_base = regions[-1].upper - region_numbering - reverse_bp_index
          positions.append(Position(position='{}:{}'.format(position + 1, paired_base + 1), sprinzl=sprinzl_positions[sprinzl_index], index=len(positions), paired=True))
          region_numbering += 1
        elif ss[position] == "<":
          while ss[regions[region_index + 2].upper - region_numbering - reverse_bp_index] == ".": reverse_bp_index += 1
          paired_base = regions[region_index + 2].upper - region_numbering - reverse_bp_index
          positions.append(Position(position='{}:{}'.format(position + 1, paired_base + 1), sprinzl=sprinzl_positions[sprinzl_index], index=len(positions), paired=True))
          region_numbering += 1
        elif ss[position] in [')', '>']:
          pass
        else:
          positions.append(Position(position=str(position + 1), sprinzl=sprinzl_positions[sprinzl_index], index=len(positions), paired=False))
      else: # last few bases should be '::::', no inserts here
        positions.append(Position(position=position + 1, sprinzl=sprinzl_positions[sprinzl_index], index=len(positions), paired=False))
      sprinzl_index += 1
      sprinzl_insert_index = 0
    if position == region.upper - 1: # end of region, reset region index and increment region number
      region_index += 1
      reverse_bp_index = 1
      region_numbering = 0
      insert_index = 0
  return positions


def get_position_base_from_seq(positions, seq):
  for position_index, position in enumerate(positions):
    if position.paired:
      index1, index2 = position.position.split(':')
      index1, index2 = int(index1), int(index2)
      base_pair = "{}:{}".format(seq[index1 - 1].upper(), seq[index2 - 1].upper())
      yield position.sprinzl, base_pair
    else:
      index = int(position.position)
      base = seq[index - 1].upper()
      yield position.sprinzl, base