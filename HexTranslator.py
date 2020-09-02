with open("codes2.txt", "w") as c:
    for i in range(2**13):
        line = "0x" + str(hex(i))[2:].upper() + "\n"#+ " in binary is " + str(bin(i))[2:].zfill(13) + "\n"
        c.write(line)

