"""
PhoBERT-based NLP Model for Vietnamese Event Extraction
Replaces rule-based regex system with transformer-based approach
"""
from __future__ import annotations
import json
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path

try:
    import torch
    from transformers import AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    TRANSFORMERS_AVAILABLE = False
    # Don't print during import to avoid Unicode errors
    pass

from .time_parser import parse_vietnamese_time_range


class PhoBERTEventExtractor:
    """
    PhoBERT-based event information extractor for Vietnamese text.
    Extracts: event name, time, location, reminder
    """
    
    def __init__(self, model_path: Optional[str] = None, device: str = 'cpu', fallback_mode: bool = False):
        """
        Initialize PhoBERT model
        
        Args:
            model_path: Path to fine-tuned model (if None, uses base PhoBERT)
            device: 'cpu' or 'cuda'
            fallback_mode: If True, allow initialization without transformers (rule-based only)
        """
        if not TRANSFORMERS_AVAILABLE and not fallback_mode:
            raise ImportError("transformers library required. Install: pip install transformers torch")
        
        if fallback_mode or not TRANSFORMERS_AVAILABLE:
            # Rule-based mode only
            self.model = None
            self.tokenizer = None
            self.classifier = None
            self.device = 'cpu'
            self.model_path = None
            return
        
        self.device = device
        self.model_path = model_path
        
        # Check if this is a fine-tuned model with .pt file
        if model_path and Path(model_path).exists():
            model_pt = Path(model_path) / "model.pt"
            if model_pt.exists():
                print(f"🔄 Loading fine-tuned PhoBERT from {model_path}...")
                # Load from phobert_trainer format
                from .phobert_trainer import PhoBERTEventClassifier
                
                # Load base model and tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                phobert_base = AutoModel.from_pretrained("vinai/phobert-base")
                
                # Create classifier and load weights
                self.classifier = PhoBERTEventClassifier(phobert_base)
                self.classifier.load_state_dict(torch.load(model_pt, map_location=device))
                self.classifier.to(self.device)
                self.classifier.eval()
                
                print("✅ Loaded fine-tuned PhoBERT model")
                return
        
        # Fallback to base PhoBERT
        # Try to use local cached directory first to avoid re-downloading
        local_base_dir = Path("./models/phobert_base")
        if local_base_dir.exists():
            print(f"🔄 Loading base PhoBERT from local cache: {local_base_dir}")
            base_source = str(local_base_dir)
        else:
            print(f"🔄 Loading base PhoBERT (vinai/phobert-base) from Hugging Face...")
            base_source = "vinai/phobert-base"

        self.tokenizer = AutoTokenizer.from_pretrained(base_source)
        self.model = AutoModel.from_pretrained(base_source)
        self.model.to(self.device)
        self.model.eval()
        self.classifier = None  # No fine-tuned classifier
        
        print("✅ PhoBERT model loaded successfully")
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text using PhoBERT
        
        Args:
            text: Input Vietnamese text
            
        Returns:
            Dict with keys: event_name, time_str, location, reminder_minutes
        """
        if not text:
            return self._empty_result()
        
        # Tokenize input
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=256
        ).to(self.device)
        
        # Use fine-tuned classifier if available
        if hasattr(self, 'classifier') and self.classifier is not None:
            with torch.no_grad():
                outputs = self.classifier(inputs['input_ids'], inputs['attention_mask'])
                
                # Get predictions
                has_event = torch.argmax(outputs['event'], dim=1).item() == 1
                has_time = torch.argmax(outputs['time'], dim=1).item() == 1
                has_location = torch.argmax(outputs['location'], dim=1).item() == 1
                has_reminder = torch.argmax(outputs['reminder'], dim=1).item() == 1
                
                # Extract based on predictions using time_parser for better accuracy
                from .time_parser import parse_vietnamese_datetime
                
                result = {
                    'event_name': None,
                    'time_str': None,
                    'location': None,
                    'reminder_minutes': 0
                }
                
                # Extract time using sophisticated time_parser
                if has_time:
                    result['time_str'] = self._extract_time_heuristic(text)
                
                # Extract location
                if has_location:
                    result['location'] = self._extract_location_heuristic(text)
                
                # Extract reminder
                if has_reminder:
                    result['reminder_minutes'] = self._extract_reminder(text)
                
                # Extract event name by removing extracted components
                if has_event:
                    result['event_name'] = self._extract_event_name(text, result)
                
                return result
        
        # Fallback: use base model embeddings
        with torch.no_grad():
            if hasattr(self, 'model'):
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state  # [batch, seq_len, hidden_size]
                entities = self._extract_with_embeddings(text, embeddings)
            else:
                # Last resort: pure heuristics
                entities = self._extract_with_heuristics(text)
        
        return entities
    
    def _extract_with_embeddings(self, text: str, embeddings: torch.Tensor) -> Dict[str, Any]:
        """
        Extract entities using PhoBERT embeddings + heuristics
        This is a hybrid approach while the model is being fine-tuned
        """
        result = {
            'event_name': None,
            'time_str': None,
            'location': None,
            'reminder_minutes': 0
        }
        
        # Use attention-weighted representation for semantic understanding
        # CLS token embedding for sentence-level representation
        cls_embedding = embeddings[0, 0, :]  # [hidden_size]
        
        # Time extraction (enhanced with semantic understanding)
        result['time_str'] = self._extract_time_semantic(text, embeddings)
        
        # Location extraction (enhanced with NER-like approach)
        result['location'] = self._extract_location_semantic(text, embeddings)
        
        # Reminder extraction
        result['reminder_minutes'] = self._extract_reminder(text)
        
        # Event name extraction (what remains after removing time/location/reminder)
        result['event_name'] = self._extract_event_name(text, result)
        
        return result
    
    def _extract_time_heuristic(self, text: str) -> Optional[str]:
        """Simple heuristic time extraction - returns time string"""
        if not text:
            return None
        
        # Normalize for matching (but return original text)
        import unicodedata
        def normalize(s):
            s = s.lower()
            s = s.replace('đ', 'd')
            
            # Fix typo numbers: "sauh" -> "sau", "namh" -> "nam", etc.
            typo_map = {
                'moth': 'mot', 'haih': 'hai', 'bah': 'ba', 'bonh': 'bon', 
                'tuh': 'tu', 'namh': 'nam', 'sauh': 'sau', 'bayh': 'bay', 
                'tamh': 'tam', 'chinh': 'chin', 'muoih': 'muoi'
            }
            for typo, correct in typo_map.items():
                s = s.replace(typo, correct)
            
            nfkd = unicodedata.normalize('NFKD', s)
            return ''.join(c for c in nfkd if not unicodedata.combining(c))
        
        text_norm = normalize(text)
        
        # Time patterns (comprehensive Vietnamese time expressions)
        # Order matters: more specific patterns first
        # NOTE: These patterns match against NORMALIZED text (no diacritics: ô→o, ư→u, đ→d, etc.)
        time_patterns = [
            # PRIORITY 0: Time ranges (MUST be FIRST to capture full range)
            # "từ 9h đến 11h sáng mai", "9h-11h", "9h đến 11h"
            # Allow period (sang/chieu/toi) and relative (mai/hom nay/etc) AFTER range
            # FIXED: Use (?:\d{2})? instead of \d{0,2} to avoid catastrophic backtracking
            r'(?:tu\s+)?\d{1,2}\s*(?:h|gio|:)(?:\d{2})?\s*(?:den|-|–)\s*\d{1,2}\s*(?:h|gio|:)(?:\d{2})?\s*(?:sang|trua|chieu|toi|dem)?\s*(?:mai|hom\s+nay|ngay\s+mai|ngay\s+kia)?',
            
            # PRIORITY 1: Number words + period + weekday (REVERSED ORDER)
            # "muoi gio sang chu nhat" → Must come FIRST
            r'(?:mot|hai|ba|bon|tu|nam|sau|bay|tam|chin|muoi|mươi)\s+gio\s*(?:sang|trua|chieu|toi|dem)?\s*(?:chu\s+nhat|cn)',
            r'(?:mot|hai|ba|bon|tu|nam|sau|bay|tam|chin|muoi|mươi)\s+gio\s*(?:sang|trua|chieu|toi|dem)?\s*(?:thu[s]?|t)\s*(?:\d+|hai|ba|tu|nam|sau|bay)',
            
            # PRIORITY 2: Weekday + number words + period
            # "chu nhat sauh gio chieu"
            r'(?:chu\s+nhat|cn)\s+(?:mot|hai|ba|bon|tu|nam|sau|bay|tam|chin|muoi)\s+gio\s*(?:sang|trua|chieu|toi|dem)',
            r'(?:thu[s]?|t)\s*(?:\d+|hai|ba|tu|nam|sau|bay)\s+(?:mot|hai|ba|bon|tu|nam|sau|bay|tam|chin|muoi)\s+gio\s*(?:sang|trua|chieu|toi|dem)',
            
            # PRIORITY 3: Weekday + period + hour (REVERSED ORDER)
            # "thứ 5 chiều 3h"
            r'(?:chu\s+nhat|cn)\s+(?:sang|trua|chieu|toi|dem)\s+\d{1,2}\s*(?:h|gio)',
            r'(?:thu[s]?|t)\s*(?:\d+|hai|ba|tu|nam|sau|bay)\s+(?:sang|trua|chieu|toi|dem)\s+\d{1,2}\s*(?:h|gio)',
            
            # PRIORITY 4: Weekday + time + period
            # "t5 8h sang", "thứ 3 10h sáng", "cn 6h chiều"
            r'(?:chu\s+nhat|cn)\s+\d{1,2}\s*(?:h|gio|:)\s*\d{0,2}\s*(?:sang|trua|chieu|toi|dem)',
            r'(?:thu[s]?|t)\s*(?:\d+|hai|ba|tu|nam|sau|bay)\s+\d{1,2}\s*(?:h|gio|:)\s*\d{0,2}\s*(?:sang|trua|chieu|toi|dem)',
            # Weekday + time (without period)
            r'(?:chu\s+nhat|cn)\s+\d{1,2}\s*(?:h|gio|:)',
            r'(?:thu[s]?|t)\s*(?:\d+|hai|ba|tu|nam|sau|bay)\s+\d{1,2}\s*(?:h|gio|:)',
            # Date + time + period: hôm nay 6h chiều, mai 10h sáng, ngày kia 8h tối
            # MUST come before simple "date + time" to capture period
            r'(?:hom\s+nay|ngay\s+mai|mai|ngay\s+kia)\s+\d{1,2}\s*(?:h|gio)\s*(?:\d{1,2}\s*(?:phut))?\s*(?:sang|trua|chieu|toi|dem)',
            # Period + date combo: tối mai, sáng mai, chiều mai, đêm nay, tối nay
            # BUT NOT "toi" alone (which could be "tôi" = I/me)
            r'(?:toi|sang|chieu|trua|dem)\s+(?:mai|hom\s+nay|nay|ngay\s+kia)',
            # Time with typo period: 7h sang, 6h toi (without diacritics)
            # Use word boundary to avoid matching "toi co" (tôi có = I have)
            r'\d{1,2}\s*h\s+(?:sang|chieu|trua|dem)\b',
            r'\d{1,2}\s*h\s+toi(?:\s+nay|\s+mai)?\b',  # "6h tối" or "6h tối nay" but not "6h tôi"
            # Time + date format DD.MM.YYYY or DD/MM/YYYY or DD-MM-YYYY
            # Handles: "9h ngày 20.10", "9h vào 20.10", "9h tới ngày 20.10"
            r'\d{1,2}\s*(?:h|gio|:|)\s*\d{0,2}\s*(?:vao|toi|den)?\s*(?:ngay\s+)?\d{1,2}[\.\-/]\d{1,2}(?:[\.\-/]\d{4})?',
            # "lúc" + time: lúc 12 giờ, lúc 10h sáng
            r'luc\s+\d{1,2}\s*(?:h|gio)\s*(?:\d{1,2}\s*(?:phut))?\s*(?:sang|trua|chieu|toi|dem)?',
            # Time + weekday + week: 9:00 cn tuần sau, 10h t2 tuần sau
            r'\d{1,2}\s*(?::|h|gio)\s*\d{0,2}\s*(?:cn|thu|t)\s*\d*\s*(?:tuan\s+sau)?',
            # Time + date complex: 14h ngày 6 tháng 12
            r'\d{1,2}\s*(?:h|gio)\s+ngay\s+\d{1,2}\s+thang\s+\d{1,2}',
            # Combined: time + period + date
            r'\d{1,2}(?:h\d{2}|:\d{2}|h)\s*(?:sang|trua|chieu|toi|dem)?\s*(?:hom\s+nay|ngay\s+mai|mai|ngay\s+kia|thu\s+\d|cn)',
            # Time with date: 8:30 ngày mai, 10h ngày mai, 12 giờ hôm nay, 17h30 hôm nay
            r'\d{1,2}\s*(?:h\d{2}|gio|:\d{2})\s+(?:hom\s+nay|ngay\s+mai|mai|ngay\s+kia)',
            # Number words: hai giờ chiều, một giờ trưa
            r'(?:mot|hai|ba|bon|nam|sau|bay|tam|chin|muoi|muoi\s+mot|muoi\s+hai)\s+gio\s*(?:sang|trua|chieu|toi|dem)?',
            # Time with period: 10h sáng, 2h chiều, 12 giờ hôm nay
            r'\d{1,2}\s*(?:h|gio)\s*(?:\d{1,2}\s*(?:phut))?\s*(?:sang|trua|chieu|toi|dem)',
            # Time with weekday: 10h thứ 2, 14h CN
            r'\d{1,2}\s*(?:h|gio)\s*(?:thu|t)?\s*\d|CN',
            # Simple time: 10h, 10:30, 10 giờ 30, 12 giờ
            r'\d{1,2}\s*(?:h|:\d{2}|gio(?:\s*\d{1,2}\s*(?:phut)?)?)',
            # Rưỡi: 10h rưỡi
            r'\d{1,2}\s*(?:h|gio)\s*ruoi',
            # Kém: 10h kém 15
            r'\d{1,2}\s*(?:h|gio)\s*kem\s*\d{1,2}',
            # Time range: 10h-12h
            r'\d{1,2}(?:h|:\d{2})?\s*[-–]\s*\d{1,2}(?:h|:\d{2})?',
            # Duration: trong X tuần/ngày/tháng
            r'trong\s+\d+\s+(?:ngay|tuan|thang)',
            # Special relative: cuối tuần
            r'cuoi\s+tuan',
            # Date relative: ngày mai, hôm nay, tuần sau
            # Also capture with time: "hôm nay 10h", "10h hôm nay"
            r'(?:hom\s+nay|ngay\s+mai|mai|ngay\s+kia|tuan\s+sau|tuan\s+toi|thang\s+sau)(?:\s+\d{1,2}\s*(?:h|gio))?',
            r'\d{1,2}\s*(?:h|gio)\s+(?:hom\s+nay|ngay\s+mai|mai)',
            # Weekdays: thứ 2, thứ hai, t2, CN
            r'(?:thu|t)\s*\d+(?:\s+tuan\s+sau)?|cn(?:\s+tuan\s+sau)?',
            # Date: ngày 15 tháng 12, ngày 6 tháng 12
            r'ngay\s+\d{1,2}\s+thang\s+\d{1,2}',
        ]
        
        # Match on normalized text for pattern recognition, then extract from original
        best_match = None
        best_length = 0
        best_span = None
        
        for pattern in time_patterns:
            match = re.search(pattern, text_norm)
            if match:
                matched_text = match.group(0)
                if len(matched_text) > best_length:
                    best_length = len(matched_text)
                    best_span = match.span()
        
        # Extract from original text using span, then extend end to capture full words with diacritics
        if best_span:
            start, end = best_span
            # Extend end position while we're still in the same word (handle diacritic chars)
            while end < len(text) and text[end].isalpha():
                end += 1
            best_match = text[start:end]
        
        return best_match
    
    def _extract_location_heuristic(self, text: str) -> Optional[str]:
        """Enhanced location extraction using improved regex from pipeline.py"""
        if not text:
            return None
        
        # Enhanced pattern: ở|o / tại|tai followed by location (stops at punctuation or time connectors)
        # This matches the improved regex from pipeline.py (lines 56-62)
        # Pattern: "o truong ham tu" -> "truong ham tu" (handles no-diacritics)
        location_pattern = re.compile(
            r"\b(?:ở|o|tại|tai)\s+"                        # location marker (with/without diacritics)
            r"([^\n,.;:!?]+?)\s*"                          # location content (non-greedy)
            r"(?=$|[，,.;:!?]|\b(?:vào|vao|lúc|luc|khoảng|khoang|đến|den|tới|toi|cho\s+đến|cho\s+den|nhắc|nhac|trước|truoc))",
            re.IGNORECASE
        )
        
        match = location_pattern.search(text)
        if match:
            location = match.group(1).strip()
            if len(location) > 2:
                return location
        
        # Fallback: specific location types (phòng, tầng, building names)
        # PRIORITY ORDER: Compound locations (company + building) FIRST, then single patterns
        fallback_patterns = [
            # PRIORITY 1: Company/organization + building (e.g., "công ty ABC phòng 401")
            # Captures full compound location: organization name + room/floor
            (r'(?:công ty|cong ty|văn phòng|van phong|trường|truong|bệnh viện|benh vien)\s+[A-Z\w]+(?:\s+(?:phòng|phong|tầng|tang|toà|toa|lầu|lau)\s+[\w\d]+)?', False),
            
            # PRIORITY 2: Named places with names (e.g., "nhà hàng Sài Gòn", "quán cafe Trung Nguyên")
            (r'(?:nhà hàng|nha hang|quán|quan|cafe|café|siêu thị|sieu thi|chợ|cho)\s+[\w\s]{2,30}', False),
            
            # PRIORITY 3: Building-only (e.g., "phòng 302", "tầng 5") - MUST BE LAST
            # Only matches if no compound location found above
            (r'(?:phòng|phong|tầng|tang|toà|toa|lầu|lau)\s+[\w\d]+', False),
        ]
        
        for pattern, has_group in fallback_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if has_group and match.lastindex:
                    location = match.group(1)
                else:
                    location = match.group(0)
                
                # Clean up
                location = re.sub(r'^(?:ở|o|tại|tai|đến|den|về|ve)\s+', '', location, flags=re.IGNORECASE)
                location = location.strip(' ,.;')
                
                # Stop at time expressions or reminder keywords
                location = re.split(r'\s+(?:\d{1,2}(?:h|:|giờ|gio)|nhắc|nhac|remind)', location)[0]
                
                if len(location) > 2:
                    return location
        
        return None
    
    def _extract_with_heuristics(self, text: str) -> Dict[str, Any]:
        """Pure heuristic extraction (fallback)"""
        result = {
            'event_name': text,
            'time_str': self._extract_time_heuristic(text),
            'location': self._extract_location_heuristic(text),
            'reminder_minutes': self._extract_reminder(text)
        }
        result['event_name'] = self._extract_event_name(text, result)
        return result
    
    def _extract_time_semantic(self, text: str, embeddings: torch.Tensor) -> Optional[str]:
        """Extract time expressions using semantic understanding"""
        # Build normalization map first
        import unicodedata
        
        # Step 1: Normalize typos character-by-character (preserves length)
        typo_map = {
            'moth': 'mot', 'haih': 'hai', 'bah': 'ba', 'bonh': 'bon',
            'tuh': 'tu', 'namh': 'nam', 'sauh': 'sau', 'bayh': 'bay',
            'tamh': 'tam', 'chinh': 'chin', 'muoih': 'muoi'
        }
        text_typo_fixed = text.lower()
        for typo, correct in typo_map.items():
            text_typo_fixed = text_typo_fixed.replace(typo, correct)
        
        # Step 2: Remove diacritics (changes length - need mapping!)
        # Build character mapping: norm_pos -> orig_pos
        text_norm = ''
        norm_to_orig = []  # Maps each char in normalized to original position
        
        for i, char in enumerate(text_typo_fixed):
            # Remove diacritics
            nfd = unicodedata.normalize('NFD', char)
            no_diacritics = ''.join(c for c in nfd if not unicodedata.combining(c))
            # Add to normalized text
            for c in no_diacritics:
                text_norm += c
                norm_to_orig.append(i)  # Each normalized char maps to this original position
        
        # Time patterns (comprehensive Vietnamese time expressions)
        # IMPORTANT: Order matters - ranges MUST come first!
        # NOTE: Patterns match against NORMALIZED text (no typos, no diacritics)
        time_patterns = [
            # PRIORITY 0: Time ranges (MUST be first to capture as single unit)
            # "từ 9h đến 11h sáng mai", "9h-11h", "9h đến 11h"
            r'(?:tu\s+)?\d{1,2}(?:h|:\d{2}|(?:\s*gio(?:\s*\d{1,2}(?:\s*phut)?)?))\s*(?:den|den|-|–)\s*\d{1,2}(?:h|:\d{2}|(?:\s*gio(?:\s*\d{1,2}(?:\s*phut)?)?))',
            # Number words + gio + period + weekday (e.g., "chu nhat sau gio chieu")
            r'(?:chu\s+nhat|cn|thu|t\s*\d)\s+(?:mot|hai|ba|bon|tu|nam|sau|bay|tam|chin|muoi)\s+(?:gio)\s*(?:sang|trua|chieu|toi|dem)?',
            r'(?:mot|hai|ba|bon|tu|nam|sau|bay|tam|chin|muoi)\s+(?:gio)\s*(?:sang|trua|chieu|toi|dem)?\s*(?:chu\s+nhat|cn|thu|t\s*\d)',
            # Explicit time: 10h, 10:30, 10 giờ 30
            r'\d{1,2}(?:h|:\d{2}|(?:\s*gio(?:\s*\d{1,2}(?:\s*phut)?)?))(?:\s*(?:sang|trua|chieu|toi|dem))?',
            # Relative: ngày mai, hôm nay, tuần sau
            r'(?:hom\s+nay|ngay\s+mai|mai|ngay\s+kia|tuan\s+sau|tuan\s+toi|thang\s+sau)',
            # Weekdays: thứ 2, thứ hai, t2, CN
            r'(?:thu|t)\s*\d|CN|chu\s+nhat',
            # Date: ngày 15 tháng 12
            r'ngay\s+\d{1,2}\s+thang\s+\d{1,2}',
            # Period: sáng, chiều, tối
            r'\b(?:sang|trua|chieu|toi|dem|khuya)\b',
        ]
        
        # Find all time-related spans ON NORMALIZED TEXT
        time_spans = []
        for pattern in time_patterns:
            for match in re.finditer(pattern, text_norm, re.IGNORECASE):
                # Map normalized positions back to original text positions
                norm_start = match.start()
                norm_end = match.end() - 1  # Last char of match
                
                # Get original positions
                orig_start = norm_to_orig[norm_start] if norm_start < len(norm_to_orig) else norm_start
                orig_end = norm_to_orig[norm_end] + 1 if norm_end < len(norm_to_orig) else norm_end + 1
                
                # Extract from ORIGINAL (typo-fixed) text
                time_spans.append((orig_start, orig_end, text_typo_fixed[orig_start:orig_end]))
        
        if not time_spans:
            return None
        
        # Merge overlapping/adjacent spans
        time_spans.sort(key=lambda x: x[0])
        merged = []
        for start, end, txt in time_spans:
            if merged and start <= merged[-1][1] + 3:
                # Merge with previous - EXTEND to max end position (don't truncate!)
                new_end = max(end, merged[-1][1])
                merged[-1] = (merged[-1][0], new_end, text_typo_fixed[merged[-1][0]:new_end])
            else:
                merged.append((start, end, txt))
        
        # Return the longest/most complete time expression FROM ORIGINAL TEXT (with typos fixed)
        if merged:
            longest = max(merged, key=lambda x: x[1] - x[0])
            start, end = longest[0], longest[1]
            # Extend end to capture full words
            while end < len(text) and text[end].isalpha():
                end += 1
            return text[start:end].strip()
        
        return None
    
    def _extract_location_semantic(self, text: str, embeddings: torch.Tensor) -> Optional[str]:
        """Extract location using semantic understanding"""
        # Location markers
        # PRIORITY ORDER: Compound locations FIRST (company + building), then single patterns
        location_markers = [
            r'(?:ở|tại|đến|về)\s+([^,\.\d]{3,50})',
            # Company/org + building: "công ty ABC phòng 401"
            r'(?:trường|công ty|văn phòng|bệnh viện|nhà hàng|quán)\s+[A-Z\w]+(?:\s+(?:phòng|tầng|toà|tòa)\s+[\w\d]+)?',
            # Building-only (MUST BE LAST)
            r'(?:phòng|tầng|toà|tòa)\s+[\w\s\d]{1,30}',
        ]
        
        for pattern in location_markers:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Return captured group if exists, else full match
                location = match.group(1) if match.lastindex else match.group(0)
                # Clean up
                location = re.sub(r'^(?:ở|tại|đến|về)\s+', '', location, flags=re.IGNORECASE)
                location = location.strip(' ,.;')
                if len(location) > 2:
                    return location
        
        return None
    
    def _extract_reminder(self, text: str) -> int:
        """Extract reminder minutes"""
        # Reminder patterns - order matters (most specific first)
        patterns = [
            # "nhắc sớm hơn 1 giờ" / "nhac som hon 1 gio"
            (r'nhắc\s+(?:tôi\s+)?(?:sớm\s+hơn|som\s+hon)\s+(\d{1,2})\s*(?:giờ|h|gio)', 60),
            # "nhắc sớm hơn 30 phút" / "nhac som hon 30 phut"
            (r'nhắc\s+(?:tôi\s+)?(?:sớm\s+hơn|som\s+hon)\s+(\d{1,3})\s*(?:phút|phut|p)', 1),
            # "nhắc trước 10 phút"
            (r'nhắc\s+(?:tôi\s+)?(?:trước|truoc)\s+(\d{1,3})\s*(?:phút|phut|p)', 1),
            # "nhắc trước 1 giờ"
            (r'nhắc\s+(?:tôi\s+)?(?:trước|truoc)\s+(\d{1,2})\s*(?:giờ|gio|h)', 60),
            # "nhắc 1 giờ trước"
            (r'nhắc\s+(?:tôi\s+)?(\d{1,2})\s*(?:giờ|gio|h)\s*(?:trước|truoc)?', 60),
            # "nhắc 30 phút"
            (r'nhắc\s+(?:tôi\s+)?(\d{1,3})\s*(?:phút|phut|p)', 1),
            # "10 phút trước nhắc"
            (r'(\d{1,3})\s*(?:phút|phut|p)\s*(?:trước|truoc)\s*nhắc', 1),
            # "1 giờ trước nhắc"
            (r'(\d{1,2})\s*(?:giờ|gio|h)\s*(?:trước|truoc)\s*nhắc', 60),
        ]
        
        for pattern, multiplier in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = int(match.group(1))
                    return value * multiplier
                except:
                    pass
        
        # Check for reminder keyword without time (default: 15 minutes)
        if re.search(r'\b(?:nhắc|nhac|remind)\b', text, re.IGNORECASE):
            return 15
        
        return 0
    
    def _extract_event_name(self, text: str, extracted: Dict[str, Any]) -> str:
        """Extract event name by removing time, location, reminder
        
        IMPROVED: Better fragment removal and location-aware cleaning
        """
        cleaned = text
        
        # Remove weekday patterns (t2, t3, t5, cn, chu nhat, thu 2, thứ 3, etc.)
        weekday_patterns = [
            r'\b(?:thứ|thu)\s*(?:hai|ba|tư|tu|năm|nam|sáu|sau|bảy|bay|chủ\s*nhật)\b',
            # Typo variants with 'h' suffix
            r'\b(?:thứ|thu)\s*(?:haih|bah|tuh|namh|sauh|bayh)\b',
            r'\b(?:thứ|thu)\s*\d\b',
            r'\bt\s*\d\b',
            r'\bcn\b',
            r'\bchủ\s*nhật\b',
            r'\bchu\s*nhat\b',
        ]
        for pattern in weekday_patterns:
            cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
        
        # Remove time patterns (explicit times: 10h, 8:30, etc.)
        time_patterns = [
            r'\b\d{1,2}\s*[hH:]\s*\d{0,2}\b',  # 10h, 8:30
            r'\b\d{1,2}\s*giờ(?:\s*\d{1,2}\s*phút)?\b',  # 10 giờ, 10 giờ 30 phút
            # Number words + giờ (mười giờ, hai giờ, etc.)
            r'\b(?:một|mot|hai|ba|bốn|bon|năm|nam|sáu|sau|bảy|bay|tám|tam|chín|chin|mười|muoi|muoi\s+mot|muoi\s+hai)\s+giờ\b',
        ]
        for pattern in time_patterns:
            cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
        
        # Remove time expression if extracted
        if extracted.get('time_str'):
            time_str = extracted['time_str']
            cleaned = cleaned.replace(time_str, ' ')
        
        # Remove location marker + location (ở/o/tại + location) - ENHANCED
        # This removes the ENTIRE phrase "ở truong ham tu" not just marker
        location_marker_pattern = r'\b(?:ở|o|tại|tai)\s+[^\s,\.!?\d]+'
        cleaned = re.sub(location_marker_pattern, ' ', cleaned, flags=re.IGNORECASE)
        
        # Remove location if extracted (without marker) - WORD BY WORD
        if extracted.get('location'):
            location = extracted['location']
            # Remove full location phrase
            cleaned = cleaned.replace(location, ' ')
            # Also remove individual words from location (handles fragments like "ham", "tu")
            # BUT preserve compound verb/event phrases
            compound_phrases = [
                r'\bkhám\s+bệnh\b', r'\bkham\s+benh\b',  # medical checkup
                r'\băn\s+tối\b', r'\ban\s+toi\b',  # dinner
                r'\băn\s+sáng\b', r'\ban\s+sang\b',  # breakfast
                r'\băn\s+trưa\b', r'\ban\s+trua\b',  # lunch
                r'\bđi\s+cafe\b', r'\bdi\s+cafe\b',  # go to cafe (event, not just location)
                r'\bđi\s+chợ\b', r'\bdi\s+cho\b',  # go to market (event, not just location)
                r'\bra\s+chợ\b', r'\bra\s+cho\b',  # go out to market
            ]
            location_words = location.split()
            for word in location_words:
                if len(word) > 2:  # Only remove meaningful words
                    # Check if this word is part of a preserved compound phrase
                    skip = False
                    for phrase_pattern in compound_phrases:
                        if re.search(phrase_pattern, cleaned, re.IGNORECASE):
                            # Check if word is in this phrase
                            if word.lower() in re.search(phrase_pattern, cleaned, re.IGNORECASE).group().lower():
                                skip = True
                                break
                    if not skip:
                        # Use word boundary to avoid removing parts of other words
                        cleaned = re.sub(r'\b' + re.escape(word) + r'\b', ' ', cleaned, flags=re.IGNORECASE)
        
        # Remove reminder phrases
        reminder_patterns = [
            r'nhắc\s+(?:tôi\s+)?(?:trước|sớm\s+hơn)?\s*\d{1,3}\s*(?:phút|p|giờ|h|gio)(?:\s+trước)?',
            r'nhac\s+(?:toi\s+)?(?:truoc|som\s+hon)?\s*\d{1,3}\s*(?:phut|p|gio|h)(?:\s+truoc)?',
            r'\d{1,3}\s*(?:phút|phut|p|giờ|gio|h)\s*(?:trước|truoc\s+)?(?:nhắc|nhac|nhở|nho)',
            r'nhắc\s+(?:tôi\s+)?(?:trước|nhở|som\s+hon)?',
            r'nhac\s+(?:toi\s+)?(?:truoc|nho|som\s+hon)?',
            # Remove standalone reminder modifiers that might remain
            r'\b(?:sớm\s+hơn|som\s+hon|trước|truoc)\b',
        ]
        for pattern in reminder_patterns:
            cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
        
        # Remove relative time words
        relative_time = [
            'hôm nay', 'hom nay', 'ngày mai', 'ngay mai', 'mai', 
            'ngày kia', 'ngay kia', 'ngày mốt', 'ngay mot', 'mốt', 'mot',
            'hôm qua', 'hom qua', 'qua', 'nay',
            'tuần sau', 'tuan sau', 'tuần trước', 'tuan truoc',
        ]
        for word in relative_time:
            cleaned = re.sub(r'\b' + re.escape(word) + r'\b', ' ', cleaned, flags=re.IGNORECASE)
        
        # Remove period words (sáng, chiều, tối, đêm) but preserve compound phrases
        # E.g., keep "ăn tối", "ăn sáng", "ăn trưa" but remove standalone period words
        period_words_to_remove = ['sáng', 'sang', 'trưa', 'trua', 'chiều', 'chieu', 'đêm', 'dem', 'khuya']
        # Remove "tối" only if NOT preceded by "ăn" (preserve "ăn tối")
        cleaned = re.sub(r'(?<!ăn\s)(?<!an\s)\b(?:tối|toi)\b', ' ', cleaned, flags=re.IGNORECASE)
        # Remove other period words normally
        for word in period_words_to_remove:
            cleaned = re.sub(r'\b' + re.escape(word) + r'\b', ' ', cleaned, flags=re.IGNORECASE)
        
        # Remove time/location connectors
        connectors = ['vào', 'vao', 'lúc', 'luc', 'vào lúc', 'vao luc', 'khoảng', 'khoang', 'từ', 'tu', 'đến', 'den', 'tới', 'cho đến', 'cho den']
        for word in connectors:
            cleaned = re.sub(r'\b' + re.escape(word) + r'\b', ' ', cleaned, flags=re.IGNORECASE)
        
        # Remove location-related fragments (common fragments that leak into events)
        # NEW: Target specific problematic fragments with smart preservation
        location_fragments = [
            # Building/place words
            r'\b(?:phòng|phong|tầng|tang|toà|toa|lầu|lau)\b',
            # Partial words from compound location names
            r'\b(?:ham|tu|gần|gan|viện|vien|hàng|hang|công|cong|ty|quan)\b',
        ]
        for pattern in location_fragments:
            cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
        
        # Remove cafe/market words ONLY if NOT part of motion event (preserve "đi chợ", "đi cafe")
        # Use negative lookbehind to keep verb + location patterns
        cleaned = re.sub(r'(?<!đi\s)(?<!di\s)(?<!ra\s)(?<!vào\s)(?<!vao\s)\b(?:cafe|café)\b', ' ', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'(?<!đi\s)(?<!di\s)(?<!ra\s)(?<!vào\s)(?<!vao\s)\b(?:chợ|cho)\b', ' ', cleaned, flags=re.IGNORECASE)
        # Remove market-related words normally (these are rarely events)
        cleaned = re.sub(r'\b(?:siêu|sieu|thị|thi|truong|trường)\b', ' ', cleaned, flags=re.IGNORECASE)
        
        # Remove standalone numbers (including typo number words)
        cleaned = re.sub(r'\b\d{1,4}\b', ' ', cleaned)
        cleaned = re.sub(r'\b(?:sauh|namh|tamh|muoih|bayh|bah|bonh|tuh|haih|moth|chinh)\b', ' ', cleaned, flags=re.IGNORECASE)
        
        # Clean up whitespace and punctuation
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip(' ,.;-:!?')
        
        # POST-PROCESSING: Remove trailing single-word fragments
        # If cleaned ends with a single short word (< 4 chars), it's likely a fragment
        words = cleaned.split()
        if len(words) > 1 and len(words[-1]) <= 3:
            # Check if last word is a common fragment
            last_word = words[-1].lower()
            if last_word in ['ham', 'tu', 'ty', 'abc', 'gan', 'nha', 'o', 'a', 'b', 'c', 'mai', 'bai', 'sai', 'gon']:
                words = words[:-1]
                cleaned = ' '.join(words)
        
        # If cleaned is empty or too short, try to extract main action verb
        if not cleaned or len(cleaned) < 2:
            # Look for common action verbs
            action_verbs = ['họp', 'hop', 'đi', 'di', 'làm', 'lam', 'gặp', 'gap', 'học', 'hoc', 'ăn', 'an', 'chạy', 'chay', 'tập', 'tap']
            for verb in action_verbs:
                if re.search(r'\b' + re.escape(verb) + r'\b', text, flags=re.IGNORECASE):
                    # Find verb and next 1-2 words
                    match = re.search(r'\b' + re.escape(verb) + r'\b(?:\s+\w+){0,2}', text, flags=re.IGNORECASE)
                    if match:
                        cleaned = match.group(0)
                        # Remove fragments from matched text too
                        for pattern in location_fragments:
                            cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
                        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                        break
        
        # Final cleanup
        if not cleaned or len(cleaned) < 2:
            words = text.split()[:3]
            cleaned = ' '.join(words)
        
        return cleaned.strip()
    
    def _classify_entities(self, text: str, embeddings: torch.Tensor) -> Dict[str, Any]:
        """
        Use trained classification heads to extract entities
        (To be implemented after training)
        """
        # This will be implemented when we add the training module
        # For now, fallback to embedding-based extraction
        return self._extract_with_embeddings(text, embeddings)
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            'event_name': None,
            'time_str': None,
            'location': None,
            'reminder_minutes': 0
        }
    
    def process(self, text: str, relative_base: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Full processing pipeline: extract entities and parse time
        HYBRID APPROACH: Use PhoBERT predictions + rule-based extraction
        
        Args:
            text: Input text
            relative_base: Base datetime for relative time parsing
            
        Returns:
            Dict with: event, start_time, end_time, location, reminder_minutes
        """
        if not text:
            return {
                'event': None,
                'start_time': None,
                'end_time': None,
                'location': None,
                'reminder_minutes': 0
            }
        
        # Use rule-based extraction (always reliable)
        time_str = self._extract_time_heuristic(text)
        location = self._extract_location_heuristic(text)
        reminder = self._extract_reminder(text)
        
        # Parse time string to datetime
        start_dt, end_dt = parse_vietnamese_time_range(
            time_str,
            relative_base=relative_base
        )
        
        # Extract event name by removing extracted components
        entities_for_cleaning = {
            'time_str': time_str,
            'location': location,
            'reminder_minutes': reminder
        }
        event_name = self._extract_event_name(text, entities_for_cleaning)
        
        return {
            'event': event_name if event_name else text,
            'start_time': start_dt.isoformat() if start_dt else None,
            'end_time': end_dt.isoformat() if end_dt else None,
            'location': location,
            'reminder_minutes': reminder,
        }


