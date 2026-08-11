#!/bin/sh

# Create partially white and fully black versions of logo.svg in a given directory

DIR=${1:-$PWD}

if [ -f "$DIR/logo.svg" ] && [ ! -f "$DIR/logo-semiwhite.svg" ]; then
    # generate logo-semiwhite.svg
    sed -E 's/#[0-5][0-9a-fA-F][0-7][0-9a-fA-F][4-9a-fA-F][0-9a-fA-F]/white/g' "$DIR/logo.svg" > "$DIR/logo-semiwhite.svg"
fi

if [ -f "$DIR/logo-semiwhite.svg" ] && [ ! -f "$DIR/logo-black.svg" ]; then
    # generate logo-black.svg
    sed -E 's/(#[0-9a-fA-F]{6}|white)/black/g' "$DIR/logo-semiwhite.svg" > "$DIR/logo-black.svg"
fi
