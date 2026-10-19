# Mode rotation and optical-delay measurement

A 45–60 minute camera / optics / vision / mathematics lab. Can temporal noise change without changing its eigenvalues? Yes—and detecting that change does not tell you which correction is safe.

## Learn and run

Prerequisites: covariance matrices, eigenvalues, stationary AR(1) noise, Gaussian PSFs, basic Python. Learn to derive a pixel-integrated image, recover exposure delay from a moving spot, construct a direction-sensitive lag diagnostic, and distinguish alarm power from measurement risk.

```sh
git clone https://github.com/ahmetalpkilic/mode-rotation-optical-delay-learning-lab.git
cd mode-rotation-optical-delay-learning-lab
sh run_demo.sh
```

Python 3.9–3.12 with venv/pip and internet for the first dependency installation. The command installs pinned dependencies, runs tests, and writes `outputs/results.json` and `outputs/experiment.png`. No datasets or credentials needed. All images are synthetic. Fixed seeds make runs deterministic within the tested software environment; floating-point differences across platforms are possible. Committed `examples/` contains reference outputs.

Spend 10 minutes predicting results, 15 reading [MODEL.md](MODEL.md) alongside annotated `model.py` and `optics.py`, 10 running and inspecting outputs, and 15–25 modifying one experiment.

## Four-way connection

| Area | Concrete model | Connection to measurement |
|---|---|---|
| Optics | 550 nm light, Gaussian pupil amplitude, 16 mm focal length | Fourier transform gives a Gaussian focal PSF |
| Camera | 4 µm full-fill pixels, exact integration, 2-electron-equivalent read noise | Sampled noisy spot provides an exposure-time observation |
| Vision / metrology | Nonlinear subpixel center fit, known 0.8 px/s motion | Center becomes optical time; timestamp fusion yields delay |
| Mathematics | Rotated AR modes, symmetric lag moments, rank thresholds, GLS | Detect a spectrum-invisible change and evaluate delay MSE |

This is a deliberately smaller successor to [lag-spectrum optical timing](https://github.com/ahmetalpkilic/lag-spectrum-optical-timing-learning-lab). It replaces the predecessor's unknown affine clock calibration with two already synchronized timestamp channels measuring a common zero-time event. Known marginal covariance isolates orientation from scale estimation. No full covariance learner is built.

## Experiment and controls

Train two separate 5% alarm thresholds on 999 independent unchanged old/pilot pairs (96 samples per sequence). Evaluate 800 new pairs at each physical rotation: 0°, 30°, 60°, 90°. All scenarios preserve marginal covariance and population lag eigenvalues. Two policies either keep old fusion weights or switch to weights for a **known 60° alternative** when their alarm fires. The 30° and 90° cases deliberately violate that alternative. Both policies receive exactly the same pilot data, final 32 timestamp repeats, and final camera image. No final measurements enter the alarm.

Compare four delay estimators: always keep old weights; eigenvalue-triggered policy; matrix-triggered policy; oracle weights knowing the true angle. The oracle is a reference, not an implementable estimator. Alternative weights are supplied analytically, not obtained with free additional calibration data; this lesson does not price calibration or optimize a refresh budget.

Read [RESULTS.md](RESULTS.md) for reference numbers. A spectrum alarm can still fire on finite samples: “invisible” means unchanged population spectrum, not identical paired sample scores. The marginal null score distribution is rotation-invariant in this isotropic Gaussian example. The matrix detector responds to directions in fixed physical channel coordinates.

## Exercises

1. Derive the matrix population score at angle θ and show it equals √2 |ρ₂−ρ₁| |sin θ|. Verify at 0°, 30°, 60°, 90°.
2. Change both mode correlations to 0.4. Predict the loss of direction information and rerun calibration and evaluation.
3. Replace the assumed 60° alternative with 30°. Which scenarios improve and which become harmful? Keep the independent seed streams.
4. Double the read-noise SD (and retain its use in fitting). Separate camera-time variance from timestamp variance. Does better alarm detection still matter?
5. Add a non-isotropic known marginal C. Whiten both sequences using the **same** C and transform timestamp weights consistently. Explain why independently whitening each block can erase or confuse direction changes.

## Assumptions and limitations

Known optics, flux, background, motion, synchronization and marginal covariance; Gaussian stationary timing errors; independently reset calibration/pilot/final sequences; instantaneous exposure; no shot noise, saturation, quantization, rolling shutter, aberration, velocity error or real camera validation. Signal is electron-equivalent under an intentionally read-noise-only model, not a complete photon budget. Symmetric lag-one moments miss antisymmetric lead/lag and higher-lag changes. Results condition on one training set; MCSE excludes training variation. Separate 5% rank guarantees are marginal and require exchangeability, not joint, conditional or sequential guarantees. Synthetic numerical recovery and repeatability do **not** establish instrument accuracy.

## Sources and attribution

Original new timing diagnostic, experiment, tests and text are MIT. `optics.py` and the runner are reused from ahmetalpkilic's MIT predecessor at `b16a8a464672e1fd14dc38507d57f360a57d80e6`; the copyright notice is retained. NumPy (BSD-style), SciPy (BSD-3-Clause) and Matplotlib (its permissive license) are dependencies, not vendored implementations. Prysm (MIT) is a reviewed optical-model reference, not a runtime dependency. Current source commits, activity and public repository inventory are recorded in `sources.json`; license texts are retained in `provenance/`. API timestamps are recorded verbatim; any timestamp later than retrieval is not evidence of a future release.

Reviewed references: [prysm propagation](https://github.com/brandondube/prysm), [SciPy symmetric eigensolvers](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.eigh.html). This lab uses the analytic Gaussian Fourier special case rather than copying propagation code.