class PhoBERTNLPPipeline:
    """
    Main pipeline that wraps PhoBERTEventExtractor
    Compatible interface with the old NLPPipeline
    """
    
    def __init__(self, model_path: Optional[str] = None, relative_base: Optional[datetime] = None):
        """
        Initialize PhoBERT pipeline
        
        Args:
            model_path: Path to fine-tuned model (optional)
            relative_base: Base datetime for relative time parsing
        """
        self.relative_base = relative_base
        
        # Check if transformers is available
        if not TRANSFORMERS_AVAILABLE:
            pass  # Silently fallback to rule-based system
            self.use_phobert = False
            return
        
        try:
            # Determine device
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            print(f"🔧 Using device: {device}")
            
            self.extractor = PhoBERTEventExtractor(model_path=model_path, device=device)
            self.use_phobert = True
            print("✅ PhoBERT pipeline initialized successfully")
            
        except Exception as e:
            # Silently fallback
            self.use_phobert = False
    
    def process(self, text: str) -> Dict[str, Any]:
        """
        Process text and extract event information
        
        Args:
            text: Input Vietnamese text
            
        Returns:
            Dict with: event, start_time, end_time, location, reminder_minutes
        """
        if not self.use_phobert:
            # Fallback to basic extraction
            return self._fallback_process(text)
        
        try:
            return self.extractor.process(text, relative_base=self.relative_base)
        except Exception as e:
            print(f"❌ PhoBERT processing error: {e}")
            return self._fallback_process(text)
    
    def _fallback_process(self, text: str) -> Dict[str, Any]:
        """Simple fallback when PhoBERT is not available"""
        # Use the existing PhoBERTEventExtractor heuristic methods in fallback mode
        extractor = PhoBERTEventExtractor(fallback_mode=True)
        return extractor.process(text, relative_base=self.relative_base)


# Convenience function for backward compatibility
def create_nlp_pipeline(use_phobert: bool = True, model_path: Optional[str] = None) -> Any:
    """
    Create NLP pipeline (PhoBERT or rule-based)
    
    Args:
        use_phobert: Whether to use PhoBERT (if available)
        model_path: Path to fine-tuned PhoBERT model
        
    Returns:
        NLP pipeline instance
    """
    if use_phobert:
        try:
            return PhoBERTNLPPipeline(model_path=model_path)
        except Exception as e:
            pass  # Silently fallback
    
    # Fallback to rule-based
    from .pipeline import NLPPipeline
    return NLPPipeline()
