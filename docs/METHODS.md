# Model and validation

## Transport

Neutrons enter normally along +x. A homogeneous slab occupies 0 < x < L and is unbounded in y and z. The number density is rho N_A / M. Microscopic cross sections in barns are multiplied by 1e-24 and number density to obtain macroscopic cross sections in cm^-1.

Flights are sampled as s = -ln(u) / Sigma_T. At an internal collision, absorption occurs with probability Sigma_a / Sigma_T; otherwise the direction is resampled isotropically. Histories terminate by absorption, escape through the incident face (reflection), or escape through the far face (transmission). The trajectory plots include sampled flight endpoints outside the slab; they are not clipped at the escape surface.

For two equal-thickness layers, the Woodcock majorant is the larger total cross section. Candidate collisions are accepted with probability Sigma_T(local) / Sigma_majorant. Rejected collisions retain the previous direction. Identical adjacent layers provide a consistency comparison with a homogeneous slab of the same total thickness.

## Material inputs inherited from the notebook

| Material | Absorption / barn | Scattering / barn | Density / g cm^-3 | Molar mass / g mol^-1 |
|---|---:|---:|---:|---:|
| Water | 0.6652 | 103.0 | 1.00 | 18.0153 |
| Lead | 0.158 | 11.221 | 11.35 | 207.2 |
| Graphite | 0.0045 | 4.74 | 1.67 | 12.011 |

Water uses a molecular number density with the supplied molecular cross sections. The notebook does not supply an evaluated-data citation or an exact neutron energy for these constants; they are retained as model inputs, not independently verified reference data.

## Uncertainty and fits

- Columns labelled `std` are sample standard deviations across repeated runs (`ddof=1`). They describe run-to-run scatter, not the standard error of the reported mean.
- The identical-layer mean comparison uses sqrt(s_W²/n_W + s_S²/n_S). Its two-standard-error indicator is a descriptive diagnostic, not a formal confidence interval or proof of unbiasedness.
- The attenuation fit uses the original repeat standard deviations in a weighted log-linear fit. Its chi-squared is thus scaled by repeat scatter rather than mean standard errors. Effective attenuation lengths depend on the fitted range and do not imply an exact exponential law.
- Zero transmission or zero estimated uncertainty points are omitted from the log fit. This can bias a low-count tail; rare transmission requires more histories and a count-based treatment.
- The absorption-depth fit excludes empty and zero-scatter bins to avoid invalid logarithms or infinite weights.

## Reproduction checks

The runner executes the complete notebook in a fresh kernel, validates notebook structure, asserts probability bounds and A + R + T = 1 for exported transport tables, and checks the exponential sample mean within five theoretical standard errors. These checks complement the notebook's visual sampling diagnostics; they are not exhaustive transport verification.

The seed fixes the sequential NumPy random stream. Re-running individual cells or changing their order changes later draws. Exact results can also vary across dependency versions. Simulation sample sizes remain those in the original notebook: 10,000 histories per repeat and ten repeats for the main scans; 3,000 and three repeats for the surrogate dataset.

## Surrogate evaluation

The random forest retains 200 trees, depth five and random_state=1. The initial random split uses 16 training and eight test configurations. Leave-one-thickness-out analysis trains on five thicknesses and tests the remaining four material-pair configurations. Interior interpolation and endpoint extrapolation are reported separately. Baselines use training targets only.

The total cross-section features equal absorption plus scattering and are redundant. The targets contain Monte Carlo noise, with only three repeats per configuration. The evaluation establishes neither reliable new-material prediction nor a measured speed advantage. The holdout diagnostics were added after examining the initial evaluation and should be treated as exploratory.
