'''
File: Set.py
Author(s): Alex Burdick, Dean Orenstein
Date: 04/30/2020
Section: 511
E-mail: burdick.alex@tamu.edu, dean27@tamu.edu

Set class: Represents a set in the cache, which contains lines (cache entries)
'''

from CacheEntry import CacheEntry

class Set:
  def __init__(self, associativity, blockSize):
    self.associativity = associativity
    # Use bit is for an LRU replacement policy
    self.use = ""
    for i in range(self.associativity):
      self.use += str(i)
      
    # Count the uses of each line for an LFU replacement policy
    self.timesUsed = [0] * self.associativity
    
    # The lines contained in the set, must add new CacheEntry objects to the array for it to work
    self.lines = []
    for i in range(self.associativity):
      line = CacheEntry("00", blockSize)
      self.lines.append(line)


  # Formatted output of this set
  def printSet(self):
    for i in range(self.associativity):
      self.lines[i].printLine()



