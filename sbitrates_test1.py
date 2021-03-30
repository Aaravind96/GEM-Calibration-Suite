import argparse
import time
import numpy as np
from scipy.optimize import curve_fit
import pandas as pd
import matplotlib.pyplot as plt
from multiprocessing import Process

def determine_thresh(data, thresh):
    val1=abs(data['SBit_Rate']-thresh).idxmin()
    return (data.iloc[val1].THR_ARM_DAC)

def plot_avg(df2, OH):
    sel=df2.OH==OH
    dataOH=df2[sel]    
    fig, ax = plt.subplots()
    ax.set_ylim(1,100000000)
    ax.set_xlabel('THR_ARM_DAC')
    ax.set_ylabel('S-Bit rate [Hz]')
    ax.set_yscale("log")
    n=0
    for vfat in dataOH.vfat.unique():        
        sel2=dataOH.vfat==vfat      
        datavfat=dataOH[sel2].reset_index()
        if n==0:
           curve, =ax.plot(datavfat.THR_ARM_DAC, datavfat.SBit_Rate, 'o')
           textcurve=ax.text(150, 1000000,'OH %i, VFAT %i'%(OH,vfat), ha='center', va='center')
           plt.savefig("Sbitrate_OH%i_VFAT%i.png"%(OH,vfat))
           n+=1
        else:
           curve.set_xdata(datavfat.THR_ARM_DAC)
           curve.set_ydata(datavfat.SBit_Rate)
           ax.draw_artist(curve)
           textcurve.set_text('OH %i, VFAT %i'%(OH,vfat))
           plt.savefig("Sbitrate_OH%i_VFAT%i.png"%(OH,vfat))      
        
start=time.time()
parser = argparse.ArgumentParser(description='Arguments to supply to sbitrates_1.py')
parser.add_argument("infilename", type=str, nargs='+', help="Filename from which input data is contained")
parser.add_argument('-p','--plotsbit', type=str, default="n", help="Argument to pick an option for plotting the sbit-rates vs THR_ARM_DAC. -p all: Plots for each VFAT are generated and saved. -p avg: Plots generated after averaging sbitrates for each VFAT, OH. Default: No plotting")
parser.add_argument('-t','--thresholdin', type=int, default=100, help="Noise threshold")
parser.add_argument('-o','--outfilename', type=str, default="SBitRates.txt", help="Filename to which analyzed data is written")
args = parser.parse_args()

infilename=args.infilename
dfs = []
iter=1
for fname in infilename:
    df = pd.read_csv(fname,names=["OH", "vfat", "THR_ARM_DAC","SBit_Rate"], sep=";")  
    df["iter"]=iter
    dfs.append(df)
    iter=iter+1
df = pd.concat(dfs)

outfilename = args.outfilename
df2=df.groupby(["OH", "vfat", "THR_ARM_DAC"]).SBit_Rate.mean().reset_index()
with open(outfilename,"w+") as file:
     file.write("OH/I:vfatN/I:threshold/I\n")      
     for OH in df2.OH.unique():
         sel=df2.OH==OH
         dataOH=df2[sel]
         for vfat in dataOH.vfat.unique():
             sel2=dataOH.vfat==vfat
             datavfat=dataOH[sel2].reset_index()
             thr=args.thresholdin
             threshold=determine_thresh(datavfat,thr)
             file.write("%i:%i:%i\n"%(OH,vfat,threshold))
         
if args.plotsbit=="avg":          
   pro= [Process(target=plot_avg, args=(df2, OH)) for OH in df2.OH.unique()]
   for p in pro:
       p.start()
   for p in pro:
       p.join()
    
if args.plotsbit=="all":
    df1=df
    for iter in df1.iter.unique():
        seli=df1.iter==iter
        df=df1[seli]
        with open("sbitrates_iter%i.txt"%iter,"w+") as file:
            file.write("Iter/I:OH/I:vfatN/I:threshold/I\n")
            fig, ax = plt.subplots()
            ax.set_ylim(1,100000000)
            ax.set_xlabel('THR_ARM_DAC')
            ax.set_ylabel('S-Bit rate [Hz]')
            ax.set_yscale("log")
            n=0        
            for OH in df.OH.unique():
                sel=df.OH==OH
                dataOH=df[sel]
                for vfat in dataOH.vfat.unique():
                    sel2=dataOH.vfat==vfat      
                    datavfat=dataOH[sel2].reset_index()
                    threshold=determine_thresh(datavfat,100)
                    file.write("%i:%i:%i:%i\n"%(iter,OH,vfat,threshold))    
                    if n==0:
                       curve, =ax.plot(datavfat.THR_ARM_DAC, datavfat.SBit_Rate, 'o')
                       textcurve=ax.text(150, 1000000,'Iter %i, OH %i, VFAT %i'%(iter,OH,vfat), ha='center', va='center')
                       plt.savefig("Sbitrate_i%i_OH%i_VFAT%i.png"%(iter,OH,vfat))
                       n+=1
                    else:
                       curve.set_xdata(datavfat.THR_ARM_DAC)
                       curve.set_ydata(datavfat.SBit_Rate)
                       ax.draw_artist(curve)
                       textcurve.set_text('Iter %i, OH %i, VFAT %i'%(iter,OH,vfat))
                       plt.savefig("Sbitrate_i%i_OH%i_VFAT%i.png"%(iter,OH,vfat))                    

