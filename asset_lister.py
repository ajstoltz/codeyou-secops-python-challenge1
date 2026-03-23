#!/usr/bin/env python3
import csv
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional


# TODO: Is the path typehint correct??
def load_assets(path: Path) -> List[Dict[str, Any]]: # TODO: Is the type hint on the return actually correct?
    rows = []
    if not path.exists():
        print(f"Error: {path} not found.")
        return []

    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            r = {k: (v.strip() if isinstance(v, str) else v) for k, v in r.items()}
            # normalize tags to a list of lowercase tokens
            raw_tags = r.get("tags") or ""
            r["tags"] = [t.strip().lower() for t in raw_tags.split(",") if t.strip()]
            r["criticality"] = r.get("criticality", "").strip().lower()
            rows.append(r)
    return rows

# TODO: Perfectionist - Add type hints for the parameters
def filter_assets(
    rows: List[Dict[str, Any]], 
    owner: Optional[str] = None, 
    tag: Optional[str] = None, 
    critical_only: bool = False,
    high_only: bool = False
) -> List[Dict[str, Any]]: # TODO: Make sure we can successfully pass high_only boolean
    
    def match(r: Dict[str, Any]) -> bool:
        if critical_only and r.get("criticality") != "critical":
            return False        
        if high_only and r.get("criticality") != "high":
            return False
        if owner and r.get("owner", "").lower() != owner.lower():
            return False    
        if tag and tag.lower() not in r.get("tags", []):
            return False  
        
        return True
    
    return [r for r in rows if match(r)]


def main():
    ap = argparse.ArgumentParser(description="Filter assets from CSV and export to JSON.")
    ap.add_argument("--owner", help="Filter by owner (exact match)")
    ap.add_argument("--tag", help="Filter by tag (lowercase after normalization)")
    ap.add_argument("--critical-only", action="store_true", help="Only include critical assets")
    # TODO: Add another argument for the user to input `--high-only`. This should pass the string `store_true` to action parameter similar to the critical-only argument 
    ap.add_argument("--high-only", action="store_true", help="Only include 'high' criticality assets")
    ap.add_argument("--infile", default="asset_inventory_list.csv", help="Input CSV") # TODO: Fix this to reference the actual asset_inventory_list.csv
    ap.add_argument("--outfile", default="critical_assets.json", help="Output JSON")
    args = ap.parse_args()

    rows = load_assets(Path(args.infile))
    out = filter_assets(
        rows, 
        owner=args.owner, 
        tag=args.tag, 
        critical_only=args.critical_only, 
        high_only=args.high_only
    ) 
    # TODO: You should already have `--high-only` done, how do we pass it to the `filter_assets()`??
    
    Path(args.outfile).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {len(out)} assets to {args.outfile}")


# TODO: BONUS!!!!
# If you've completed all the TODOs up to this point then you are encouraged to add more functionality to this script including the following:

# - Ensure that a user can pass in the `--tag` to filter results by tag

# - Ensure that a user can filter by hostname in a similar way as you have filtered by owner and tag

# - (HARD) Ensure that your script can actually reach the real API for grabbing the asset inventory list in realtime rather than referencing a downloaded file such as `asset_inventory_list.csv`
    # - NOTE: There are instructions in a relevant README for how to accomplish reaching the API if you are interested

# - (HARD) Add an optional argument for the user so that they can display the data in a Table format instead of JSON. The script should still default to JSON
    # - NOTE: Instructions for accomplishing this are in a readme file within the `/docs` directory

if __name__ == "__main__":
    main()
