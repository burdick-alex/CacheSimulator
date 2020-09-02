'''
File: Cache.py
Author(s): Alex Burdick, Dean Orenstein
Date: 04/30/2020
Section: 511
E-mail: burdick.alex@tamu.edu, dean27@tamu.edu

Cache class: represents the cache to be simulated, which reads from (and writes to)
its own RAM and contains a computed amount of sets
'''

from Set import Set
from CacheEntry import CacheEntry
from MainMemory import MainMemory
from math import log2
from random import randint

class Cache:
    def __init__(self, ram, C, B, E, replacementPolicy, writeHitPolicy, writeMissPolicy):
        # Cache has its own main memory to interact with
        self.ram = ram

        # C, B, E, and S
        self.cacheSize = int(C)
        self.blockSize = int(B)
        self.associativity = int(E)
        self.numSets = int(self.cacheSize / (self.blockSize * self.associativity))

        # b, s, and t
        self.numBlockOffsetBits = int(log2(self.blockSize))
        self.numSetIndexBits = int(log2(self.numSets))
        self.numTagBits = 8 - (self.numBlockOffsetBits + self.numSetIndexBits)

        # Create the sets for the cache
        self.sets = []
        for i in range(self.numSets):
          blankSet = Set(self.associativity, self.blockSize)
          self.sets.append(blankSet)
        
        # Number of cache hits and cache misses
        self.numHits = 0
        self.numMisses = 0

        # Converting policies to their string equivalents
        if int(replacementPolicy) == 1:
          self.replacementPolicy = "random_replacement"
        elif int(replacementPolicy) == 2:
          self.replacementPolicy = "least_recently_used"
        else:
          self.replacementPolicy = "least_frequently_used"
        if int(writeHitPolicy) == 1:
          self.writeHitPolicy = "write_through"
        else:
          self.writeHitPolicy = "write_back"
        if int(writeMissPolicy) == 1:
          self.writeMissPolicy = "write_allocate"
        else:
          self.writeMissPolicy = "no_write_allocate"


    # Read data from an address
    def cacheRead(self, address):
        # Convert the hex address to binary equivalent
        tag, index, offset = self.hexToBinaryString(address[2:])
        # Convert the tag to hex
        if len(tag) / 4 != 0:
          finalLength = int(len(tag) / 4) * 4
          tag = tag.zfill(finalLength + 4)
        tag = self.fourBitsToHex(tag).upper()     

        if offset == "":
          offset = 0
        else:
          offset = int(offset, 2)

        # Set selection: Take the set index bits from the address and navigate to that set
        # If we have a fully-associative cache (1 set), this is trivial
        if index == "":
          index = 0
        else:
          index = int(index, 2)
        theSet = self.sets[index]

        # For formatting and correct checking
        if len(tag) < 2:
          tag = tag.zfill(2)

        # Other variables
        isMiss = True
        data = ""
        doReplacement = True
        hitMessage = "hit:"
        evictionLineNumber = -1
        addressMessage = "ram_address:"
        
        # Line matching: a hit occurs if the valid bit of a line is set and the tag bits match
        for i in range(self.associativity):
          if theSet.lines[i].valid == 1:
            if tag == theSet.lines[i].tag:
              # Hit! Update everything we need to update
              self.numHits += 1
              hitMessage += "yes"
              addressMessage += "-1"
              data = theSet.lines[i].blocks[offset]
              theSet.timesUsed[i] += 1
              isMiss = False
              doReplacement = False
              break

        # If we have a miss, check if there is a line with valid set to 0 (only in the set)
        if isMiss:
          self.numMisses += 1
          hitMessage += "no"
          addressMessage += address

          for i in range(self.associativity):
            if theSet.lines[i].valid == 0:
              theLine = theSet.lines[i]

              # Set the content of the blockSize contiguous bytes from memory to the line's blocks
              theLine.blocks = self.ram.getBlocks(address, self.blockSize, offset)
              # Valid bit is now set
              theLine.valid = 1
              # Update tag
              theLine.tag = tag

              # The data block is indicated by the offset
              data = theLine.blocks[offset]

              doReplacement = False
              evictionLineNumber = str(i)

              # If we are using an LRU policy, update recentness of the line by removing it from the "use" string of the current set, and then appending it to the end
              if self.replacementPolicy == "least_recently_used" or self.replacementPolicy == "least_frequently_used":
                lineNumber = str(i)
                theSet.use = theSet.use.replace(lineNumber, "")
                theSet.use += lineNumber
              
              # If using an LFU policy, also update the frequency counter at index i of "timesUsed"
              if self.replacementPolicy == "least_frequently_used":
                theSet.timesUsed[i] = 0

              break

          # If we get here, all the lines are valid, perform a replacement using the policy
          if doReplacement:

            # Random replacement: choose a random line in the set to evict and replace with the content starting at address
            if self.replacementPolicy == "random_replacement":
              evictionLineNumber = randint(0,self.associativity-1)
              theSet.use = theSet.use.replace(str(evictionLineNumber),"") + str(evictionLineNumber)

            # Least recently used replacement: choose the last updated line in the set to evict
            elif self.replacementPolicy == "least_recently_used":
              # Evicted line is oldest line (first char in "use" for current set, move it to the end of "use")
              evictionLineNumber = theSet.use[0]
              theSet.use = theSet.use.replace(str(evictionLineNumber),"") + str(evictionLineNumber)

            # Least frequently used replacement: choose the least frequently updated line to evict
            else:
              leastTimesUsed = min(theSet.timesUsed)
              for i in range(len(theSet.timesUsed)):
                if(theSet.timesUsed[i] == leastTimesUsed):
                  evictionLineNumber = i
                  break
              theSet.use = theSet.use.replace(str(evictionLineNumber),"") + str(evictionLineNumber)
            
            # Now that eviction line is indicated and any frequency/recentness is updated, we can do the replacement
            theLine = theSet.lines[int(evictionLineNumber)]
            theLine.blocks = self.ram.getBlocks(address, self.blockSize, offset)
            theLine.tag = tag
            data = theLine.blocks[offset]

        # Print the information from the read
        print("set:" + str(index))
        print("tag:", end="")
        # Ensure correct tag output (dont include any leading 0)
        if tag[0] == "0" and len(tag) > 1:
          print(tag[1])
        else:
          print(tag)
        print(hitMessage)
        print("eviction_line:" + str(evictionLineNumber))
        print(addressMessage)
        print("data:0x" + data)


    # Write data to an address in cache (and RAM if write-through hit policy)
    def cacheWrite(self, address, data, evictionLineNumber, hadAMiss):
        # Set-up is the same as cache read: extract the tag, index, and offset bits, set selection, set variables
        if len(data) > 2:
          data = data[:2] + data[2:].upper()

        tag, index, offset = self.hexToBinaryString(address[2:])
        if len(tag) / 4 != 0:
          finalLength = int(len(tag) / 4) * 4
          tag = tag.zfill(finalLength + 4)
        tag = self.fourBitsToHex(tag).upper()

        if offset == "":
          offset = 0
        else:
          offset = int(offset, 2)

        if index == "":
          index = 0
        else:
          index = int(index, 2)
        theSet = self.sets[index]

        if len(tag) < 2:
          tag = tag.zfill(2)

        isMiss = True
        doReplacement = True
        hitMessage = "write_hit:"
        addressMessage = "ram_address:"
        
        # Line matching happens before writing
        for i in range(self.associativity):
          if theSet.lines[i].valid == 1:
            if tag == theSet.lines[i].tag:

              # If its had a miss (write-allocate miss policy), output address and "no" for hit
              if hadAMiss:
                addressMessage += address
                hitMessage += "no"
              else:
                addressMessage += "-1"
                hitMessage += "yes"
                self.numHits += 1
              
              theSet.timesUsed[i] += 1
              isMiss = False
              doReplacement = False

              # Write-through hit policy: Write the data to cache and ram
              if self.writeHitPolicy == "write_through":
                theLine = theSet.lines[i]
                theLine.setByte(offset, data[2:])
                self.ram.setBlocks(address, theLine.blocks, offset)

              # Write-back hit policy: Write the data ONLY to ram
              else:
                theLine = theSet.lines[i]
                theLine.setByte(offset, data[2:])
                theLine.dirty = 1
              
              # Print the info here if write-allocate miss policy, since its in the base case for its recursive calls
              if self.writeMissPolicy == "write_allocate":
                print("set:" + str(index))
                print("tag:", end="")
                if tag[0] == "0":
                  print(tag[1])
                else:
                  print(tag)
                print(hitMessage)
                print("eviction_line:" + str(evictionLineNumber))
                print(addressMessage)
                print("data:0x" + data[2:])
                print("dirty_bit:" + str(theSet.lines[int(evictionLineNumber)].dirty))

              break
        
        # A cache read miss means use the write miss policy
        if isMiss:
          self.numMisses += 1
          hitMessage += "no"
          
          # No-write allocate miss policy: simply write the data to ram
          if self.writeMissPolicy == "no_write_allocate":
            blockToChange = self.ram.getBlocks(address, self.blockSize, offset)
            blockToChange[offset] = data[2:]
            self.ram.setBlocks(address, blockToChange, offset)
            addressMessage += address

          # Write-allocate miss policy: load data from ram to cache and then write
          else:
            # Fill first available empty line with the data from ram (if possible), same process from cacheRead's simple miss procedure
            for i in range(self.associativity):
              if theSet.lines[i].valid == 0:
                theLine = theSet.lines[i]

                theLine.blocks = self.ram.getBlocks(address, self.blockSize, offset)
                theLine.valid = 1
                theLine.tag = tag

                doReplacement = False
                evictionLineNumber = str(i)

                if self.replacementPolicy == "least_recently_used" or self.replacementPolicy == "least_frequently_used":
                  lineNumber = str(i)
                  theSet.use = theSet.use.replace(lineNumber, "")
                  theSet.use += lineNumber
                
                if self.replacementPolicy == "least_frequently_used":
                  theSet.timesUsed[i] = 0

                break

            # If we get here, all the lines are valid, perform a replacement using the policy (exact same as in cache read)
            if doReplacement:

              # RR
              if self.replacementPolicy == "random_replacement":
                evictionLineNumber = randint(0,self.associativity-1)
                theSet.use = theSet.use.replace(str(evictionLineNumber),"") + str(evictionLineNumber)

              # LRU
              elif self.replacementPolicy == "least_recently_used":
                evictionLineNumber = theSet.use[0]
                theSet.use = theSet.use.replace(str(evictionLineNumber),"") + str(evictionLineNumber)

              # LFU
              else:
                leastTimesUsed = min(theSet.timesUsed)
                for i in range(len(theSet.timesUsed)):
                  if theSet.timesUsed[i] == leastTimesUsed:
                    evictionLineNumber = i
                    break
                theSet.use = theSet.use.replace(str(evictionLineNumber),"") + str(evictionLineNumber)

              theLine = theSet.lines[int(evictionLineNumber)]
              theLine.blocks = self.ram.getBlocks(address, self.blockSize, offset)
              theLine.tag = tag

            # Recur since write-allocate says to perform a cache write (preferrably a hit) once the data is loaded
            self.cacheWrite(address, data, evictionLineNumber, True)
        
        # Print the info at the end ONLY for no-write-allocate miss policy, since recursion from write-allocate causes multiple prints
        if self.writeMissPolicy == "no_write_allocate":
          print("set:" + str(index))
          print("tag:", end="")
          if tag[0] == "0":
            print(tag[1])
          else:
            print(tag)
          print(hitMessage)
          print("eviction_line:" + str(evictionLineNumber))
          print(addressMessage)
          print("data:0x" + data[2:])
          print("dirty_bit:" + str(theSet.lines[int(evictionLineNumber)].dirty))


    # Clear the cache
    def cacheFlush(self):
      self.sets = []
      for i in range(self.numSets):
        blankSet = Set(self.associativity, self.blockSize)
        self.sets.append(blankSet)
      print("cache_cleared")


    # Display the cache content and status
    def cacheView(self):
      print("cache-size:" + str(self.cacheSize))
      print("data_block_size:" + str(self.blockSize))
      print("associativity:" + str(self.associativity))
      print("replacement_policy:" + self.replacementPolicy)
      print("write_hit_policy:" + self.writeHitPolicy)
      print("write_miss_policy:" + self.writeMissPolicy)
      print("number_of_cache_hits:" + str(self.numHits))
      print("number_of_cache_misses:" + str(self.numMisses))

      print("cache_content:")
      for i in range(self.numSets):
        self.sets[i].printSet()


    # Display the RAM content and status
    def memoryView(self):
        self.ram.memoryView()


    # Dump current state of cache (its blocks content) into cache.txt
    def cacheDump(self):
      with open("cache.txt","w+") as f:
        for i in range(len(self.sets)):
          thisSet = self.sets[i]
          for j in range(len(thisSet.lines)):
            thisLine = thisSet.lines[j]
            for k in range(len(thisLine.blocks)):
              thisByte = thisLine.blocks[k]
              f.write(thisByte + " ")
            f.write("\n")


    # Dump the RAM content into ram.txt
    def memoryDump(self):
        self.ram.memoryDump()


    # Get the tag, set index, and block offset bits from a hex address (formatted "##"")
    def hexToBinaryString(self, address):
      bina = ""
      conversions = {"0":"0000","1":"0001","2":"0010","3":"0011","4":"0100","5":"0101","6":"0110","7":"0111","8":"1000","9":"1001",
      "A": "1010","B":"1011","C":"1100","D":"1101","E":"1110","F":"1111"}

      # Create the binary string from the 1 byte address
      for i in range(len(address)):
          bina += conversions[address[i].upper()]
  
      tag = bina[:self.numTagBits]
      index = bina[self.numTagBits:self.numSetIndexBits + self.numTagBits]
      offset = bina[self.numSetIndexBits + self.numTagBits:]

      return tag, index, offset
      

    # Takes in a binary string with a length that is a multiple of 4 and translates it to hex
    def fourBitsToHex(self, bits):
      hexVal = ""
      conversions = {"0000":"0","0001":"1","0010":"2","0011":"3","0100":"4","0101":"5","0110":"6","0111":"7","1000":"8","1001":"9",
      "1010":"A","1011":"B","1100":"C","1101":"D","1110":"E","1111":"F"}

      # Create the binary string from the 1 byte address
      j = 4
      for i in range(0, len(bits), 4):
        hexVal = conversions[bits[i:j]]
        j += 4

      return hexVal