"""
Evaluation script for SafeType+ system.
Run this to evaluate the system on labeled datasets.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from evaluation.metrics import MetricsCalculator
from evaluation.dataset_loader import DatasetLoader
from services.risk_engine import RiskEngine
from services.pii_regex import PIIRegexDetector
from services.pii_ner import PIINERDetector
from services.nlp_intent import NLPIntentClassifier
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def evaluate_system(dataset_path: str, output_report: str = None):
    """
    Evaluate SafeType+ system on a labeled dataset.
    
    Args:
        dataset_path: Path to dataset file (JSON or CSV)
        output_report: Optional path to save evaluation report
    """
    logger.info("=== SafeType+ Evaluation ===")
    
    # Initialize components
    loader = DatasetLoader()
    metrics_calc = MetricsCalculator()
    
    # Initialize detection services
    pii_regex = PIIRegexDetector()
    pii_ner = PIINERDetector(Config.SPACY_MODEL)
    nlp_intent = NLPIntentClassifier(Config.NLP_MODEL)
    risk_engine = RiskEngine(Config())
    
    # Load dataset
    logger.info(f"Loading dataset from: {dataset_path}")
    
    if dataset_path.endswith('.json'):
        texts, labels = loader.load_json_dataset(dataset_path)
    elif dataset_path.endswith('.csv'):
        texts, labels = loader.load_csv_dataset(dataset_path)
    else:
        logger.error("Unsupported file format. Use .json or .csv")
        return
    
    if not texts:
        logger.error("No data loaded. Exiting.")
        return
    
    # Show dataset statistics
    distribution = loader.get_label_distribution(labels)
    logger.info(f"Dataset size: {len(texts)} samples")
    logger.info(f"Label distribution: {distribution}")
    
    # Evaluate each sample
    predictions = []
    risk_scores = []
    
    logger.info("Running predictions...")
    
    for i, (text, true_label) in enumerate(zip(texts, labels)):
        if (i + 1) % 10 == 0:
            logger.info(f"Processed {i + 1}/{len(texts)} samples")
        
        try:
            # Run detection pipeline
            regex_detections = pii_regex.detect_pii(text)
            ner_detections = pii_ner.detect_entities(text, "en")
            all_pii = pii_ner.combine_with_regex(regex_detections, ner_detections)
            
            intent_probs = nlp_intent.classify_intent(text, "en")
            
            risk_assessment = risk_engine.compute_risk(
                pii_detections=all_pii,
                intent_probabilities=intent_probs,
                text_length=len(text)
            )
            
            risk_score = risk_assessment['risk_score']
            risk_scores.append(risk_score)
            
            # Convert risk score to binary prediction
            # Threshold: 0.5 (adjust as needed)
            prediction = 1 if risk_score >= 0.5 else 0
            predictions.append(prediction)
        
        except Exception as e:
            logger.error(f"Error processing sample {i}: {e}")
            predictions.append(0)  # Default to benign on error
            risk_scores.append(0.0)
    
    # Compute metrics
    logger.info("\n=== Computing Metrics ===")
    
    binary_metrics = metrics_calc.compute_binary_metrics(
        y_true=labels,
        y_pred=predictions,
        positive_label=1
    )
    
    # Compute regression metrics for risk scores
    # Convert labels to float for regression (0.0 = benign, 1.0 = phishing)
    true_scores = [float(label) for label in labels]
    regression_metrics = metrics_calc.compute_regression_metrics(
        y_true=true_scores,
        y_pred=risk_scores
    )
    
    # Generate report
    report = metrics_calc.generate_classification_report(
        binary_metrics,
        dataset_name=os.path.basename(dataset_path)
    )
    
    print("\n" + report)
    
    print("\n=== Risk Score Regression Metrics ===")
    print(f"MAE:  {regression_metrics['mae']:.4f}")
    print(f"RMSE: {regression_metrics['rmse']:.4f}")
    print(f"R²:   {regression_metrics['r2_score']:.4f}")
    
    # Save report if requested
    if output_report:
        try:
            with open(output_report, 'w') as f:
                f.write(report)
                f.write("\n\n=== Risk Score Regression Metrics ===\n")
                f.write(f"MAE:  {regression_metrics['mae']:.4f}\n")
                f.write(f"RMSE: {regression_metrics['rmse']:.4f}\n")
                f.write(f"R²:   {regression_metrics['r2_score']:.4f}\n")
            
            logger.info(f"Report saved to: {output_report}")
        except Exception as e:
            logger.error(f"Could not save report: {e}")
    
    return binary_metrics, regression_metrics

def create_sample_dataset_if_needed():
    """Create a sample dataset if none exists."""
    sample_path = os.path.join(
        os.path.dirname(__file__),
        'sample_dataset.json'
    )
    
    if not os.path.exists(sample_path):
        logger.info("Creating sample dataset...")
        loader = DatasetLoader()
        loader.create_sample_dataset(sample_path, format='json')
        logger.info(f"Sample dataset created at: {sample_path}")
    
    return sample_path

if __name__ == "__main__":
    # Check if dataset path provided
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        # Create and use sample dataset
        dataset_path = create_sample_dataset_if_needed()
    
    # Optional: output report path
    output_report = sys.argv[2] if len(sys.argv) > 2 else "evaluation_report.txt"
    
    # Run evaluation
    evaluate_system(dataset_path, output_report)
