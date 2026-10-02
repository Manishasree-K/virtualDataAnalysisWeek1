"""E-Governance Digital Services - Sample Dataset + Cleaning Demo
Week 1 | Run: python egovernance_data_cleaning.py
Outputs: sample_egov_services.csv, cleaned_egov_services.csv, cleaning_report.txt
"""
import pandas as pd
import numpy as np
import os

BASE = os.path.dirname(os.path.abspath(__file__))
np.random.seed(42)
N = 500
services = ['Aadhaar Update', 'Passport Application', 'Tax Filing (ITR)',
    'Voter ID Registration', 'Driving Licence', 'Birth Certificate',
    'Pension Scheme', 'Ration Card']
channels = ['Portal', 'Mobile App', 'CSC Center', 'Kiosk', None]
districts = ['Lucknow', 'Patna', 'Jaipur', 'Bhopal', 'lucknow ', 'PATNA', None]
statuses = ['Completed', 'completed', 'COMPLETED', 'Pending', 'Failed',
    ' In Progress ']
df = pd.DataFrame({
    'application_id': [f'EGOV-{1000+i}' for i in range(N)],
    'service_name': np.random.choice(services, N),
    'applicant_age': np.random.randint(15, 85, N).astype(float),
    'district': np.random.choice(districts, N),
    'channel': np.random.choice(channels, N),
    'status': np.random.choice(statuses, N),
    'processing_time_days': np.random.exponential(scale=6, size=N).round(1),
    'satisfaction_score': np.random.choice([1,2,3,4,5,np.nan], N,
        p=[0.08,0.12,0.22,0.30,0.20,0.08]),
    'submission_date': pd.date_range('2024-01-01', periods=N, freq='D'
        ).strftime('%Y-%m-%d').tolist(),
})
# Inject data-quality issues deliberately (demo)
idx = np.random.choice(N, 25, replace=False)
df.loc[idx[:7], 'applicant_age'] = [5, 120, -3, 200, 12, 150, 8]
df.loc[idx[8:15], 'processing_time_days'] = [120, 250, -5, 300, 150, 200, 180]
df.loc[idx[15:20], 'service_name'] = ['aadhaar update', 'PASSPORT application',
    'tax filing (itr)', ' voter id registration', 'driving licence']
df_raw = pd.concat([df, df.iloc[:10].copy()], ignore_index=True)
bad = ['01/15/2024', '15-01-2024', '2024.02.30', 'not-a-date', '2024-13-01']
df_raw.loc[np.random.choice(len(df_raw), 20, replace=False),
    'submission_date'] = bad * 4
raw_path = os.path.join(BASE, 'sample_egov_services.csv')
df_raw.to_csv(raw_path, index=False)
print(f'[1/5] Raw dataset saved: {raw_path} ({len(df_raw)} rows)')

# ---------- CLEANING PIPELINE ----------
report = []
report.append(f'RAW shape: {df_raw.shape}')
report.append(f'RAW missing:\n{df_raw.isnull().sum().to_string()}')
report.append(f'RAW duplicates: {df_raw.duplicated().sum()}')
clean = df_raw.copy()

# 1. Standardise text
for col in ['service_name', 'district', 'channel', 'status']:
    clean[col] = clean[col].astype('string').str.strip().str.title()
svc_map = {'Tax Filing (Itr)': 'Tax Filing (ITR)',
    'Voter Id Registration': 'Voter ID Registration',
    'Passport Application': 'Passport Application'}
clean['service_name'] = clean['service_name'].replace(svc_map)

# 2. Duplicates
b4 = len(clean)
clean = clean.drop_duplicates(
    subset=['application_id', 'service_name', 'submission_date'])
report.append(f'Duplicates removed: {b4 - len(clean)}')

# 3. Age: valid range 18-100, else median impute
clean['applicant_age'] = pd.to_numeric(clean['applicant_age'], errors='coerce')
n_bad_age = ((clean['applicant_age'] < 18) |
    (clean['applicant_age'] > 100)).sum()
clean.loc[(clean['applicant_age'] < 18) |
    (clean['applicant_age'] > 100), 'applicant_age'] = np.nan
med_age = clean['applicant_age'].median()
clean['applicant_age'] = clean['applicant_age'].fillna(med_age).astype(int)
report.append(f'Invalid ages fixed via median {med_age:.0f}: {n_bad_age}')

# 4. Processing time: negative -> median; >60 capped at p99
clean['processing_time_days'] = pd.to_numeric(
    clean['processing_time_days'], errors='coerce')
n_out = ((clean['processing_time_days'] < 0) |
    (clean['processing_time_days'] > 60)).sum()
clean.loc[clean['processing_time_days'] < 0,
    'processing_time_days'] = np.nan
cap = clean['processing_time_days'].quantile(0.99)
clean.loc[clean['processing_time_days'] > 60,
    'processing_time_days'] = round(float(cap), 1)
clean['processing_time_days'] = clean['processing_time_days'].fillna(
    clean['processing_time_days'].median()).round(1)
report.append(f'Time outliers handled (cap p99={float(cap):.1f}): {n_out}')

# 5. Satisfaction: service-wise median impute
clean['satisfaction_score'] = pd.to_numeric(
    clean['satisfaction_score'], errors='coerce')
clean['satisfaction_score'] = clean['satisfaction_score'].fillna(
    clean.groupby('service_name')['satisfaction_score'].transform('median'))
clean['satisfaction_score'] = clean['satisfaction_score'].fillna(
    clean['satisfaction_score'].median()).round(0).astype(int)
report.append('Missing satisfaction imputed (service-wise median).')

# 6. Dates multi-format
clean['submission_date'] = pd.to_datetime(
    clean['submission_date'], errors='coerce', format='mixed')
n_bad_dt = int(clean['submission_date'].isnull().sum())
clean['submission_date'] = clean['submission_date'].fillna(
    pd.to_datetime('2024-06-15'))
report.append(f'Bad dates coerced/filled: {n_bad_dt}')

# 7. Categorical nulls
for col in ['district', 'channel']:
    clean[col] = clean[col].fillna('Unknown')

report.append(f'CLEANED shape: {clean.shape}')
report.append(f'CLEANED nulls total: {int(clean.isnull().sum().sum())}')
report.append('Stats:\n' + clean[
    ['applicant_age', 'processing_time_days',
     'satisfaction_score']].describe().round(2).to_string())
clean.to_csv(os.path.join(BASE, 'cleaned_egov_services.csv'), index=False)
open(os.path.join(BASE, 'cleaning_report.txt'), 'w',
    encoding='utf-8').write('\n'.join(report))
print('\n'.join(report))
print('[5/5] cleaned_egov_services.csv + cleaning_report.txt saved.')
