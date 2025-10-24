# Network Analysis Summary - Elderly 75+ Cohort

## Cohort Overview
- **Age threshold:** 75+ years
- **Patients:** 342
- **Condition events:** 100,482
- **Unique diseases:** 2,665
- **Mean age:** 79.6 ± 3.3 years
- **Age range:** 75.0 - 89.0 years

## Disease Co-occurrence Network

### Network Structure
- **Nodes (diseases):** 2,665 total → 1,517 in main component
- **Edges (co-occurrences):** 98,768
- **Density:** 0.0278 (2.78% of possible edges exist)
- **Average degree:** 130.21 (each disease co-occurs with ~130 other diseases)
- **Clustering coefficient:** 0.8292 (highly clustered - diseases form tight groups)

### Top 10 Hub Diseases (Most Connected)
1. **Essential hypertension** - Degree: 1,381 (connects to 91% of diseases!)
2. **Electrocardiogram abnormal** - Degree: 1,316
3. **Hyperlipidemia** - Degree: 1,300
4. **Dyspnea** - Degree: 1,047
5. **Abnormal findings on diagnostic imaging of lung** - Degree: 1,028
6. **Anemia** - Degree: 962
7. **Cardiomegaly** - Degree: 956
8. **Chest pain** - Degree: 950
9. **Acute renal failure syndrome** - Degree: 940
10. **Pleural effusion** - Degree: 938

## Community Detection Results

### Overview
- **Number of communities:** 5
- **Modularity:** 0.1153 (indicates good community structure)
- **Algorithm:** Louvain method (optimizes modularity)

### Community Breakdown

**Community 0 (459 diseases) - "Chronic Metabolic & Pain"**
- Essential hypertension
- Hyperlipidemia
- Type 2 diabetes mellitus
- Chronic pain, Low back pain
- Gastroesophageal reflux disease
- Fatigue, Dizziness

**Community 4 (352 diseases) - "Acute Cardiac & Renal"**
- Electrocardiogram abnormal
- Anemia
- Acute renal failure syndrome
- Pleural effusion
- Atrial fibrillation
- Cardiac arrhythmia
- Urinary tract infections

**Community 3 (302 diseases) - "Heart Failure & Post-op"**
- Cardiomegaly
- Congestive heart failure
- Atherosclerosis of coronary artery
- Postoperative state
- Chronic kidney disease stage 3
- Old myocardial infarction

**Community 1 (212 diseases) - "GI & Systemic Symptoms"**
- Constipation
- Tachycardia
- Atelectasis
- Hyponatremia
- Abdominal pain
- Iron deficiency anemia
- Nausea and vomiting

**Community 2 (192 diseases) - "Respiratory & Infections"**
- Dyspnea
- Abnormal findings on diagnostic imaging of lung
- Chest pain
- Cough
- Pneumonia
- Inflammatory dermatosis

## Key Insights

1. **Cardiovascular dominance:** The three largest disease hubs are all cardiovascular-related (hypertension, ECG abnormal, hyperlipidemia)

2. **High interconnectivity:** With an average degree of 130, diseases in elderly patients rarely occur in isolation

3. **Clear disease clusters:** 5 distinct communities suggest different physiological systems/disease patterns

4. **Chronic vs acute separation:** Community 0 captures chronic conditions while Community 4 captures acute events

5. **Comorbidity patterns:** The high clustering coefficient (0.83) shows diseases tend to co-occur in tight groups, not randomly

## Output Files Created

### In `output_elderly_75plus/`
1. `disease_prevalence_elderly.csv` - Disease frequency rankings
2. `elderly_75plus_conditions_with_names.csv` - Full dataset
3. `patient_disease_summary.csv` - Patient-level statistics

### In `network_analysis/elderly_75plus/`
1. `disease_network_full.pkl` - Full network (Python pickle)
2. `disease_network_main.pkl` - Main component (Python pickle)
3. `disease_network_main.graphml` - For Gephi/Cytoscape
4. `disease_cooccurrence_edges.csv` - Edge list with weights
5. `disease_network_nodes.csv` - Node list with metrics
6. `diseases_with_communities.csv` - All diseases with community assignments
7. `community_summary.csv` - Statistics for each community
8. `community_analysis.csv` - Top diseases in each community
9. `disease_network_communities.png` - Network visualization
10. `community_network.png` - Community-level view

## Next Steps for Report

1. Interpret what each community represents clinically
2. Discuss why hypertension is the central hub
3. Analyze disease progression patterns within communities
4. Compare findings to published epidemiology literature
5. Discuss implications for clinical care coordination
