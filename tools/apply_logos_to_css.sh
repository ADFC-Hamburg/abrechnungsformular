#!/bin/sh

usage() # EXITCODE
{
    echo "Usage: $(basename $0) DIRECTORY TARGET..."
    echo "Scans a DIRECTORY for logo files."
    echo "Searches TARGET(s) for this pattern:\n  url('path/to/file/filename.svg'),url('path/to/file/filename.png')"
    echo "Matches are edited according to logos found."
    exit $1
}

replace_url() # FILEPATH PATHTOKEEP SEARCHSTRING REPLACESTRING
{
    sed -i -E "s/url\\('([^']*)$3\\.svg'\\),url\\('([^']*)$3\\.png'\\)/url\\('\\$2$4'\\)/g" "$1"
}


if [ -z "$1" ] || [ -z "$2" ]; then usage 1; fi
if [ $1 = "--help" ] || [ $1 = "--usage" ]; then usage 0; fi
DIR=$1
shift

if [ -f "$DIR/logo.svg" ]; then
    SVGorPNG=1
    EXTENSION=".svg"
else
    SVGorPNG=2
    EXTENSION=".png"
fi

for file in "$@"; do
    replace_url "$file" $SVGorPNG logo logo$EXTENSION
done


if [ -f "$DIR/logo-semiwhite.svg" ]; then
    SVGorPNG=1
    EXTENSION="-semiwhite.svg"
else
    SVGorPNG=2
    if [ -f "$DIR/static/img/logo-semiwhite.png" ]; then
        EXTENSION="-semiwhite.png"
    else
        EXTENSION=".png"
    fi
fi

for file in "$@"; do
    replace_url "$file" $SVGorPNG logo-semiwhite logo$EXTENSION
done


if [ -f "$DIR/logo-white.svg" ]; then
    SVGorPNG=1
    EXTENSION="-white.svg"
else
    SVGorPNG=2
    if [ -f "$DIR/static/img/logo-white.png" ]; then
        EXTENSION="-white.png"
    elif [ -f "$DIR/static/img/logo-semiwhite.png" ]; then
        EXTENSION="-semiwhite.png"
    else
        EXTENSION=".png"
    fi
fi

for file in "$@"; do
    replace_url "$file" $SVGorPNG logo-white logo$EXTENSION
done
