#!/bin/bash

awk -F'[()]' '{print "DASM(\"" $2 "\")"}' | spike-dasm