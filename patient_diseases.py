import pandas as pd

# Load the full elderly conditions with names
df = pd.read_csv('output/elderly_conditions_with_names.csv')

# Filter to patient 115967185
patient_data = df[df['person_id'] == 115967185]

print(f"Patient 115967185 Analysis")
print("="*80)
print(f"Total condition records: {len(patient_data)}")
print(f"Unique diseases: {patient_data['condition_concept_id'].nunique()}")
print(f"Age range: {patient_data['age_at_event'].min():.1f} - {patient_data['age_at_event'].max():.1f} years")
print(f"Date range: {patient_data['condition_start_DATE'].min()} to {patient_data['condition_start_DATE'].max()}")
print("\n" + "="*80)
print("All 134 Unique Diseases:")
print("="*80)

# Get unique diseases with their frequency
disease_summary = patient_data.groupby(['condition_concept_id', 'concept_name']).size().reset_index(name='count')
disease_summary = disease_summary.sort_values('count', ascending=False)

for idx, row in disease_summary.iterrows():
    disease_name = row['concept_name'] if pd.notna(row['concept_name']) else f"Unknown (ID: {row['condition_concept_id']})"
    print(f"{idx+1:3d}. {disease_name:70s} ({row['count']:3d} times)")
