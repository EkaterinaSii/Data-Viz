# Blood Pressure Dashboard
An interactive data visualization dashboard for exploring global blood pressure patterns, hypertension prevalence, and related demographic or lifestyle factors.

The dashboard is built with **Python**, **Dash**, **Plotly**, and **Pandas**. It allows users to explore blood pressure data across countries, filter by population characteristics, and inspect country-specific health patterns.

## Dashboard Preview

### Global Overview
<img width="2048" height="1049" alt="image" src="https://github.com/user-attachments/assets/872c0824-c5b6-4cf3-a02a-41afdca9974e" />

### Country-Specific View
<img width="2048" height="1048" alt="image" src="https://github.com/user-attachments/assets/f5b5dad8-0470-4db1-8ab1-c5e14331a3e7" />

## Features

- Interactive global choropleth map
- Country selection by clicking on the map
- Sidebar filters for:
  - Year range
  - Sex
  - Age group
  - BMI category
  - Smoking status
  - Physical activity
  - Salt intake
  - Stress level
  - Diabetes
  - Family history of hypertension
- Active filter chips with removable filters
- Summary statistic cards with explanatory tooltips
- Top 5 countries by selected map metric
- Country-specific dashboard view
- Historical blood pressure chart with two modes:
  - Yearly average trend
  - Individual database records
- Blood pressure category distribution by age group
- Blood pressure category distribution by diabetes status

## Project Goal

High blood pressure is a major risk factor for serious health problems, including stroke, heart disease, and kidney damage.

This dashboard helps users explore:

- Hypertension prevalence
- Systolic and diastolic blood pressure
- Pulse pressure and heart rate
- BMI and age patterns
- Differences across lifestyle and demographic groups

The goal is to support better understanding of high-risk populations and provide useful visual insights for prevention, screening, lifestyle interventions, and public health decision-making.

## Tech Stack

- Python
- Dash
- Plotly
- Pandas
- HTML/CSS

## Project Structure

```text
.
├── app.py
├── callbacks.py
├── components.py
├── config.py
├── data.py
├── figures.py
├── layout.py
├── Blood_Pressure.csv
├── assets/
    ├── style.css
    ├── male-icon.png
    ├── female-icon.png
    ├── no-smoking-icon.png
    ├── smoking-status.png
    └── ex-smoker.png

```
## Installation
Clone the repository:

```text
git clone https://github.com/your-username/blood-pressure-dashboard.git
cd blood-pressure-dashboard
```
Create and activate a virtual environment:

```text
python3 -m venv venv
source venv/bin/activate
```
Install dependencies:

```text
pip install requirements.txt
```
Place it in the root project folder.
You can also use a custom CSV path by setting the environment variable:
```text
export BLOOD_PRESSURE_CSV="/path/to/your/Blood_Pressure.csv"
```
Then run the app normally.

## Expected Dataset Columns
The dashboard uses the following columns:
```text
Patient_ID
Year
Country
WHO_Region
Income_Level
ISO2_Country_Code
Age
Age_Group
Sex
BMI
BMI_Category
Smoking_Status
Physical_Activity
Diet_Salt_Intake
Stress_Level
Diabetes
Family_Hx_Hypertension
Systolic_BP_mmHg
Diastolic_BP_mmHg
Pulse_Pressure_mmHg
Mean_Arterial_Pressure
Heart_Rate_bpm
BP_Category
Country_HTN_Prevalence_pct
Age_Category
BP_Category_2
```
If some columns are missing, the app prints a warning and handles missing values safely where possible.

## Running the App
Start the dashboard:

```text
python3 app.py
```
Then open the app in your browser:
```text
http://127.0.0.1:8050/
```
## How to use

1. Use the sidebar filters to explore different population groups.
2. Change the map metric using the map metric dropdown.
3. Click a country on the map to open the country-specific view.
4. Use the Clear filters button to reset filters while staying in the current view.
5. Use Reset country selection to return to the global overview.
6. In the country view, switch the blood pressure trend chart between:
    * Yearly
    * By record

## Notes

This dashboard is intended for data exploration and visualization. It is not a medical diagnosis tool.

## Author
Made by Ekaterina Siikavirta


