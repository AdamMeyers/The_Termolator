#reffile = 'out/annotation2.out'
#targetfile = 'out/annotation2KLDiv.out'
reffile = '/misc/proteus107/zg440/bio/436/sample-outlist-annotation2.out'
targetfile = '/misc/proteus107/zg440/bio/436/top-bothlists-annotation2.out'
# get reference annotatations
f = open(reffile)
reflines = f.read().split('\n')
f.close()
# create lookup dictionary
refindex = {}
for i in range(len(reflines)):
    key = reflines[i].split(' | ')[0]
    refindex[key] = i
# get target annotations
f = open(targetfile)
lines = f.read().split('\n')
f.close()
# fill in target annotations using reference
for i in range(len(lines)):
    key = lines[i].split(' | ')[0]
    if key in refindex:
        lines[i] = reflines[refindex[key]]
# write to file
f = open(targetfile,'w')
for i in range(len(lines)):
    f.write(lines[i]+'\n')
f.close()
