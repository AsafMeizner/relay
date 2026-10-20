from pathlib import Path
import json
from demo_video import storyboard, record, openscreen, mix, check
out=Path('/workspace/relay/demo/video')
board=storyboard.load(Path('/workspace/relay/demo/storyboard.yaml'))
take=record.Take.load(out/'take.json')
# Existing screen recording is unchanged. All zoom instructions are removed.
take.zooms=[]
take.warnings=[]
offsets=record.beat_offsets(take)
hidden=[]
for i,beat in enumerate(board.beats):
    if beat.card:
        end=take.beats[i+1] if i+1<len(take.beats) else take.ended_ms
        hidden.append((take.beats[i]-take.started_ms,end-take.started_ms))
display=record.start_display(':99',take.size)
try:
    result=openscreen.polish(board,take,out/'take.mp4',out/'polished.mp4',display=':99',work=out,frames_at=[round(t+1.5,2) for t in offsets],cards=[(a/1000,b/1000) for a,b in hidden])
finally:
    display.terminate()
final=mix.mux(out/'polished.mp4',out/'soundtrack.wav',out/'final.mp4')
summary=check.inspect(final,out,max_seconds=board.max_seconds,warnings=result['warnings'])
(out/'report.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary),flush=True)
