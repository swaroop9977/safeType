"""
Dataset loader for evaluation.
Loads labeled datasets for phishing/benign classification testing.
"""

from typing import List, Dict, Tuple
import json
import csv
import logging

logger = logging.getLogger(__name__)

class DatasetLoader:
    """
    Loads and manages datasets for evaluation.
    Supports CSV and JSON formats with flexible schema.
    """
    
    def __init__(self):
        """Initialize dataset loader."""
        self.datasets = {}
    
    def load_csv_dataset(
        self,
        filepath: str,
        text_column: str = 'text',
        label_column: str = 'label'
    ) -> Tuple[List[str], List[int]]:
        """
        Load dataset from CSV file.
        
        Args:
            filepath: Path to CSV file
            text_column: Name of column containing text
            label_column: Name of column containing labels
            
        Returns:
            Tuple of (texts, labels)
        """
        texts = []
        labels = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    if text_column in row and label_column in row:
                        texts.append(row[text_column])
                        # Convert label to int
                        label = self._parse_label(row[label_column])
                        labels.append(label)
            
            logger.info(f"Loaded {len(texts)} samples from {filepath}")
            return texts, labels
        
        except FileNotFoundError:
            logger.error(f"Dataset file not found: {filepath}")
            return [], []
        except Exception as e:
            logger.error(f"Error loading CSV dataset: {e}")
            return [], []
    
    def load_json_dataset(
        self,
        filepath: str,
        text_key: str = 'text',
        label_key: str = 'label'
    ) -> Tuple[List[str], List[int]]:
        """
        Load dataset from JSON file.
        
        Expected format:
        [
            {"text": "...", "label": 0},
            {"text": "...", "label": 1}
        ]
        
        Args:
            filepath: Path to JSON file
            text_key: Key for text field
            label_key: Key for label field
            
        Returns:
            Tuple of (texts, labels)
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                logger.error("JSON must contain a list of samples")
                return [], []
            
            texts = []
            labels = []
            
            for item in data:
                if text_key in item and label_key in item:
                    texts.append(item[text_key])
                    label = self._parse_label(item[label_key])
                    labels.append(label)
            
            logger.info(f"Loaded {len(texts)} samples from {filepath}")
            return texts, labels
        
        except FileNotFoundError:
            logger.error(f"Dataset file not found: {filepath}")
            return [], []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            return [], []
        except Exception as e:
            logger.error(f"Error loading JSON dataset: {e}")
            return [], []
    
    def _parse_label(self, label) -> int:
        """
        Parse label to integer.
        
        Handles various formats:
        - Integers: 0, 1, 2, ...
        - Strings: "0", "1", "benign", "phishing", etc.
        
        Args:
            label: Label value
            
        Returns:
            Integer label
        """
        if isinstance(label, int):
            return label
        
        if isinstance(label, str):
            label_lower = label.lower().strip()
            
            # Check for common label names
            if label_lower in ['benign', 'safe', 'normal', 'legitimate', 'ham']:
                return 0
            elif label_lower in ['phishing', 'malicious', 'spam', 'suspicious']:
                return 1
            else:
                # Try to parse as integer
                try:
                    return int(label)
                except ValueError:
                    logger.warning(f"Could not parse label: {label}, defaulting to 0")
                    return 0
        
        return 0
    
    def create_sample_dataset(
        self,
        output_path: str,
        format: str = 'json'
    ):
        """
        Create a sample dataset for testing.
        
        Args:
            output_path: Path to save dataset
            format: 'json' or 'csv'
        """
        samples = [
            {
                "text": "Hi, I hope you're doing well!",
                "label": 0,
                "category": "benign"
            },
            {
                "text": "Your account has been suspended! Click here to verify immediately!",
                "label": 1,
                "category": "phishing"
            },
            {
                "text": "Meeting scheduled for tomorrow at 2 PM",
                "label": 0,
                "category": "benign"
            },
            {
                "text": "URGENT: Confirm your credit card details now or account will be closed!",
                "label": 1,
                "category": "phishing"
            },
            {
                "text": "Thanks for the update",
                "label": 0,
                "category": "benign"
            },
            {
                "text": "You've won $1,000,000! Claim your prize by providing your SSN and bank details.",
                "label": 1,
                "category": "phishing"
            },
            {
                "text": "Please find the attached report for your review",
                "label": 0,
                "category": "benign"
            },
            {
                "text": "Your tax refund is ready. Update your information at this link immediately.",
                "label": 1,
                "category": "phishing"
            }
        ]
        
        try:
            if format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(samples, f, indent=2)
            elif format == 'csv':
                with open(output_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['text', 'label', 'category'])
                    writer.writeheader()
                    writer.writerows(samples)
            
            logger.info(f"Created sample dataset at {output_path}")
        
        except Exception as e:
            logger.error(f"Error creating sample dataset: {e}")
    
    def split_dataset(
        self,
        texts: List[str],
        labels: List[int],
        train_ratio: float = 0.8
    ) -> Tuple[List[str], List[int], List[str], List[int]]:
        """
        Split dataset into train and test sets.
        
        Args:
            texts: List of text samples
            labels: List of labels
            train_ratio: Ratio of training data (default 0.8)
            
        Returns:
            Tuple of (train_texts, train_labels, test_texts, test_labels)
        """
        if len(texts) != len(labels):
            raise ValueError("texts and labels must have same length")
        
        # Simple split without shuffling (for reproducibility)
        split_idx = int(len(texts) * train_ratio)
        
        train_texts = texts[:split_idx]
        train_labels = labels[:split_idx]
        test_texts = texts[split_idx:]
        test_labels = labels[split_idx:]
        
        logger.info(
            f"Split dataset: {len(train_texts)} train, {len(test_texts)} test"
        )
        
        return train_texts, train_labels, test_texts, test_labels
    
    def get_label_distribution(
        self,
        labels: List[int]
    ) -> Dict[int, int]:
        """
        Get distribution of labels in dataset.
        
        Args:
            labels: List of labels
            
        Returns:
            Dict mapping label to count
        """
        distribution = {}
        for label in labels:
            distribution[label] = distribution.get(label, 0) + 1
        
        return distribution
    
    def balance_dataset(
        self,
        texts: List[str],
        labels: List[int],
        method: str = 'undersample'
    ) -> Tuple[List[str], List[int]]:
        """
        Balance dataset by undersampling or oversampling.
        
        Args:
            texts: List of text samples
            labels: List of labels
            method: 'undersample' or 'oversample'
            
        Returns:
            Balanced (texts, labels)
        """
        # Get label distribution
        distribution = self.get_label_distribution(labels)
        
        if method == 'undersample':
            # Undersample to match smallest class
            min_count = min(distribution.values())
            
            balanced_texts = []
            balanced_labels = []
            label_counts = {label: 0 for label in distribution.keys()}
            
            for text, label in zip(texts, labels):
                if label_counts[label] < min_count:
                    balanced_texts.append(text)
                    balanced_labels.append(label)
                    label_counts[label] += 1
            
            logger.info(f"Undersampled to {len(balanced_texts)} samples")
            return balanced_texts, balanced_labels
        
        elif method == 'oversample':
            # Simple duplication oversampling
            max_count = max(distribution.values())
            
            # Group by label
            label_groups = {}
            for text, label in zip(texts, labels):
                if label not in label_groups:
                    label_groups[label] = []
                label_groups[label].append(text)
            
            # Oversample each group
            balanced_texts = []
            balanced_labels = []
            
            for label, group in label_groups.items():
                current_count = len(group)
                # Repeat samples to reach max_count
                repetitions = max_count // current_count
                remainder = max_count % current_count
                
                balanced_texts.extend(group * repetitions)
                balanced_texts.extend(group[:remainder])
                balanced_labels.extend([label] * max_count)
            
            logger.info(f"Oversampled to {len(balanced_texts)} samples")
            return balanced_texts, balanced_labels
        
        else:
            logger.warning(f"Unknown balancing method: {method}")
            return texts, labels
