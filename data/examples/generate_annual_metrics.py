#!/usr/bin/env python3
"""Generate annual metrics one at a time - more stable than notebook."""

import sys
from pathlib import Path
import yaml
import time

sys.path.append(str(Path(__file__).parent.parent / 'src'))
from process_daily_data import ClimateDataProcessor

# Load config
config_path = Path(__file__).parent.parent / 'config.yml'
with open(config_path) as f:
    config = yaml.safe_load(f)

processor = ClimateDataProcessor(config, ensemble_member=1)
base_path = Path(config['chess_scape_netcdf_location'])

def file_exists(rcp, bias_corrected, metric):
    """Check if a metric file already exists."""
    bias_suffix = '_bias-corrected' if bias_corrected else ''
    filename = f'chess-scape_rcp{rcp}{bias_suffix}_01_{metric}_uk_1km_annual_19801201-20801130.nc'
    path = base_path / f'data/rcp{rcp}{bias_suffix}/01/annual' / filename
    return path.exists()

# Process annual season, one metric at a time
metrics = [
    ('tropical_nights', True, False, False, False, False),
    ('hot_days', False, True, False, False, False),
    ('heavy_rain', False, False, True, False, False),
    ('dry_days', False, False, False, True, False),
    ('windy_days', False, False, False, False, True),
]

print("Generating annual metrics one at a time...")
print("=" * 60)

# Check what's missing
total_combos = len(metrics) * 2 * 2  # metrics × 2 RCPs × 2 bias options
missing_count = 0
for metric_name, trop, hot, rain, dry, wind in metrics:
    for rcp in [60, 85]:
        for bias in [True, False]:
            if not file_exists(rcp, bias, metric_name):
                missing_count += 1

print(f"Missing {missing_count}/{total_combos} combinations")
print()

for metric_name, trop, hot, rain, dry, wind in metrics:
    print(f"\n{metric_name.upper()}")
    print("-" * 60)
    
    for rcp in [60, 85]:
        for bias in [True, False]:
            bias_label = 'bias' if bias else 'non-bias'
            
            if file_exists(rcp, bias, metric_name):
                print(f"  SKIP: RCP{rcp} {bias_label} (already exists)")
                continue
            
            print(f"  Generating: RCP{rcp} {bias_label}...", end=' ', flush=True)
            start = time.time()
            
            try:
                processor.generate_data(
                    quantiles_config={},
                    tropical_nights_enabled=trop,
                    hot_days_enabled=hot,
                    heavy_rain_enabled=rain,
                    dry_days_enabled=dry,
                    windy_days_enabled=wind,
                    seasons=['annual'],
                    rcps=[rcp],
                    bias_options=[bias],
                )
                elapsed = (time.time() - start) / 60
                print(f"✓ ({elapsed:.1f} min)")
            except Exception as e:
                print(f"✗ FAILED")
                print(f"    Error: {str(e)[:80]}")
                # Continue with next combination instead of stopping

print("\n" + "=" * 60)
print("All annual metrics complete!")
