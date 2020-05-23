# commoper.py

# Format and write results to output file
def FormatWrite(s, file):
  sorteds = sorted(list(s))
  for node in sorteds:
    file.write(str(node) + " ")

# File handling
inputfile = open("cmtyvv.txt", "r")
outputfile = open("commoperoutput.txt", "w")

# Fetch communities from input file
commlist = [set(line.split()) for line in inputfile]

# Ask for a query and process it
while True:
  query = input("Enter <Community-1-ID> <Operator> <Community-2-ID> or <Community-ID> or EXIT: ").split()
  if len(query) == 1:
    if query[0] == "EXIT":
      break
    else:
      i = int(query[0])
      comm = commlist[i]
      outputfile.write("Community " + str(i) + " (Length = " + str(len(comm)) + "): ")
      FormatWrite(comm, outputfile)
      outputfile.write("\n")
  else:
    i = int(query[0])
    j = int(query[2])
    if query[1] == "UNION":
      union = commlist[i].union(commlist[j])
      outputfile.write("Community " + str(i) + " UNION Community " + str(j) + " (Length = " + str(len(union)) + "): ")
      FormatWrite(union, outputfile)
      outputfile.write("\n")
    elif query[1] == "INTERSECTION":
      intersection = commlist[i].intersection(commlist[j])
      outputfile.write("Community " + str(i) + " INTERSECTION Community " + str(j) + " (Length = " + str(len(intersection)) + "): ")
      FormatWrite(intersection, outputfile)
      outputfile.write("\n")
    elif query[1] == "DIFF":
      diff = commlist[i].difference(commlist[j])
      outputfile.write("Community " + str(i) + " DIFF Community " + str(j) + " (Length = " + str(len(diff)) + "): ")
      FormatWrite(diff, outputfile)
      outputfile.write("\n")
    elif query[1] == "SYMM-DIFF":
      symmdiff = commlist[i].symmetric_difference(commlist[j])
      outputfile.write("Community " + str(i) + " SYMM-DIFF Community " + str(j) + " (Length = " + str(len(symmdiff)) + "): ")
      FormatWrite(symmdiff, outputfile)
      outputfile.write("\n")
print("Results successfully written to commoperoutput.txt!")

# File handling
inputfile.close()
outputfile.close()
