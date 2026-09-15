"""Fixed-model leave-one-thickness-out diagnostic; no hyperparameter tuning."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

folder = Path(__file__).resolve().parents[1] / 'results'
data = pd.read_csv(folder / 'ml_data.csv')
features = ['layer thickness', 'Sigma_a_left', 'Sigma_s_left', 'Sigma_T_left',
            'Sigma_a_right', 'Sigma_s_right', 'Sigma_T_right']
thicknesses = sorted(data['layer thickness'].unique())
if len(data) != 24 or data.duplicated(['layer thickness', 'left slab', 'right slab']).any():
    raise ValueError('Unexpected configuration grid')
rows = []
for thickness in thicknesses:
    train = data[data['layer thickness'] != thickness]
    test = data[data['layer thickness'] == thickness]
    mode = 'endpoint extrapolation' if thickness in (thicknesses[0], thicknesses[-1]) else 'interior interpolation'
    rf = RandomForestRegressor(n_estimators=200, max_depth=5, random_state=1)
    rf.fit(train[features], train['T mean'])
    pred = rf.predict(test[features])
    for (_, row), rf_pred in zip(test.iterrows(), pred):
        pair = train[(train['left slab'] == row['left slab']) &
                     (train['right slab'] == row['right slab'])].sort_values('layer thickness')
        x = pair['layer thickness'].to_numpy()
        y = pair['T mean'].to_numpy()
        # np.interp uses nearest endpoint outside training range: label explicitly.
        predictions = {'random_forest': float(rf_pred),
                       'training_mean': float(train['T mean'].mean()),
                       'pair_linear_interpolation_endpoint_clamp': float(np.interp(thickness, x, y))}
        for model, value in predictions.items():
            rows.append({'held_out_thickness': thickness, 'mode': mode,
                         'left': row['left slab'], 'right': row['right slab'],
                         'model': model, 'target': row['T mean'], 'prediction': value,
                         'absolute_error': abs(value-row['T mean'])})
result = pd.DataFrame(rows)
result.to_csv(folder / 'thickness_predictions.csv', index=False)
summary = result.groupby(['mode', 'model']).agg(
    mae=('absolute_error', 'mean'), max_error=('absolute_error', 'max'),
    count=('absolute_error', 'size')).reset_index()
summary.to_csv(folder / 'thickness_summary.csv', index=False)
print(summary.to_string(index=False))
# Compare independent repeated means using standard errors; diagnostic, not a CI.
w = pd.read_csv(folder / 'woodcock_same.csv')
s = pd.read_csv(folder / 'single_10.csv')
checks = []
for _, a in w.iterrows():
    b = s[s['material'] == a['left slab']].iloc[0]
    for outcome in ['A', 'R', 'T']:
        se = np.sqrt(a[f'{outcome} std']**2/10 + b[f'{outcome} std']**2/10)
        diff = a[f'{outcome} mean'] - b[f'{outcome} mean']
        checks.append({'material': a['left slab'], 'outcome': outcome,
                       'difference': diff, 'combined_standard_error': se,
                       'difference_over_se': diff/se if se else None})
pd.DataFrame(checks).to_csv(folder / 'mean_difference_diagnostic.csv', index=False)
print('Mean comparison diagnostics:', json.dumps(checks))
