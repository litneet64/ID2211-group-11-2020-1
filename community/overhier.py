# overhier.py

# Define constants (default = the graph we used)
N = 157
NNODES = 40336
OVERTRESHOLD = 0.2
HIERTRESHOLD = 0.8

# Calculate Jaccard coefficient
def JaccardCoef(set1, set2):
  return len(set1.intersection(set2))/len(set1.union(set2))

# File handling
inputfile = open("../../outputs/cmtyvv.txt", "r")
outputfile = open("../../outputs/overhieroutputX.txt", "w")

# Find overlapping and hierarchical communities
overlist = list()
hierlist = list()
commlist = [set(line.split()) for line in inputfile]
lencommlist = [len(comm) for comm in commlist]
for i in range(N):
  for j in range(i + 1, N):
    jc = JaccardCoef(commlist[i], commlist[j])
    leni = lencommlist[i]
    lenj = lencommlist[j]
    lenover = len(commlist[i].intersection(commlist[j]))
    info = (i, j, leni, lenj, lenover, jc)
    if jc > OVERTRESHOLD:
      overlist.append(info)
    if lenover/leni > HIERTRESHOLD or lenover/lenj > HIERTRESHOLD:
      hierlist.append(info)

# Sort all lists in descending order of overlap length
commlistwinfo = list(zip(range(N), lencommlist))
sortedcommlistwinfo = sorted(commlistwinfo, key=lambda info: info[1], reverse=True)
sortedoverlist = sorted(overlist, key=lambda info: info[4], reverse=True)
sortedhierlist = sorted(hierlist, key=lambda info: info[4], reverse=True)

# Find percentage of nodes in communities
superset = set()
for i in range(N):
  superset = superset.union(commlist[i])
perc = len(superset)/NNODES

# Write results
outputfile.write("Constants: " + "\n")
outputfile.write("N = " + str(N) + "\n")
outputfile.write("NNODES = " + str(NNODES) + "\n")
outputfile.write("OVERTRESHOLD = " + str(OVERTRESHOLD) + "\n")
outputfile.write("HIERTRESHOLD = " + str(HIERTRESHOLD) + "\n")
outputfile.write("\n")
outputfile.write("Percentage of nodes in communities = " + str(perc) + "\n")
outputfile.write("Communities sorted in descending order of length: " + "\n")
outputfile.write("(i, lencomm)" + "\n")
for info in sortedcommlistwinfo:
  outputfile.write(str(info) + "\n")
outputfile.write("\n")
outputfile.write("Number of sufficiently overlapping communities = " + str(len(overlist)) + "\n")
outputfile.write("Sufficiently overlapping communities sorted in descending order of overlap length: " + "\n")
outputfile.write("(i, j, leni, lenj, lenover, jc)" + "\n")
for info in sortedoverlist:
  outputfile.write(str(info) + "\n")
outputfile.write("\n")
outputfile.write("Number of sufficiently hierarchical communities = " + str(len(hierlist)) + "\n")
outputfile.write("Sufficiently hierarchical communities sorted in descending order of overlap length: " + "\n")
outputfile.write("(i, j, leni, lenj, lenover, jc)" + "\n")
for info in sortedhierlist:
  outputfile.write(str(info) + "\n")
print("Results successfully written to overhieroutput.txt!")

# File handling
inputfile.close()
outputfile.close()