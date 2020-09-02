'''
File: CacheEntry.py
Author(s): Alex Burdick, Dean Orenstein
Date: 04/30/2020
Section: 511
E-mail: burdick.alex@tamu.edu, dean27@tamu.edu

CacheEntry class: represents a cache line, which has a valid bit, dirty bit,
tag, and a computed amount of data blocks
'''

class CacheEntry:
  def __init__(self, tag, blockSize):
    self.valid = 0
    self.dirty = 0
    self.tag = tag
    self.blocks = ["00"] * blockSize


  # Formatted output of this cache line
  def printLine(self):
    print(str(self.valid) + " " + str(self.dirty) + " " + self.tag, end=" ")
    for i in range(len(self.blocks)):
      print(self.blocks[i], end=" ")
    print()
  

  # Return line's byte at offset
  def readByte(self, offset):
    return self.blocks[offset]


  # Set the line's byte at offset
  def setByte(self, offset, newByte):
    self.blocks[offset] = newByte

