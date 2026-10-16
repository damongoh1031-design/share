import json, glob, os, yaml

spec = yaml.safe_load(open('fields.yaml', encoding='utf-8'))
groups = {g['group']: [x['name'] for x in g['fields']] for g in spec['field_groups']}
declared = set(n for v in groups.values() for n in v)

files = sorted(glob.glob('results/*.json'))
print('items found:', len(files))
for p in files:
    name = os.path.basename(p)
    try:
        d = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        print('BAD JSON', name, e)
        continue
    unc = len(d.get('uncertain', []))
    if all(g in d for g in groups):
        print('%-46s grouped  groups=%d/6 uncertain=%d' % (name, sum(1 for g in groups if g in d), unc))
        continue
    targets = d.get('targets') or d.get('candidates')
    if isinstance(targets, list) and targets and isinstance(targets[0], dict):
        full = sum(1 for t in targets if all(f in t for f in declared))
        print('%-46s targets  full_field_targets=%d/%d uncertain=%d' % (name, full, len(targets), unc))
        continue
    present = [f for f in declared if f in d]
    print('%-46s flat     fields=%d/43 uncertain=%d' % (name, len(present), unc))
