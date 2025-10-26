import pandas as pd
import os

# Configuration
AGE_THRESHOLD = 75
COHORT_NAME = 'elderly_75plus'
OUTPUT_DIR = f"output_{COHORT_NAME}"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load data
person_df = pd.read_csv('EHRShot_sampled_2000patients/sampled_person.csv')
condition_df = pd.read_csv('EHRShot_sampled_2000patients/sampled_condition_occurrence.csv', low_memory=False)
concept_df = pd.read_csv('EHRShot_sampled_2000patients/concept.csv', low_memory=False)

# Create birthdate (coerce errors to handle missing values)
person_df['birthdate'] = pd.to_datetime(
    person_df[['year_of_birth', 'month_of_birth', 'day_of_birth']].rename(
        columns={'year_of_birth': 'year', 'month_of_birth': 'month', 'day_of_birth': 'day'}
    )
)

# Merge and calculate age at event
merged_df = condition_df.merge(
    person_df[['person_id', 'birthdate', 'gender_concept_id', 'race_concept_id']], 
    on='person_id'
)
merged_df['condition_start_DATE'] = pd.to_datetime(merged_df['condition_start_DATE'])
merged_df['age_at_event'] = (merged_df['condition_start_DATE'] - merged_df['birthdate']).dt.days / 365

# Filter to elderly cohort
elderly_df = merged_df[merged_df['age_at_event'] >= AGE_THRESHOLD].copy()

print(f"Statistics:")
print(f"Condition events: {len(elderly_df):,}")
print(f"Unique patients: {elderly_df['person_id'].nunique()}")
print(f"Age range: {elderly_df['age_at_event'].min():.1f} - {elderly_df['age_at_event'].max():.1f} years")
print()
# Map condition IDs to disease names
condition_concepts = concept_df[
    (concept_df['domain_id'] == 'Condition') & 
    (concept_df['standard_concept'] == 'S')
][['concept_id', 'concept_name', 'concept_class_id', 'vocabulary_id']]

elderly_with_names = elderly_df.merge(
    condition_concepts,
    left_on='condition_concept_id',
    right_on='concept_id',
    how='left'
)

# Analyze disease prevalence
disease_counts = elderly_with_names.groupby(['condition_concept_id', 'concept_name']).agg({
    'person_id': 'nunique',
    'condition_occurrence_id': 'count'
}).reset_index()
disease_counts.columns = ['condition_concept_id', 'disease_name', 'num_patients', 'num_occurrences']
disease_counts = disease_counts.sort_values('num_patients', ascending=False)

print(f"Unique diseases: {len(disease_counts)}\n")
print(f"Top 10 Most Common Diseases:")

for idx, row in disease_counts.head(10).iterrows():
    disease = row['disease_name'] 
    print(f"    {disease[:60]:60s} | {row['num_patients']:4d} pts | {row['num_occurrences']:5d} events")

# Patient-disease summary
patient_disease_summary = elderly_with_names.groupby('person_id').agg({
    'condition_concept_id': 'nunique',
    'condition_occurrence_id': 'count'
}).reset_index()
patient_disease_summary.columns = ['person_id', 'num_unique_diseases', 'num_total_events']

# Save output files
disease_counts.to_csv(os.path.join(OUTPUT_DIR, 'disease_prevalence_elderly.csv'), index=False)
elderly_with_names.to_csv(os.path.join(OUTPUT_DIR, f'{COHORT_NAME}_conditions_with_names.csv'), index=False)
patient_disease_summary.to_csv(os.path.join(OUTPUT_DIR, 'patient_disease_summary.csv'), index=False)

print(f"Output files saved to: {OUTPUT_DIR}/")

if __name__ == '__main__':
    pass 
