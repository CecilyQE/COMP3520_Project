import pandas as pd
import os

run_id = "20260326T121152Z"
norm_file = f"artifacts/runs/{run_id}/normalized_outputs.csv"
alias_file = "data/aliases/default_aliases.csv"

if os.path.exists(norm_file):
    df = pd.read_csv(norm_file)
    # Extract entries where parsed_answer was found
    mask = df['parsed_answer'].notna()
    subset = df[mask][['panel_id', 'item_id', 'parsed_answer']].copy()
    subset.columns = ['panel_id', 'item_id', 'surface_form']
    subset['canonical_answer'] = subset['surface_form'] # Default: surface form = canonical
    subset['notes'] = "auto-generated"
    
    # Save to aliases
    subset.to_csv(alias_file, index=False)
    print(f"Generated {len(subset)} alias entries into {alias_file}")
else:
    print(f"Error: {norm_file} not found")
