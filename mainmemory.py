'''
File: MainMemory.py
Author(s): Alex Burdick, Dean Orenstein
Date: 04/30/2020
Section: 511
E-mail: burdick.alex@tamu.edu, dean27@tamu.edu

MainMemory class: represents a 256-byte RAM with each word being 1 byte.
Assigns hex data values from a text file to their corresponding hex addresses 
'''

class MainMemory:
    def __init__(self):
      self.content = {}

    def readFromFile(self, fileName):
      # If file name is invalid, ask user for new file name
      while True:
        try:
          dataFile = open(fileName, 'r')
        except:
          print("Bad filename!")
          fileName = input("Enter a valid filename:\n")
          continue
        break

      # Get a list of the lines from the file and update dictionary, assuming file has valid data entries
      data = dataFile.read().splitlines()

      # Addresses 0-15 need a filler "0" in the address
      for i in range(16):
        convertedAddress = str(hex(i))
        address = convertedAddress[0:2] + "0" + convertedAddress[-1].upper()
        self.content[address] = str(data[i]).upper()

      for i in range(16, 256):
        address = "0x" + hex(i)[2:].upper()
        self.content[address] = str(data[i]).upper()

      dataFile.close()
    

    # Get the blockSize blocks of data starting at address - offset
    def getBlocks(self, address, blockSize, offset):
      # Convert hex address to decimal, which is the particular starting RAM addresss
      startKey = int(address[2:], 16)
      startKey -= offset
      endKey = startKey + blockSize
      fullBlock = []

      for i in range(startKey, endKey):  # (start key, end key)
        # Convert int addresss back to hex and add its data to full block
        hexKey = "0x"
        if i < 16:
          hexKey += "0"
        hexKey += hex(i)[2:].upper()
        fullBlock.append(self.content[hexKey])

      return fullBlock


    # Set the blockSize blocks of data starting at address - offset
    def setBlocks(self, address, newBlock, offset):
      ramKeys = list(self.content.keys())
      start = 0

      for i in range(len(ramKeys)):
        if(ramKeys[i] == address):
          start = i
          break

      start -= offset
      end = start + len(newBlock)

      j = 0
      for i in range(start, end):  # (start key, end key)
        self.content[ramKeys[i]] = newBlock[j]
        j+=1


    # Dump the memory content into ram.txt
    def memoryDump(self):
      with open("ram.txt","w+") as f:
        ramKeys = list(self.content.keys())
        for i in range(len(ramKeys)):
          if(i == len(ramKeys) - 1):
            f.write(self.content[ramKeys[i]])
          else:
            f.write(self.content[ramKeys[i]] + "\n")


    # Displays the memory content and status
    def memoryView(self):
      ramKeys = list(self.content.keys())
      print("memory_size:" + str(len(ramKeys)))
      print("memory_content:")
      print("Address:Data")
      rest = ""
      
      for i in range(len(ramKeys)):
        if (i == 0):
          print(ramKeys[i] + ":",end="")
          rest += self.content[ramKeys[i]] + " "
        elif (i % 8 == 0):
          print(rest[:-1])
          rest = ""
          print(ramKeys[i] + ":",end="")
          rest += self.content[ramKeys[i]] + " "
        else:
          rest += self.content[ramKeys[i]] + " "
      print(rest)

