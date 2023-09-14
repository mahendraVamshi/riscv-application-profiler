#!/bin/bash

cat > .original
cat .original | awk '{match($0, /0x[0-9a-fA-F]+/); print substr($0, RSTART, RLENGTH)}' > .original.tmp.swp ;
cat .original | awk -F'[()]' '{print "DASM(" $2 ")"}' | spike-dasm > .dasm.tmp.swp ;
exec 3<.original.tmp.swp
exec 4<.dasm.tmp.swp
echo "" > .merged.tmp.swp
while read -r line1 <&3 && read -r line2 <&4; do
    echo "$line1    ::    $line2" >> .merged.tmp.swp
done
exec 3<&-
exec 4<&-
cat .merged.tmp.swp > $1
rm -f .original
rm -f .original.tmp.swp
rm -f .dasm.tmp.swp
rm -f .merged.tmp.swp