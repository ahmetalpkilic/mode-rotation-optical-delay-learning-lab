# Derivation and coordinate conventions

## Pupil to integrated camera samples

Use an untruncated scalar paraxial Gaussian pupil amplitude P(r)=exp(−r²/a²), a=1000 µm (1/e amplitude radius), wavelength λ=0.550 µm, focal length f=16000 µm. This is an apodized infinite-support pupil, not a hard circular aperture; a hard-aperture f-number or Airy diameter is not substituted.

The Fourier transform of exp(−x²/a²) is proportional to exp(−π²a²ν²). Set ν=X/(λf), square the amplitude, and identify exp(−X²/(2σ²)): σ_sensor=λf/(2πa). Pixel pitch p=4 µm gives σ_px=λf/(2πap), approximately 0.35014 px. This narrow PSF is undersampled; exact pixel integration is essential.

Use the 1-D marginal of a separable 2-D intensity PSF. Pixel centers are integers −16…16; edges j±0.5; positive x points right. Principal point is x=0 in centered coordinates (array index 16). A corresponding 33×33 camera has K=[[4000,0,16],[0,4000,16],[0,0,1]] in zero-based array coordinates, square pixels and zero skew/distortion. No object-plane metric scale is inferred.

For total marginal flux F=10000, background b=20, expected pixel signal is

μ_j(c)=b+F[Φ((j+0.5−c)/σ)−Φ((j−0.5−c)/σ)].

Add independent Gaussian read noise of SD 2 per pixel. `optics.derivative` differentiates this CDF difference; `fit_center` minimizes sum_j (data_j−μ_j(c))²/2² with known photometry and σ. Bounds ±6 px reject edge failures. Flux and finite-difference derivative tests validate this forward model independently of the optimizer.

Known motion is c(t)=c₀+vt, c₀=0.23 px, v=0.8 px/reference second. The event is at reference time zero; exposure delay τ=0.12 s yields c=0.326 px. Optical time is t_hat=(c_hat−c₀)/v. This is an instantaneous exposure model.

## Rotating noise without changing marginal covariance

Two already synchronized timestamp channels both measure zero, with error e_k=s Qθ x_k, s=0.02 s. Independent stationary modes obey

x_k,j=ρ_j x_(k−1),j+sqrt(1−ρ_j²) z_k,j,

with x_0,j standard normal and ρ=(0,0.85). Qθ is a 2-D rotation. Therefore

C=E[e_k e_kᵀ]=s² I,
Γ_h=s² Qθ diag(ρ_j^h) Qθᵀ.

The whitened lag Hθ=Γ₁/s² has eigenvalues (0,0.85) at every angle. Its directions change. This is a physical change in noise mixing with fixed channel labels, unlike a common coordinate transformation of both old and pilot data.

Center each sequence, whiten with the **known common** s, and form

H_hat=(Σ_(k=0)^(n−2) y_k y_(k+1)ᵀ + transpose)/(2n).

Centering and normalization cause finite-sample bias; calibrate this exact procedure. Define the spectrum score as max absolute difference of sorted eigenvalues, and matrix score as ||H_hat,pilot−H_hat,old||_F. Common orthogonal coordinate changes preserve both scores. Arbitrary affine changes require transforming C and using common C whitening; the code only tests orthogonal controls for C=s²I. No general affine-invariance claim is made for dividing arbitrary coordinates by s.

In the population, the matrix score equals √2(0.85)|sin θ|, whereas the spectrum score is zero. A fixed rotation of an isotropic-noise sequence preserves its sample eigenvalues exactly; an independent pilot has new random sample eigenvalues, whose distribution remains the same at every angle. There is no exact per-pair equality claim for independent data.

## Independent finite-sample thresholds

For N=999 training null pairs, rank k=ceil((N+1)(1−0.05))=950 (one-based) defines each threshold. Alarm if score > threshold. For an independent exchangeable null pair, P(alarm)≤(N+1−k)/(N+1)=0.05, marginalizing over training randomness (ties only make strict comparison more conservative). This does not guarantee ≤5% conditional on a particular trained threshold. Training, held-out pilots, final camera and final clocks have separate RNG streams.

## From alarm to optical-delay risk

For m=32 final timestamp repeats, exact mean covariance is

Vθ=(s²/m²) Qθ diag[m+2 Σ_(h=1)^(m−1)(m−h)ρ_j^h] Qθᵀ.

This follows by counting each lag h twice in the double covariance sum. Tests compare to the full double sum and independent Monte Carlo. Minimum-variance unbiased common-time fusion uses

wθ=Vθ⁻¹1/(1ᵀVθ⁻¹1), with 1ᵀwθ=1.

Negative weights are allowed; this is unconstrained GLS. Delay estimate is τ_hat=t_hat−wᵀ mean(e). Old weights assume 0°; both alarm policies switch to **60°** weights, even at 30° or 90°. The oracle knows θ. Conditional clock variance is wᵀVθw. Camera-time error is independent and shared across paired policies; it adds variance and any center-fitting bias to total MSE.

`exact_clock_rmse_ms` averages wᵀVθw over the realized alarm decisions, then takes its square root. It excludes camera noise and is not the total analytical MSE. Measured RMSE includes the actual nonlinear fit. For paired policy comparison, d_i=error_matrix²−error_spectrum²; report mean(d) ± 2 SD(d)/sqrt(800), in ms². This is a descriptive two-MCSE interval, not an exact coverage guarantee. A more sensitive detector can harm risk when its assumed corrective model is wrong.
