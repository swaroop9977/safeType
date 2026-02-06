"""
Metrics computation for SafeType+ evaluation.
Computes accuracy, precision, recall, F1-score for academic reporting.
"""

from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class MetricsCalculator:
    """
    Computes classification metrics for model evaluation.
    Critical for academic validation of the system.
    """
    
    def __init__(self):
        """Initialize metrics calculator."""
        self.metrics_history = []
    
    def compute_binary_metrics(
        self,
        y_true: List[int],
        y_pred: List[int],
        positive_label: int = 1
    ) -> Dict:
        """
        Compute binary classification metrics.
        
        Args:
            y_true: True labels (0 or 1)
            y_pred: Predicted labels (0 or 1)
            positive_label: Which label is "positive" (default 1)
            
        Returns:
            Dict with accuracy, precision, recall, F1, etc.
        """
        if len(y_true) != len(y_pred):
            raise ValueError("y_true and y_pred must have same length")
        
        if not y_true:
            return self._empty_metrics()
        
        # Compute confusion matrix elements
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == positive_label and p == positive_label)
        tn = sum(1 for t, p in zip(y_true, y_pred) if t != positive_label and p != positive_label)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != positive_label and p == positive_label)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == positive_label and p != positive_label)
        
        total = len(y_true)
        
        # Compute metrics
        accuracy = (tp + tn) / total if total > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        
        # F1 Score (harmonic mean of precision and recall)
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # F2 Score (weights recall higher than precision)
        beta = 2
        f2 = ((1 + beta**2) * precision * recall) / ((beta**2 * precision) + recall) if (precision + recall) > 0 else 0.0
        
        metrics = {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "f2_score": round(f2, 4),
            "specificity": round(specificity, 4),
            "confusion_matrix": {
                "true_positives": tp,
                "true_negatives": tn,
                "false_positives": fp,
                "false_negatives": fn
            },
            "support": {
                "positive": tp + fn,
                "negative": tn + fp,
                "total": total
            }
        }
        
        return metrics
    
    def compute_multiclass_metrics(
        self,
        y_true: List[int],
        y_pred: List[int],
        num_classes: int = None
    ) -> Dict:
        """
        Compute multiclass classification metrics.
        
        Args:
            y_true: True class labels
            y_pred: Predicted class labels
            num_classes: Number of classes (inferred if None)
            
        Returns:
            Dict with macro/micro averaged metrics
        """
        if len(y_true) != len(y_pred):
            raise ValueError("y_true and y_pred must have same length")
        
        if not y_true:
            return self._empty_metrics()
        
        # Infer number of classes
        if num_classes is None:
            num_classes = max(max(y_true), max(y_pred)) + 1
        
        # Compute per-class metrics
        per_class_metrics = []
        
        for class_idx in range(num_classes):
            # Treat as binary: this class vs all others
            y_true_binary = [1 if y == class_idx else 0 for y in y_true]
            y_pred_binary = [1 if y == class_idx else 0 for y in y_pred]
            
            class_metrics = self.compute_binary_metrics(y_true_binary, y_pred_binary)
            class_metrics['class'] = class_idx
            per_class_metrics.append(class_metrics)
        
        # Compute macro averages (unweighted mean across classes)
        macro_precision = sum(m['precision'] for m in per_class_metrics) / num_classes
        macro_recall = sum(m['recall'] for m in per_class_metrics) / num_classes
        macro_f1 = sum(m['f1_score'] for m in per_class_metrics) / num_classes
        
        # Compute micro averages (aggregate then compute)
        total_tp = sum(m['confusion_matrix']['true_positives'] for m in per_class_metrics)
        total_fp = sum(m['confusion_matrix']['false_positives'] for m in per_class_metrics)
        total_fn = sum(m['confusion_matrix']['false_negatives'] for m in per_class_metrics)
        
        micro_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        micro_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        micro_f1 = (2 * micro_precision * micro_recall) / (micro_precision + micro_recall) if (micro_precision + micro_recall) > 0 else 0.0
        
        # Overall accuracy
        correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
        accuracy = correct / len(y_true)
        
        return {
            "accuracy": round(accuracy, 4),
            "macro_precision": round(macro_precision, 4),
            "macro_recall": round(macro_recall, 4),
            "macro_f1": round(macro_f1, 4),
            "micro_precision": round(micro_precision, 4),
            "micro_recall": round(micro_recall, 4),
            "micro_f1": round(micro_f1, 4),
            "per_class_metrics": per_class_metrics,
            "num_classes": num_classes,
            "total_samples": len(y_true)
        }
    
    def compute_regression_metrics(
        self,
        y_true: List[float],
        y_pred: List[float]
    ) -> Dict:
        """
        Compute regression metrics for risk score evaluation.
        
        Args:
            y_true: True risk scores
            y_pred: Predicted risk scores
            
        Returns:
            Dict with MAE, MSE, RMSE, R²
        """
        import math
        
        if len(y_true) != len(y_pred):
            raise ValueError("y_true and y_pred must have same length")
        
        if not y_true:
            return self._empty_regression_metrics()
        
        n = len(y_true)
        
        # Mean Absolute Error
        mae = sum(abs(t - p) for t, p in zip(y_true, y_pred)) / n
        
        # Mean Squared Error
        mse = sum((t - p) ** 2 for t, p in zip(y_true, y_pred)) / n
        
        # Root Mean Squared Error
        rmse = math.sqrt(mse)
        
        # R² Score (coefficient of determination)
        mean_true = sum(y_true) / n
        ss_tot = sum((t - mean_true) ** 2 for t in y_true)
        ss_res = sum((t - p) ** 2 for t, p in zip(y_true, y_pred))
        
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        
        return {
            "mae": round(mae, 4),
            "mse": round(mse, 4),
            "rmse": round(rmse, 4),
            "r2_score": round(r2, 4),
            "total_samples": n
        }
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics dict."""
        return {
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "error": "No data provided"
        }
    
    def _empty_regression_metrics(self) -> Dict:
        """Return empty regression metrics dict."""
        return {
            "mae": 0.0,
            "mse": 0.0,
            "rmse": 0.0,
            "r2_score": 0.0,
            "error": "No data provided"
        }
    
    def generate_classification_report(
        self,
        metrics: Dict,
        dataset_name: str = "test"
    ) -> str:
        """
        Generate formatted classification report for documentation.
        
        Args:
            metrics: Computed metrics dict
            dataset_name: Name of dataset
            
        Returns:
            Formatted report string
        """
        report_lines = [
            f"Classification Report - {dataset_name}",
            "=" * 50,
            f"Accuracy:   {metrics.get('accuracy', 0):.4f}",
            f"Precision:  {metrics.get('precision', 0):.4f}",
            f"Recall:     {metrics.get('recall', 0):.4f}",
            f"F1-Score:   {metrics.get('f1_score', 0):.4f}",
            f"F2-Score:   {metrics.get('f2_score', 0):.4f}",
            "",
            "Confusion Matrix:",
            f"  TP: {metrics.get('confusion_matrix', {}).get('true_positives', 0)}",
            f"  TN: {metrics.get('confusion_matrix', {}).get('true_negatives', 0)}",
            f"  FP: {metrics.get('confusion_matrix', {}).get('false_positives', 0)}",
            f"  FN: {metrics.get('confusion_matrix', {}).get('false_negatives', 0)}",
            "",
            f"Total Samples: {metrics.get('support', {}).get('total', 0)}",
            "=" * 50
        ]
        
        return "\n".join(report_lines)
    
    def compare_models(
        self,
        model_metrics: Dict[str, Dict]
    ) -> Dict:
        """
        Compare metrics across multiple models.
        
        Args:
            model_metrics: Dict mapping model names to their metrics
            
        Returns:
            Comparison dict with best model info
        """
        if not model_metrics:
            return {"error": "No models to compare"}
        
        # Find best model by F1 score
        best_f1_model = max(
            model_metrics.items(),
            key=lambda x: x[1].get('f1_score', 0)
        )
        
        # Find best model by accuracy
        best_acc_model = max(
            model_metrics.items(),
            key=lambda x: x[1].get('accuracy', 0)
        )
        
        comparison = {
            "best_f1": {
                "model": best_f1_model[0],
                "f1_score": best_f1_model[1].get('f1_score', 0)
            },
            "best_accuracy": {
                "model": best_acc_model[0],
                "accuracy": best_acc_model[1].get('accuracy', 0)
            },
            "all_models": {
                name: {
                    "accuracy": metrics.get('accuracy', 0),
                    "f1_score": metrics.get('f1_score', 0)
                }
                for name, metrics in model_metrics.items()
            }
        }
        
        return comparison
