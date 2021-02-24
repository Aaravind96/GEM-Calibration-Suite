import argparse
#from pathlib import Path

parser = argparse.ArgumentParser(description='Arguments to supply to sbitrates_1.py')
parser.add_argument("infilename", type=str, help="Filename from which input data is contained")
#parser.add_argument('-d','--debug', action='store_true', help="Prints additional debugging information")
parser.add_argument('-t','--thresholdin', type=int, default=100, help="Threshold")
parser.add_argument('-o','--outfilename', type=str, default="SBitRates.txt", help="Filename to which analyzed data is written")
args = parser.parse_args()

import numpy as np
from scipy.optimize import curve_fit
import pandas as pd
import matplotlib.pyplot as plt

infilename=args.infilename
#fnames=Path(infilename).match("*/Scan_iteration*.txt")
df = pd.read_csv(infilename,names=["OH", "vfat", "THR_ARM_DAC","SBit_Rate"], sep=";")

def determine_thresh(data, thresh):
    val1=abs(data['SBit_Rate']-thresh).idxmin()
    return (data.iloc[val1].THR_ARM_DAC)

outfilename = args.outfilename
with open(outfilename,"w+") as file:
     file.write("OH/I:vfatN/I:threshold/I\n")      
     for OH in df.OH.unique():
         sel=df.OH==OH
         dataOH=df[sel]
         for vfat in dataOH.vfat.unique():
             sel2=dataOH.vfat==vfat
             datavfat=dataOH[sel2].reset_index()
             thr=args.thresholdin
             threshold=determine_thresh(datavfat,thr)
             file.write("%i:%i:%i\n"%(OH,vfat,threshold))
