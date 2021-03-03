import argparse
#from pathlib import Path

parser = argparse.ArgumentParser(description='Arguments to supply to sbitrates_1.py')
parser.add_argument("infilename", type=str, help="Filename from which input data is contained")
parser.add_argument('-p','--plotsbit', type=str, default="n", help="Argument to pick an option for plotting the sbit-rates vs THR_ARM_DAC. -p all: Plots for each VFAT are generated and saved. -p avg: Plots generated after averaging sbitrates for each VFAT, OH. Default: No plotting")
parser.add_argument('-t','--thresholdin', type=int, default=100, help="Noise threshold")
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
df2=df.groupby(["OH", "vfat", "THR_ARM_DAC"]).SBit_Rate.mean().reset_index()
with open(outfilename,"w+") as file:
     file.write("OH/I:vfatN/I:threshold/I\n")      
     for OH in df2.OH.unique():
         sel=df2.OH==OH
         dataOH=df[sel]
         for vfat in dataOH.vfat.unique():
             sel2=dataOH.vfat==vfat
             datavfat=dataOH[sel2].reset_index()
             thr=args.thresholdin
             threshold=determine_thresh(datavfat,thr)
             file.write("%i:%i:%i\n"%(OH,vfat,threshold))
            
if args.plotsbit=="avg":
#    df2=df.groupby(["OH", "vfat", "THR_ARM_DAC"]).SBit_Rate.mean().reset_index()
#    with open("sbitrates_avg.txt","w+") as file:
#        file.write("OH/I:vfatN/I:threshold/I\n")
    for OH in df2.OH.unique():
        sel=df2.OH==OH
        dataOH=df2[sel]
        for vfat in dataOH.vfat.unique():
            sel2=dataOH.vfat==vfat
            plt.ioff()
            plt.figure()
            datavfat=dataOH[sel2].reset_index()
            plt.semilogy(datavfat.THR_ARM_DAC, datavfat.SBit_Rate, '.')
            threshold=determine_thresh(datavfat,100)
#            file.write("%i:%i:%i\n"%(OH,vfat,threshold))
            plt.ylim(1,100000000)
            plt.xlabel('THR_ARM_DAC')
            plt.ylabel('S-Bit rate [Hz]')
            plt.text(150, 1000000,'OH %i, VFAT %i'%(OH,vfat), ha='center', va='center')
            plt.savefig("Sbitrate_avg_OH%i_VFAT%i.png"%(OH,vfat))
            plt.close()
if args.plotsbit=="all":
    with open("sbitrates_avg.txt","w+") as file:
        file.write("OH/I:vfatN/I:threshold/I\n")
        for OH in df.OH.unique():
            sel=df.OH==OH
            dataOH=df[sel]
            for vfat in dataOH.vfat.unique():
                sel2=dataOH.vfat==vfat
                plt.ioff()
                plt.figure()
                datavfat=dataOH[sel2].reset_index()
                plt.semilogy(datavfat.THR_ARM_DAC, datavfat.SBit_Rate, '.')
                threshold=determine_thresh(datavfat,100)
                file.write("%i:%i:%i\n"%(OH,vfat,threshold))
                plt.ylim(1,100000000)
                plt.xlabel('THR_ARM_DAC')
                plt.ylabel('S-Bit rate [Hz]')
                plt.text(150, 1000000,'OH %i, VFAT %i'%(OH,vfat), ha='center', va='center')
                plt.savefig("Sbitrate_OH%i_VFAT%i.png"%(OH,vfat))
                plt.close()
