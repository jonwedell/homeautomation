#!/bin/sh

pwgen -s 16 1|od -A n -t x1|sed 's/ /,0x/g'|sed 's/,//'|sed 's/0x0a//'