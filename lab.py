"""Fixed-seed independent calibration, held-out alarms, and optical risk."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import sequence,scores,threshold,weights,mean_covariance,population_lag
from optics import image,fit_center,ORIGIN,VELOCITY,READ_SD,SIGMA

def run():
    train_rng,test_rng,camera_rng,clock_rng=[np.random.default_rng(s) for s in (18001,18002,18003,18004)]
    n,m,trials=96,32,800
    training=np.array([scores(sequence(train_rng,n,0),sequence(train_rng,n,0)) for _ in range(999)])
    cut=threshold(training); old_w,new_w=weights(m,0),weights(m,60)
    result=dict(seed_streams=[18001,18002,18003,18004],pilot_n=n,measurement_m=m,training_pairs=999,
                heldout_per_scenario=trials,thresholds=cut.tolist(),sigma_px=SIGMA,
                weights_old=old_w.tolist(),weights_alternative=new_w.tolist(),scenarios={})
    tau=.12; center=ORIGIN+VELOCITY*tau
    for angle in (0,30,60,90):
        alarms=[];errors=[];conditional=[];affine_error=0.
        v=mean_covariance(m,angle)
        for _ in range(trials):
            old,pilot=sequence(test_rng,n,0),sequence(test_rng,n,angle)
            s=scores(old,pilot); alarm=s>cut
            # Independent final image and clock repeats; paired policies share both.
            optical_time=(fit_center(image(center)+camera_rng.normal(0,READ_SD,33))-ORIGIN)/VELOCITY
            e=sequence(clock_rng,m,angle).mean(0)
            ws=[old_w,new_w if alarm[0] else old_w,new_w if alarm[1] else old_w,weights(m,angle)]
            errors.append([optical_time-w@e-tau for w in ws])
            conditional.append([w@v@w for w in ws]);alarms.append(alarm)
            q=np.array([[0.,-1.],[1.,0.]])
            affine_error=max(affine_error,float(np.max(abs(scores(old@q,pilot@q)-s))))
        errors=np.array(errors);conditional=np.array(conditional);alarms=np.array(alarms)
        delta=(errors[:,2]**2-errors[:,1]**2)*1e6
        result['scenarios'][str(angle)]=dict(alarm_rates=alarms.mean(0).tolist(),
            rmse_ms=(np.sqrt(np.mean(errors**2,0))*1000).tolist(),
            exact_clock_rmse_ms=(np.sqrt(conditional.mean(0))*1000).tolist(),
            matrix_minus_spectrum_mse_ms2=float(delta.mean()),paired_two_mcse_ms2=float(2*delta.std(ddof=1)/np.sqrt(trials)),
            max_common_rotation_score_error=affine_error)
    out=Path('outputs');out.mkdir(exist_ok=True)
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    fig,axs=plt.subplots(1,3,figsize=(13,3.7),layout='constrained')
    angles=list(result['scenarios']);rows=list(result['scenarios'].values())
    for j,name in enumerate(('spectrum','matrix')):axs[0].plot(angles,[r['alarm_rates'][j] for r in rows],'o-',label=name)
    axs[0].set(xlabel='Mode rotation (degrees)',ylabel='Alarm probability',ylim=(0,1));axs[0].legend()
    for j,name in enumerate(('keep old','spectrum policy','matrix policy','oracle')):axs[1].plot(angles,[r['rmse_ms'][j] for r in rows],'o-',label=name)
    axs[1].set(xlabel='Mode rotation (degrees)',ylabel='Optical-delay RMSE (ms)');axs[1].legend(fontsize=8)
    axs[2].plot(np.arange(-16,17),image(center),'o-');axs[2].set(xlim=(-3,3),xlabel='Sensor x (px)',ylabel='Expected signal (electron-equivalent)')
    fig.savefig(out/'experiment.png',dpi=140);plt.close(fig)
    print(json.dumps(result,indent=2))
if __name__=='__main__':run()
