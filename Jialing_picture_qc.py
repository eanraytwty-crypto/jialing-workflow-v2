#!/usr/bin/env python3
"""Inspect picture-only intermediate MP4s. Technical QC does not prove narrative or visual quality."""
import json, subprocess, argparse, sys
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('videos', nargs='+')
parser.add_argument('--fps', default='24/1')
parser.add_argument('--width', type=int, default=864)
parser.add_argument('--height', type=int, default=480)
parser.add_argument('--max-duration', type=float, default=15)
args=parser.parse_args()
failed=False
for path in args.videos:
    try:
        cp=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',path], capture_output=True, text=True, check=True)
        j=json.loads(cp.stdout); streams=j['streams']; v=[s for s in streams if s['codec_type']=='video']; aud=[s for s in streams if s['codec_type']=='audio']
        if not v: raise ValueError('No video stream')
        s=v[0]; dur=float(j['format']['duration'])
        warnings=[]
        if aud: warnings.append('unexpected AUDIO stream')
        if (s.get('width'),s.get('height')) != (args.width,args.height):warnings.append('unexpected dimensions')
        if s.get('avg_frame_rate') != args.fps: warnings.append('unexpected fps')
        if dur<=0 or dur>args.max_duration: warnings.append('unexpected duration')
        decode=subprocess.run(['ffmpeg','-v','error','-i',path,'-map','0:v:0','-f','null','-'],capture_output=True,text=True)
        if decode.returncode != 0: warnings.append('decode failure')
        print(('FAIL' if warnings else 'PASS'),path,'; '.join(warnings) if warnings else 'technical media checks')
        failed |= bool(warnings)
    except Exception as e:
        print('FAIL',path,str(e));failed=True
sys.exit(1 if failed else 0)
