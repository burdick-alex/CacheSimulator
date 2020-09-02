'''
File: cachesimulator.py
Author(s): Alex Burdick, Dean Orenstein
Date: 04/30/2020
Section: 511
E-mail: burdick.alex@tamu.edu, dean27@tamu.edu

The simulator itself: the main program, which reads cache configuration values
from the user, prompts the user with simulation options, and then performs
various cache functionalities, including read, write, and clear.
Also includes some helper functions
'''

from Cache import Cache
from MainMemory import MainMemory
import sys

# Checks the user's input for cacheSize, blockSize, and associativity when configuring cache
def isCorrectInput(entry, lowBound, upBound):
  if entry.isdigit() and (int(entry) < lowBound or int(entry) > upBound):
      return False
  elif not entry.isdigit():
    return False
  else:
    return True


# Makes sure the address/data in hex provided by the user (for cache-read or cache-write) is valid
def isValidByte(byte):
  # Not valid if not in the form of "0x#"" or "0x##" (where # is an int/char)
  if len(byte) > 4 or len(byte) < 3:
    return False
  if byte[0:2] != "0x":
    return False

  # If first # is a char its hex value cant be greater than F
  if byte[2].isalpha():
    if byte[2].upper() > 'F':
      return False

  # Also not valid if not an int/char
  elif not byte[2].isdigit():
    return False

  # If we have a second #, check the same things
  if len(byte) == 4:
    if byte[3].isalpha():
      if byte[3].upper() > 'F':
        return False
    elif not byte[3].isdigit():
      return False

  return True


# Start the simulator, initialize the physical memory with bytes in hexadecimal provided in input.txt
print("*** Welcome to the cache simulator ***")
print("initialize the RAM:")
print("init-ram 0x00 0xFF")
ourRam = MainMemory()
ourRam.readFromFile(sys.argv[1])
print("ram successfully initialized!")


# Get values from user on cache specifics (check validity)
print("configure the cache:")

# C
cacheSize = input("cache size: ")
if not isCorrectInput(cacheSize, 8, 256):
  sys.exit("Invalid cache size!")

# B
blockSize = input("data block size: ")
if not isCorrectInput(blockSize, 1, int(cacheSize)):
  sys.exit("Invalid block size!")
  
'''
E
Direct-mapped: E = 1
Set-associative: 1 < E < C/B
Fully-associative: E = C/B
'''
associativity = input("associativity: ")
if not isCorrectInput(associativity, 1, int(cacheSize)/int(blockSize)):
  sys.exit("Invalid associativity!")

replacementPolicy = input("replacement policy: ")
if not isCorrectInput(replacementPolicy, 1, 3):
  sys.exit("Invalid replacement policy!")
writeHitPolicy = input("write hit policy: ")
if not isCorrectInput(writeHitPolicy, 1, 2):
  sys.exit("Invalid write hit policy!")
writeMissPolicy = input("write miss policy: ")
if not isCorrectInput(writeMissPolicy, 1, 2):
  sys.exit("Invalid write miss policy!")

# Easy testing
'''
cacheSize = 32
blockSize = 8
associativity = 1
replacementPolicy = 1
writeHitPolicy = 1
writeMissPolicy = 1
'''

ourCache = Cache(ourRam, cacheSize, blockSize, associativity, replacementPolicy, writeHitPolicy, writeMissPolicy)
print("cache successfully configured!")


# Indefinitely prompt user with menu until they type quit or an invalid option
while True:
  choice = input("*** Cache simulator menu ***\n"
  "type one command:\n"
  "1. cache-read\n"
  "2. cache-write\n"
  "3. cache-flush\n"
  "4. cache-view\n"
  "5. memory-view\n"
  "6. cache-dump\n"
  "7. memory-dump\n"
  "8. quit\n"
  "****************************\n")

  choice = choice.split(" ")
  numArgs = len(choice)

  if choice[0] == "cache-read" and numArgs == 2 and isValidByte(choice[1]):
    ourCache.cacheRead(choice[1])

  elif choice[0] == "cache-write" and numArgs == 3 and isValidByte(choice[1]) and isValidByte(choice[2]):
    ourCache.cacheWrite(choice[1], choice[2], -1, False)

  elif choice[0] == "cache-flush" and numArgs == 1:
    ourCache.cacheFlush()

  elif choice[0] == "cache-view" and numArgs == 1:
    ourCache.cacheView()

  elif choice[0] == "memory-view" and numArgs == 1:
    ourCache.memoryView()
  
  elif choice[0] == "cache-dump" and numArgs == 1:
    ourCache.cacheDump()
  
  elif choice[0] == "memory-dump" and numArgs == 1:
    ourCache.memoryDump()
  
  elif choice[0] == "quit" and numArgs == 1:
    break
  
  else:
    sys.exit("Invalid choice!")