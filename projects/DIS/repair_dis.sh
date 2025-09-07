git checkout -- *.CLS
git checkout -- *.DIS
git checkout -- *.TOC

for EXT in DIS TOC CLS
do
  perl -i -pe 's/\\/#/g' *.${EXT}
  perl -i -pe 's/\r//g'  *.${EXT}
  perl -i -pe 's/`/#/g'  *.${EXT}

  perl -i -pe 's/\x1A//g' *.${EXT}
done

perl ../STEDT5-U4Map-7.plx .

for f in `ls *.u8`
do
  python3 ../RE_DATA_1994/fix_sequences.py $f $f.fix
done

for f in `ls *.DIS *.TOC *.CLS`
do
  cp $f.u8.fix $f
  rm $f.u8 $f.u8.fix
done

