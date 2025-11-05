from __future__ import annotations
import json
from typing import Iterable
from datetime import datetime
from ics import Calendar


def import_from_json(db_manager, filepath: str, nlp_pipeline=None) -> int:
    """Import events from a JSON file.
    Supports two formats:
    1. Export format: {"event_name": "...", "start_time": "...", ...}
    2. Test case format: {"input": "...", "expected": {...}} - will parse 'input' with NLP
    
    Returns number of events imported.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("JSON không hợp lệ: cần một danh sách sự kiện")
    count = 0
    for ev in data:
        if not isinstance(ev, dict):
            continue
        
        # Check if this is a test case format (has 'input' and 'expected' keys)
        if 'input' in ev and 'expected' in ev:
            # This is a test case file - parse the 'input' field with NLP
            if nlp_pipeline is None:
                # If no NLP pipeline provided, skip test cases
                continue
            
            input_text = ev.get('input', '').strip()
            if not input_text:
                continue
            
            # Parse the input with NLP pipeline
            try:
                parsed = nlp_pipeline.process(input_text)
                to_insert = {
                    'event': parsed.get('event') or '',
                    'start_time': parsed.get('start_time'),
                    'end_time': parsed.get('end_time'),
                    'location': parsed.get('location'),
                    'reminder_minutes': int(parsed.get('reminder_minutes') or 0),
                }
                if to_insert['event'] and to_insert['start_time']:
                    db_manager.add_event(to_insert)
                    count += 1
            except Exception:
                # Skip items that fail to parse
                continue
        else:
            # Map compatible fields from export format
            to_insert = {
                'event': ev.get('event_name') or ev.get('event') or '',
                'start_time': ev.get('start_time'),
                'end_time': ev.get('end_time'),
                'location': ev.get('location'),
                'reminder_minutes': int(ev.get('reminder_minutes') or 0),
            }
            if to_insert['event'] and to_insert['start_time']:
                db_manager.add_event(to_insert)
                count += 1
    return count


essential_ics_fields = ('name', 'begin', 'location')


def _iter_ics_events(filepath: str) -> Iterable:
    with open(filepath, 'r', encoding='utf-8') as f:
        cal = Calendar(f.read())
    return cal.events


def import_from_ics(db_manager, filepath: str) -> int:
    """Import events from an .ics file. Returns number of events imported.
    Uses fields: name -> event_name, begin -> start_time, location.
    """
    count = 0
    for e in _iter_ics_events(filepath):
        name = getattr(e, 'name', None)
        begin = getattr(e, 'begin', None)
        location = getattr(e, 'location', None)
        start_iso = None
        if begin is not None:
            try:
                # ics may provide Arrow-like object
                dt = begin if isinstance(begin, datetime) else begin.datetime
                start_iso = dt.isoformat()
            except Exception:
                start_iso = None
        to_insert = {
            'event': name or '',
            'start_time': start_iso,
            'end_time': None,
            'location': location or None,
            'reminder_minutes': 0,
        }
        if to_insert['event'] and to_insert['start_time']:
            db_manager.add_event(to_insert)
            count += 1
    return count
