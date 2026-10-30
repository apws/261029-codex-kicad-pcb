#!/usr/bin/env python3
"""Codex/KiCad local experiment harness. No network, router installation or GUI control.
Run with KiCad's Python (on this Linux host: /usr/bin/python3).
Every output directory must be new. Source projects are never saved in place.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write_json(p, obj):
    Path(p).write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')

def manifest(root):
    return {str(p.relative_to(root)): digest(p) for p in sorted(root.rglob('*'))
            if p.is_file() and '.git' not in p.relative_to(root).parts}

def fresh(p, outside=None):
    p = Path(p).resolve()
    if outside and (p == outside or outside in p.parents):
        raise ValueError('Output must be outside the input project directory')
    if p.exists():
        raise ValueError(f'Output already exists; choose a new path: {p}')
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def copy_project(src, dst):
    if not src.is_dir():
        raise ValueError('Source must be a directory containing the complete project')
    for p in src.rglob('*'):
        if '.git' in p.relative_to(src).parts:
            continue
        if p.is_symlink():
            raise ValueError(f'Project contains symlink {p.name}; make dependencies explicit before copying')
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('.git', '*.lck', '*.kicad_prl', '__pycache__'))

def pcb_api():
    try:
        import pcbnew
        return pcbnew
    except ImportError as e:
        raise RuntimeError('pcbnew unavailable: use KiCad Python, normally /usr/bin/python3 on Linux') from e

def board_path(value):
    p = Path(value).resolve()
    if p.suffix != '.kicad_pcb' or not p.is_file():
        raise ValueError('Expected an existing .kicad_pcb file')
    return p

def snapshot(board, pcb):
    xy = lambda p: [p.x, p.y]  # native integer nanometres
    footprints = []
    for fp in board.GetFootprints():
        pads = sorted([[p.GetNumber(), p.GetNetname(), xy(p.GetPosition()), xy(p.GetSize()),
                        xy(p.GetDrillSize()), int(p.GetShape()), str(p.GetLayerSet().FmtHex())]
                       for p in fp.Pads()], key=str)
        footprints.append({'ref': fp.GetReference(), 'library': str(fp.GetFPID().GetLibItemName()),
                           'position_nm': xy(fp.GetPosition()), 'angle': fp.GetOrientationDegrees(),
                           'layer': int(fp.GetLayer()), 'locked': fp.IsLocked(), 'pads': pads})
    tracks = []
    for t in board.GetTracks():
        tracks.append({'type': t.GetClass(), 'net': t.GetNetname(), 'start_nm': xy(t.GetStart()),
                       'end_nm': xy(t.GetEnd()), 'width_nm': t.GetWidth(t.GetLayer()) if t.GetClass() == 'PCB_VIA' else t.GetWidth(), 'layer': int(t.GetLayer()),
                       'locked': t.IsLocked(), 'drill_nm': t.GetDrillValue() if t.GetClass() == 'PCB_VIA' else None})
    return {'units': 'integer nanometres', 'footprints': sorted(footprints, key=lambda f: f['ref']),
            'tracks': sorted(tracks, key=lambda t: json.dumps(t, sort_keys=True)),
            'metrics': {'footprints': len(footprints), 'track_segments': sum(t['type'] != 'PCB_VIA' for t in tracks),
                        'vias': sum(t['type'] == 'PCB_VIA' for t in tracks), 'zones': len(list(board.Zones())),
                        'copper_layers': board.GetCopperLayerCount(),
                        'track_length_mm': sum(pcb.ToMM(t.GetLength()) for t in board.GetTracks() if t.GetClass() != 'PCB_VIA')}}

def run_logged(cmd, out, name):
    result = subprocess.run(cmd, capture_output=True, text=True)
    (out / (name + '.stdout.txt')).write_text(result.stdout)
    (out / (name + '.stderr.txt')).write_text(result.stderr)
    return {'command': cmd, 'exit_code': result.returncode}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='action', required=True)
    sub.add_parser('doctor', help='Report local tools; does not install anything')
    p = sub.add_parser('init', help='Copy complete source into a new experiment')
    p.add_argument('--source', required=True); p.add_argument('--dest', required=True)
    p = sub.add_parser('check', help='Native ERC/DRC, netlist/PDF exports and geometry snapshot')
    p.add_argument('--board', required=True); p.add_argument('--out', required=True)
    p = sub.add_parser('export-dsn', help='Export DSN through native pcbnew, without changing source')
    p.add_argument('--board', required=True); p.add_argument('--out', required=True)
    p = sub.add_parser('import-ses', help='Copy project and import routing into the new candidate')
    p.add_argument('--board', required=True); p.add_argument('--ses', required=True); p.add_argument('--dest', required=True)
    p = sub.add_parser('compare', help='Compare two geometry.json snapshots (not full electrical proof)')
    p.add_argument('before'); p.add_argument('after')
    a = ap.parse_args()
    if a.action == 'doctor':
        data = {'python': sys.executable, 'kicad_cli': shutil.which('kicad-cli'),
                'java': shutil.which('java'), 'node': shutil.which('node'),
                'konnect': shutil.which('konnect'), 'freerouting': shutil.which('freerouting')}
        for key, cmd in [('kicad_version', ['kicad-cli', 'version']), ('java_version', ['java', '-version'])]:
            try:
                r = subprocess.run(cmd, capture_output=True, text=True)
                data[key] = (r.stdout + r.stderr).strip()
            except FileNotFoundError:
                data[key] = 'NOT_FOUND'
        try:
            pcb = pcb_api(); data['pcbnew_version'] = pcb.GetBuildVersion()
            data['dsn_export_api'] = hasattr(pcb, 'ExportSpecctraDSN')
            data['ses_import_api'] = hasattr(pcb, 'ImportSpecctraSES')
        except RuntimeError as e:
            data['pcbnew_error'] = str(e)
        print(json.dumps(data, indent=2)); return 0 if data['kicad_cli'] else 2
    if a.action == 'init':
        src = Path(a.source).resolve(); dest = fresh(a.dest, src)
        before = manifest(src)
        dest.mkdir(); copy_project(src, dest / 'design')
        for name in ['README.adoc', 'AGENTS.md', 'WORKLOG.adoc', 'board-brief.adoc', 'routing-report.adoc']:
            shutil.copy2(ROOT / 'templates' / name, dest / name)
        with (dest / 'AGENTS.md').open('a') as f:
            f.write(f'\nToolkit location for this local experiment: `{ROOT}`. Read its `AGENTS.md` and `guides/01-how-it-works.adoc`.\n')
        shutil.copy2(ROOT / 'templates' / 'kicad-project.gitignore', dest / '.gitignore')
        write_json(dest / 'source-manifest.json', before)
        write_json(dest / 'copied-manifest.json', manifest(dest / 'design'))
        if before != manifest(src):
            raise RuntimeError('Source changed during copy; discard this experiment and coordinate the writer')
        copied = manifest(dest / 'design')
        if any(before.get(k) != v for k, v in copied.items()):
            raise RuntimeError('Copy verification failed')
        print(f'Created {dest}; source unchanged; {len(copied)} copied files verified.'); return 0
    if a.action == 'compare':
        b = json.loads(Path(a.before).read_text()); n = json.loads(Path(a.after).read_text())
        locked = [t for t in b['tracks'] if t['locked']]
        result = {'footprints_and_pad_nets_unchanged': b['footprints'] == n['footprints'],
                  'tracks_unchanged': b['tracks'] == n['tracks'],
                  'locked_tracks_preserved_exactly': all(t in n['tracks'] for t in locked),
                  'before': b['metrics'], 'after': n['metrics'],
                  'scope': 'Snapshot fields only; inspect outline, zone geometry, custom rules, arc/via details and electrical behavior separately'}
        print(json.dumps(result, indent=2))
        return 0 if result['footprints_and_pad_nets_unchanged'] and result['locked_tracks_preserved_exactly'] else 1
    board = board_path(a.board); pcb = pcb_api()
    source_before = manifest(board.parent)
    native = pcb.LoadBoard(str(board))
    if a.action == 'import-ses':
        ses = Path(a.ses).resolve()
        if not ses.is_file() or ses.suffix.lower() != '.ses':
            raise ValueError('Expected an existing .ses file')
        dest = fresh(a.dest, board.parent)
        copy_project(board.parent, dest)
        before = snapshot(native, pcb)
        if not pcb.ImportSpecctraSES(native, str(ses)):
            raise RuntimeError('Native SES import failed; candidate is not accepted')
        after = snapshot(native, pcb)
        if before['footprints'] != after['footprints']:
            raise RuntimeError('SES changed footprint/pad data; refusing to save imported board')
        pcb.SaveBoard(str(dest / board.name), native)
        write_json(dest / 'routing-import.json', {'source_sha256': digest(board), 'ses_sha256': digest(ses),
                   'status': 'IMPORTED_NOT_VALIDATED', 'before': before['metrics'], 'after': after['metrics']})
        print(f'Imported into {dest / board.name}; refill zones, run native checks, compare and review.')
    else:
        out = fresh(a.out); out.mkdir()
        if a.action == 'export-dsn':
            dsn = out / (board.stem + '.dsn')
            if not pcb.ExportSpecctraDSN(native, str(dsn)) or not dsn.is_file() or not dsn.stat().st_size:
                raise RuntimeError('Native DSN export failed')
            write_json(out / 'export.json', {'source_sha256': digest(board), 'dsn_sha256': digest(dsn),
                       'kicad': pcb.GetBuildVersion(), 'status': 'EXPORTED_NOT_ROUTED'})
            print(f'Exported {dsn}')
        else:
            sch = board.with_suffix('.kicad_sch'); pro = board.with_suffix('.kicad_pro')
            if not sch.is_file() or not pro.is_file():
                raise ValueError('Require matching .kicad_sch and .kicad_pro for parity checking')
            write_json(out / 'geometry.json', snapshot(native, pcb))
            commands = [
                ('erc', ['kicad-cli','sch','erc','--severity-all','--exit-code-violations','--format','json','-o',str(out/'erc.json'),str(sch)]),
                ('drc', ['kicad-cli','pcb','drc','--severity-all','--all-track-errors','--schematic-parity','--exit-code-violations','--format','json','-o',str(out/'drc.json'),str(board)]),
                ('netlist', ['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(out/'netlist.xml'),str(sch)]),
                ('schematic', ['kicad-cli','sch','export','pdf','-o',str(out/'schematic.pdf'),str(sch)])]
            results = [run_logged(cmd, out, name) for name, cmd in commands]
            outputs = ['erc.json','drc.json','netlist.xml','schematic.pdf']
            ok = all(r['exit_code'] == 0 for r in results) and all((out/f).is_file() and (out/f).stat().st_size for f in outputs)
            unchanged = all((board.parent / rel).is_file() and digest(board.parent / rel) == h
                            for rel, h in source_before.items())
            ok = ok and unchanged
            write_json(out/'checks.json', {'checked_at': datetime.now(timezone.utc).isoformat(), 'commands': results,
                       'status': 'PASS' if ok else 'REVIEW_REQUIRED', 'source_files_unchanged': unchanged,
                       'hardware_validation': 'NOT_RUN', 'zone_refill': 'NOT_RUN',
                       'scope': 'Native saved-file checks and exports; inspect warnings/exclusions and drawings', 'source_sha256': digest(board)})
            print(f'{"PASS" if ok else "REVIEW_REQUIRED"}: {out}')
            return 0 if ok else 1
    # Ignore newly-created reports if output is under source; verify every pre-existing file.
    if any(not (board.parent/rel).is_file() or digest(board.parent/rel) != h for rel,h in source_before.items()):
        raise RuntimeError('A pre-existing source file changed during the operation')
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError) as e:
        print(f'ERROR: {e}', file=sys.stderr); sys.exit(2)
