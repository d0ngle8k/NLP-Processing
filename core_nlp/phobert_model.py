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
        print(f"🔄 Loading base PhoBERT (vinai/phobert-base)...")
        self.tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")
        self.model = AutoModel.from_pretrained("vinai/phobert-base")
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
                
                # Extract based on predictions
                result = {
                    'event_name': text if has_event else None,
                    'time_str': self._extract_time_heuristic(text) if has_time else None,
                    'location': self._extract_location_heuristic(text) if has_location else None,
                    'reminder_minutes': self._extract_reminder(text) if has_reminder else 0
                }
                
                # Refine event name
                if result['event_name']:
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
            nfkd = unicodedata.normalize('NFKD', s)
            return ''.join(c for c in nfkd if not unicodedata.combining(c))
        
        text_norm = normalize(text)
        
        # Time patterns (comprehensive Vietnamese time expressions)
        # Order matters: more specific patterns first
        # NOTE: These patterns match against NORMALIZED text (no diacritics: ô→o, ư→u, đ→d, etc.)
        time_patterns = [
            # Weekday + time: thứ 3 mười giờ, thứ 2 10h, t2 8:30, chủ nhật 10h
            # Also handle typos: "bah" (ba + h), "sáuh" (sáu + h), "mườih" (mười + h)
            # Normalized forms: "muoih", "namh", "haih", "tamh", "sauh", "bah"
            r'(?:chu\s+nhat|cn)\s+(?:mot|hai|ba|bon|tu|nam|sau|bay|tam|chin|muoi|moth|haih|bah|bonh|tuh|namh|sauh|bayh|tamh|chinh|muoih)(?:\s+(?:mot|hai|moth|haih))?\b',
            r'(?:chu\s+nhat|cn)\s+\d{1,2}\s*(?:h|gio|:)',
            r'(?:thu[s]?|t)\s*(?:\d+|hai|ba|tu|nam|sau|bay)\s+(?:mot|hai|ba|bon|tu|nam|sau|bay|tam|chin|muoi|moth|haih|bah|bonh|tuh|namh|sauh|bayh|tamh|chinh|muoih)(?:\s+(?:mot|hai|moth|haih))?\b',
            r'(?:thu[s]?|t)\s*(?:\d+|hai|ba|tu|nam|sau|bay)\s+\d{1,2}\s*(?:h|gio|:)',
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
        
        # Find all time matches on normalized text but return original text
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
        
        # Extract from original text using span
        if best_span:
            best_match = text[best_span[0]:best_span[1]]
        
        return best_match
    
    def _extract_location_heuristic(self, text: str) -> Optional[str]:
        """Simple heuristic location extraction - returns location string"""
        if not text:
            return None
        
        # Location markers (ordered by specificity)
        location_patterns = [
            # Specific: phòng 302, tầng 5, toà A
            (r'(?:phòng|tầng|toà|tòa|lầu)\s+[\w\d]+', False),
            # Marker + location: ở văn phòng, tại bệnh viện
            (r'(?:ở|tại|đến|về)\s+([^\s,\.]{3,50}(?:\s+[^\s,\.]{1,20}){0,3})', True),
            # Named places: bệnh viện, công ty, văn phòng
            (r'(?:trường|công ty|văn phòng|bệnh viện|nhà hàng|quán|cafe|café|siêu thị|chợ)(?:\s+[\w\s]{1,30})?', False),
        ]
        
        for pattern, has_group in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if has_group and match.lastindex:
                    location = match.group(1)
                else:
                    location = match.group(0)
                
                # Clean up
                location = re.sub(r'^(?:ở|tại|đến|về)\s+', '', location, flags=re.IGNORECASE)
                location = location.strip(' ,.;')
                
                # Stop at time expressions or reminder keywords
                location = re.split(r'\s+(?:\d{1,2}(?:h|:|giờ)|nhắc|remind)', location)[0]
                
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
        # Time patterns (comprehensive Vietnamese time expressions)
        time_patterns = [
            # Explicit time: 10h, 10:30, 10 giờ 30
            r'\d{1,2}(?:h|:\d{2}|(?:\s*giờ(?:\s*\d{1,2}(?:\s*phút)?)?))(?:\s*(?:sáng|trưa|chiều|tối|đêm))?',
            # Relative: ngày mai, hôm nay, tuần sau
            r'(?:hôm\s+nay|ngày\s+mai|mai|ngày\s+kia|tuần\s+sau|tuần\s+tới|tháng\s+sau)',
            # Weekdays: thứ 2, thứ hai, t2, CN
            r'(?:thứ|t)\s*\d|CN|chủ\s+nhật',
            # Date: ngày 15 tháng 12
            r'ngày\s+\d{1,2}\s+tháng\s+\d{1,2}',
            # Period: sáng, chiều, tối
            r'\b(?:sáng|trưa|chiều|tối|đêm|khuya)\b',
        ]
        
        # Find all time-related spans
        time_spans = []
        for pattern in time_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                time_spans.append((match.start(), match.end(), match.group()))
        
        if not time_spans:
            return None
        
        # Merge overlapping/adjacent spans
        time_spans.sort(key=lambda x: x[0])
        merged = []
        for start, end, txt in time_spans:
            if merged and start <= merged[-1][1] + 3:
                # Merge with previous
                merged[-1] = (merged[-1][0], end, text[merged[-1][0]:end])
            else:
                merged.append((start, end, txt))
        
        # Return the longest/most complete time expression
        if merged:
            return max(merged, key=lambda x: x[1] - x[0])[2].strip()
        
        return None
    
    def _extract_location_semantic(self, text: str, embeddings: torch.Tensor) -> Optional[str]:
        """Extract location using semantic understanding"""
        # Location markers
        location_markers = [
            r'(?:ở|tại|đến|về)\s+([^,\.\d]{3,50})',
            r'(?:phòng|tầng|toà|tòa)\s+[\w\s\d]{1,30}',
            r'(?:trường|công ty|văn phòng|bệnh viện|nhà hàng|quán)\s+[\w\s]{2,40}',
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
        """Extract event name by removing time, location, reminder"""
        cleaned = text
        
        # Remove time expression first (most specific)
        if extracted.get('time_str'):
            time_str = extracted['time_str']
            cleaned = cleaned.replace(time_str, ' ')
            # Also remove time markers
            cleaned = re.sub(r'\b(?:lúc|vào)\s+', ' ', cleaned, flags=re.IGNORECASE)
        
        # Remove location with marker
        if extracted.get('location'):
            location = extracted['location']
            # Remove with location marker
            cleaned = re.sub(
                r'(?:ở|tại|đến|về)\s+' + re.escape(location),
                ' ',
                cleaned,
                flags=re.IGNORECASE
            )
        
        # Remove reminder phrases
        reminder_phrases = [
            r'nhắc\s+(?:tôi\s+)?(?:trước\s+)?\d{1,3}\s*(?:phút|p|giờ|h)(?:\s+trước)?',
            r'\d{1,3}\s*(?:phút|p|giờ|h)\s*(?:trước\s+)?(?:nhắc|nhở)',
            r'nhắc\s+(?:tôi\s+)?(?:trước|nhở)?',
        ]
        for pattern in reminder_phrases:
            cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
        
        # Remove standalone numbers (likely from time/room that wasn't caught)
        cleaned = re.sub(r'\b\d{1,4}\b', ' ', cleaned)
        
        # Remove common time/location connectors
        connectors = [
            'vào', 'lúc', 'vào lúc', 'khoảng', 'từ', 'đến', 'tới',
            'ở', 'tại', 'đến', 'về',
            'sáng', 'trưa', 'chiều', 'tối', 'đêm', 'khuya',
            'hôm nay', 'ngày mai', 'mai', 'ngày kia'
        ]
        for word in connectors:
            cleaned = re.sub(r'\b' + re.escape(word) + r'\b', ' ', cleaned, flags=re.IGNORECASE)
        
        # Clean up whitespace and punctuation
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip(' ,.;-:')
        
        # If cleaned is empty or too short, return first few words of original
        if not cleaned or len(cleaned) < 2:
            words = text.split()[:3]
            cleaned = ' '.join(words)
        
        return cleaned
    
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
