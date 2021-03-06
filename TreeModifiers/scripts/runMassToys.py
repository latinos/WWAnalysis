#!/usr/bin/env python

import sys
import os.path
import optparse
import fnmatch

def main():
    usage = '''usage: %prog [opts] scenario'''
    parser = optparse.OptionParser(usage)
    parser.add_option('-a','--config1D',dest='oneD',help='Run 1D fit (m4l) ', action='store_true', default=False)
    parser.add_option('-b','--config2D',dest='twoD',help='Run 2D fit (m4l-merr) ', action='store_true', default=False)
    parser.add_option('-c','--config3D',dest='threeD',help='Run 1D fit (m4l-merr-KD) ', action='store_true', default=False)
    parser.add_option('--queue','-q',dest='queue',help='run in batch in queue specified as option (default -q 8nh)', default='8nh')
    parser.add_option('-t', '--toy'     , dest='toys'        , help='Number of toys'                             , default=None   , type='int'   )

    (opt, args) = parser.parse_args()
    toysperjob=25
    jobs = opt.toys/toysperjob

    dcdir  = os.getcwd()+'/cards/'
    outdir = os.getcwd()+'/results/'
    logdir = os.getcwd()+'/log/'
    srcdir = os.getcwd()+'/Src/'
    
    onedext   ='c1DNoMassErr'
    twodext   ='c1DMassErr'
    threedext ='c2DMassErr'

    ext=''
    if(opt.oneD):
        print 'you chose 1D'
        ext='c1DNoMassErr/'
    elif(opt.twoD):
        print 'you chose 2D'
        ext='c1DMassErr/'
    elif(opt.threeD):
        print 'you chose 3D'
        ext='c2DMassErr/'
    else:
        print 'You have to use 1D, 2D or 3D fit. Exiting.' 
        return

    dcdir += ext
    outdir += ext
    logdir += ext
    srcdir += ext

    #channels = ['4mu','4e','2e2mu','comb']
    channels = ['4mu','4e','2e2mu']
    for ch in channels:
        print "submitting toys for channel "+ch+"..."
        command = 'combine -M MultiDimFit '
        command = command+dcdir+'FloatMass_'+ch+'_hzz.root '
        command = command+'-m 125.8 -P MH --floatOtherPOI=1 --algo=singles -n MASS_'+ch+' --expectSignal=1 -t '+str(toysperjob)+' -s -1' 

        print 'I will run '+str(jobs)+' jobs with '+str(toysperjob)+' toys each...'
        for j in range(jobs):
            f=open(srcdir+'run-ch'+ch+'-j'+str(j)+'.src','w')
            f.write('cd ~/workspace/hzz4l/CMSSW_6_1_1/src/\n')
            f.write('eval `scram ru -sh` \n')
            f.write('cd - \n')
            f.write(command+'\n')
            move = 'cp higgsCombineMASS_'+ch+'.MultiDimFit*root %s ' % (outdir)
            f.write(move+'\n')
            f.close()
            bsub = 'bsub -q %s -J ch%s-j%s -o %s/ch-%s-job-%s.log source %s/run-ch%s-j%s.src' % (opt.queue,ch,j,logdir,ch,j,srcdir,ch,j)
            print 'submitting job #'+str(j)
            print bsub
            os.system(bsub)


if __name__ == '__main__':
    main()
        
