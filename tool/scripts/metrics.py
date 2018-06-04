#!/usr/bin/python
#
#   [2018] S. Capella-Gutierrez - salvador.capella@bsc.es
#
#   this script is free software: you can redistribute it and/or modify it under
#   the terms of the GNU General Public License as published by the Free
#   Software Foundation, the last available version.
#
#   this script is distributed in the hope that it will be useful, but WITHOUT
#   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#   FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
#   more details on <http://www.gnu.org/licenses/>
#

import os
import sys
import random
import hashlib
import argparse

if __name__ == "__main__":

  parser = argparse.ArgumentParser()

  parser.add_argument("--reference", dest = "refFile", required = True, 
    type = str, help = "Reference Proteome List")

  parser.add_argument("--species_tag", dest = "species", default = "HUMAN",  
	type = str, help = "Set mnemotechnic UNIPROT species label")

  parser.add_argument("--input", dest = "inFile", required = True, type = str,
    help = "Provide the input file to be validated")

  parser.add_argument("--out", dest = "outFile", default = None, type = str, \
    help = "Set output file. Default is STDOUT")

  parser.add_argument("--golden", dest = "goldenFiles", default = [], type = str,
    nargs = "+", help = "Provide at least one golden reference dataset")

  args = parser.parse_args()

  ## Check reference proteome file
  if not os.path.isfile(args.refFile):
    sys.exit(("ERROR: Check Reference Proteome File '%s'") % (args.refFile))

  ## Check input file to be validated
  if not os.path.isfile(args.inFile):
    sys.exit(("ERROR: Check Input File '%s'") % (args.inFile))

  ## Check golden dataset files
  goldenFiles = []
  for infile in args.goldenFiles:
    if not os.path.isfile(infile):
      print("ERROR: Check Golden Reference File '%s'" % (infile))
      continue
    goldenFiles.append(infile)

  if not goldenFiles:
    sys.exit(("ERROR: Check provided Golden Reference File/s"))

  ## Load proteome file 
  all_proteins = []
  for line in open(args.refFile, "r"):
    ## Skip header
    if line.find(args.species) == -1:
      continue
    ## We save field #2 which contains protein "Entry Name"
    f = [e.strip() for e in line.split("\t")]
    all_proteins.append(f[1])
  print('[1]\t{0:14} => {1:10,g}\n'.format("All Proteins", len(all_proteins)))
  
  remaining_proteins = set(all_proteins)
  gold_datasets = {}
  
  for infile in sorted(goldenFiles):
    ref = ".".join(os.path.split(infile)[1].split(".")[:-1])
    
    gold_datasets.setdefault(ref, set())
    for line in open(infile, "r"):
      ## Skip header
      if line.find(args.species) == -1:
        continue
      ## We save field #1 which contains protein "Entry Name"
      f = [e.strip() for e in line.split("\t")]
      gold_datasets[ref].add(f[0])
      
    remaining_proteins -= gold_datasets[ref]
    print('[2]\t{0:60} => {1:10,g}'.format(ref, len(gold_datasets[ref])))
      
  ## Load file to be validated 
  input_proteins = []
  for line in open(args.inFile, "r"):
    ## Skip header
    if line.startswith("#"):
      continue
    ## We save field #1 which contains protein "Entry Name"
    f = [e.strip() for e in line.split("\t")]
    input_proteins.append(f[0])
    
  print('\n[3]\t{0:60} => {1:10,g}\n'.format("Detected Proteins", \
    len(input_proteins)))
 
  ## Assuming we have a perfect input data which only contain proteins from the three gold reference datasets
  minimum_size = len(set(all_proteins) - remaining_proteins)
          
  true_positive = len(set(input_proteins) - set(remaining_proteins))
  false_positive = len(set(input_proteins) & set(remaining_proteins))

  input_tag = os.path.split(args.inFile)[1].split(".")[0]
  print('[4]\t{0:60} => Size: {1:6,g} TP: {2:6,g} FP: {3:,g}'.format(input_tag,
        true_positive + false_positive, true_positive, false_positive))
            
  if args.outFile:
    sys.stdout = open(args.outFile, "w")
            
  for ref in sorted(gold_datasets):
    overlap = gold_datasets[ref] & set(input_proteins)
    ratio = len(overlap)/len(gold_datasets[ref])
    sys.stdout.write('{0:40}\tSize:{1:8}\t{2:60}\tx:{4:4}\ty:{3:10,g}\n'.format(
      input_tag, len(input_proteins), ref, ratio, len(overlap)))
  
  ratio = true_positive/(true_positive+false_positive)
  sys.stdout.write('{0:40}\tSize:{1:8}\t{2:60}\tx:{4:4}\ty:{3:10,g}\n'.format(
    input_tag, len(input_proteins), "all", ratio, true_positive))
    
  sys.stdout.close()