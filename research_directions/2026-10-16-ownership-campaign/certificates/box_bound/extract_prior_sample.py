from pathlib import Path
import sys,json
sys.path.insert(0,'/private/tmp/coopgpt-ownership-20261016/mixed')
src=Path('/private/tmp/coopgpt-ownership-20261016/mixed/verify_owner_boxes.py').read_text()
src=src.replace("if v['F']>0:max_ratio=max(max_ratio,sum(R)/v['F']);max_gap=max(max_gap,(sum(floor)-sum(R))/v['F'])", "if v['F']>0:\n            if sum(R)/v['F']>max_ratio:\n                Path(OUT).write_text(json.dumps({'rows':rows,'v':v,'R':R,'ratio':sum(R)/v['F']},indent=2))\n            max_ratio=max(max_ratio,sum(R)/v['F']);max_gap=max(max_gap,(sum(floor)-sum(R))/v['F'])")
exec(compile(src,'audited_source_instrumented_for_best_profile','exec'),{'__name__':'__main__','Path':Path,'OUT':str(Path(__file__).parent/'prior-worst-profile.json')})
