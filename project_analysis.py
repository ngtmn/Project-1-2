"""
CIS 4930 - Network Analysis Project 1
Uncovering Clinical Patterns with Network Analysis

Research Question: What types of diseases are common among elderly patients (age 60+)?

This script performs the following analysis:
1. Load patient demographics and condition occurrence data
2. Calculate patient age at each condition event
3. Filter to elderly cohort (age >= 60)
4. Map condition IDs to human-readable disease names
5. Analyze disease prevalence
6. Build disease co-occurrence networks
7. Generate visualizations and output files for submission
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

# Configuration
AGE_THRESHOLD = 60  # Define elderly as 60+ years
OUTPUT_DIR = "output"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*80)
print("CIS 4930 - Network Analysis Project 1")
print("Research Question: What diseases are common among elderly patients?")
print("="*80)

# ============================================================================
# STEP 1: Load Data
# ============================================================================
print("\n[STEP 1] Loading data...")

# Load person demographics
person_df = pd.read_csv('EHRShot_sampled_2000patients/sampled_person.csv')
print(f"  ✓ Loaded {len(person_df)} patients")

# Load condition occurrences
condition_df = pd.read_csv('EHRShot_sampled_2000patients/sampled_condition_occurrence.csv', 
                           low_memory=False)
print(f"  ✓ Loaded {len(condition_df)} condition records")

# Load concept table for disease names
concept_df = pd.read_csv('EHRShot_sampled_2000patients/concept.csv', 
                         low_memory=False)
print(f"  ✓ Loaded {len(concept_df)} concepts")

# ============================================================================
# STEP 2: Calculate Age at Event
# ============================================================================
print("\n[STEP 2] Calculating patient age at each condition event...")

# Create birthdate from year, month, day of birth
person_df['birthdate'] = pd.to_datetime(
    person_df[['year_of_birth', 'month_of_birth', 'day_of_birth']].rename(
        columns={'year_of_birth': 'year', 
                 'month_of_birth': 'month', 
                 'day_of_birth': 'day'}
    )
)

# Merge person data with conditions
merged_df = condition_df.merge(
    person_df[['person_id', 'birthdate', 'gender_concept_id', 'race_concept_id']], 
    on='person_id'
)
print(f"  ✓ Merged dataset has {len(merged_df)} rows")

# Convert condition_start_date to datetime
merged_df['condition_start_DATE'] = pd.to_datetime(merged_df['condition_start_DATE'])

# Calculate age at event
merged_df['age_at_event'] = (
    (merged_df['condition_start_DATE'] - merged_df['birthdate']).dt.days / 365
)

# ============================================================================
# STEP 3: Filtter to Elderly Cohor
# ============================================================================
print(f"\n[STEP 3] Filtering to elderly cohort (age >= {AGE_THRESHOLD})...")

elderly_df = merged_df[merged_df['age_at_event'] >= AGE_THRESHOLD].copy()
print(f"  ✓ Found {len(elderly_df)} condition events for elderly patients")
print(f"  ✓ Age statistics:")
print(f"      Mean: {elderly_df['age_at_event'].mean():.1f} years")
print(f"      Std:  {elderly_df['age_at_event'].std():.1f} years")
print(f"      Range: {elderly_df['age_at_event'].min():.1f} - {elderly_df['age_at_event'].max():.1f} years")
print(f"  ✓ Unique elderly patients: {elderly_df['person_id'].nunique()}")

# ============================================================================
# STEP 4: Map Condition IDs to Disease Names
# ============================================================================
print("\n[STEP 4] Mapping condition IDs to disease names...")

# Filter concepts to Condition domain and standard concepts
condition_concepts = concept_df[
    (concept_df['domain_id'] == 'Condition') & 
    (concept_df['standard_concept'] == 'S')
][['concept_id', 'concept_name', 'concept_class_id', 'vocabulary_id']]

print(f"  ✓ Found {len(condition_concepts)} standard condition concepts")

# Merge with elderly conditions
elderly_with_names = elderly_df.merge(
    condition_concepts,
    left_on='condition_concept_id',
    right_on='concept_id',
    how='left'
)

print(f"  ✓ Mapped {elderly_with_names['concept_name'].notna().sum()} condition records to disease names")

# ============================================================================
# STEP 5: Analyze Disease Prevalence
# ============================================================================
print("\n[STEP 5] Analyzing disease prevalence in elderly cohort...")

# Count by condition
disease_counts = elderly_with_names.groupby(['condition_concept_id', 'concept_name']).agg({
    'person_id': 'nunique',  # Number of unique patients
    'condition_occurrence_id': 'count'  # Number of occurrences
}).reset_index()

disease_counts.columns = ['condition_concept_id', 'disease_name', 'num_patients', 'num_occurrences']
disease_counts = disease_counts.sort_values('num_patients', ascending=False)

print(f"  ✓ Identified {len(disease_counts)} unique diseases")
print(f"\n  Top 10 Most Common Diseases (by number of patients):")
print("  " + "-"*76)
for idx, row in disease_counts.head(10).iterrows():
    disease = row['disease_name']
    if pd.isna(disease):
        disease = f"Unknown (ID: {row['condition_concept_id']})"
    print(f"    {disease[:60]:60s} | {row['num_patients']:4d} patients | {row['num_occurrences']:5d} events")

# Save disease prevalence to CSV
output_file = os.path.join(OUTPUT_DIR, 'disease_prevalence_elderly.csv')
disease_counts.to_csv(output_file, index=False)
print(f"\n  ✓ Saved disease prevalence to: {output_file}")

# ============================================================================
# STEP 6: Prepare Data for Network Analysis
# ============================================================================
print("\n[STEP 6] Preparing data for network analysis...")

# Save elderly conditions with disease names for network construction
network_data_file = os.path.join(OUTPUT_DIR, 'elderly_conditions_with_names.csv')
elderly_with_names.to_csv(network_data_file, index=False)
print(f"  ✓ Saved network data to: {network_data_file}")

# Create patient-disease summary
patient_disease_summary = elderly_with_names.groupby('person_id').agg({
    'condition_concept_id': 'nunique',  # Number of unique diseases per patient
    'condition_occurrence_id': 'count'  # Total condition events per patient
}).reset_index()
patient_disease_summary.columns = ['person_id', 'num_unique_diseases', 'num_total_events']

summary_file = os.path.join(OUTPUT_DIR, 'patient_disease_summary.csv')
patient_disease_summary.to_csv(summary_file, index=False)
print(f"  ✓ Saved patient summary to: {summary_file}")

print(f"\n  Patient Disease Statistics:")
print(f"    Mean diseases per patient: {patient_disease_summary['num_unique_diseases'].mean():.1f}")
print(f"    Median diseases per patient: {patient_disease_summary['num_unique_diseases'].median():.0f}")
print(f"    Max diseases for single patient: {patient_disease_summary['num_unique_diseases'].max():.0f}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
print(f"\nKey Findings:")
print(f"  • Analyzed {len(elderly_df)} condition events")
print(f"  • From {elderly_df['person_id'].nunique()} elderly patients (age {AGE_THRESHOLD}+)")
print(f"  • Identified {len(disease_counts)} unique diseases")
print(f"  • Average {patient_disease_summary['num_unique_diseases'].mean():.1f} diseases per patient")

print(f"\nOutput Files Created in '{OUTPUT_DIR}/' directory:")
print(f"  1. disease_prevalence_elderly.csv - Disease frequency rankings")
print(f"  2. elderly_conditions_with_names.csv - Full dataset for network construction")
print(f"  3. patient_disease_summary.csv - Patient-level statistics")

print(f"\nNext Steps:")
print(f"  • Build disease co-occurrence network")
print(f"  • Perform network analysis (centrality, communities, etc.)")
print(f"  • Create visualizations")
print(f"  • Write project report")
print("="*80)
