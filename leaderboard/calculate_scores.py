# leaderboard/calculate_scores.py
from pathlib import Path
import pandas as pd
from sklearn.metrics import f1_score
import os

# Ground truth labels
GROUND_TRUTH = Path(__file__).resolve().parent.parent / "data" / "train.csv"

def calculate_scores(submission_path: Path):
    """
    Compute F1 score for a single CSV submission and return as dict
    """
    print(f"DEBUG: calculate_scores called with submission: {submission_path}")
    
    # Check if file exists
    if not submission_path.exists():
        raise FileNotFoundError(f"Submission file not found: {submission_path}")
    
    print(f"DEBUG: Loading submission from {submission_path}")
    submission_df = pd.read_csv(submission_path)
    
    print(f"DEBUG: Submission columns: {list(submission_df.columns)}")
    print(f"DEBUG: Submission shape: {submission_df.shape}")
    print(f"DEBUG: First few rows of submission:")
    print(submission_df.head(3).to_string())
    
    # Check for graph_index column
    if "graph_index" not in submission_df.columns:
        raise ValueError(f"Submission missing required column: graph_index. Found columns: {list(submission_df.columns)}")
    
    # Find the prediction column - try multiple possible names
    possible_pred_cols = ["label", "prediction", "target", "predictions", "Label", "Prediction", "Target", "y_pred", "pred"]
    
    pred_col = None
    for col in possible_pred_cols:
        if col in submission_df.columns:
            pred_col = col
            print(f"DEBUG: Found prediction column: '{col}'")
            break
    
    if pred_col is None:
        # If none of the expected columns found, use the second column (assuming first is graph_index)
        other_cols = [col for col in submission_df.columns if col != "graph_index"]
        if len(other_cols) == 1:
            pred_col = other_cols[0]
            print(f"DEBUG: Using '{pred_col}' as prediction column (only non-graph_index column)")
        else:
            raise ValueError(
                f"Could not find prediction column. Submission has columns: {list(submission_df.columns)}. "
                f"Expected one of: {possible_pred_cols}"
            )
    
    # Load ground truth
    print(f"DEBUG: Loading ground truth from {GROUND_TRUTH}")
    if not GROUND_TRUTH.exists():
        raise FileNotFoundError(f"Ground truth file not found: {GROUND_TRUTH}")
    
    gt_df = pd.read_csv(GROUND_TRUTH)
    print(f"DEBUG: Ground truth columns: {list(gt_df.columns)}")
    print(f"DEBUG: Ground truth shape: {gt_df.shape}")
    print(f"DEBUG: First few rows of ground truth:")
    print(gt_df.head(3).to_string())
    
    # Find ground truth label column
    possible_truth_cols = ["label", "target", "Label", "Target", "y_true", "truth", "ground_truth"]
    
    truth_col = None
    for col in possible_truth_cols:
        if col in gt_df.columns:
            truth_col = col
            print(f"DEBUG: Found ground truth column: '{col}'")
            break
    
    if truth_col is None:
        # If none of the expected columns found, use the second column (assuming first is graph_index)
        other_cols = [col for col in gt_df.columns if col != "graph_index"]
        if len(other_cols) == 1:
            truth_col = other_cols[0]
            print(f"DEBUG: Using '{truth_col}' as ground truth column (only non-graph_index column)")
        else:
            raise ValueError(f"Could not find ground truth column in {GROUND_TRUTH}. Found columns: {list(gt_df.columns)}")
    
    # Merge on graph_index
    print(f"DEBUG: Merging on graph_index...")
    merged = submission_df.merge(gt_df, on="graph_index", how="inner", suffixes=('_sub', '_gt'))
    print(f"DEBUG: Merged shape: {merged.shape}")
    
    if len(merged) == 0:
        raise ValueError("No matching graph_index values found between submission and ground truth")
    
    # Get the prediction and truth columns
    # Handle column name conflicts after merge
    if pred_col in merged.columns:
        y_pred = merged[pred_col]
    elif f"{pred_col}_sub" in merged.columns:
        y_pred = merged[f"{pred_col}_sub"]
    else:
        raise ValueError(f"Could not find prediction column '{pred_col}' in merged data")
    
    if truth_col in merged.columns:
        y_true = merged[truth_col]
    elif f"{truth_col}_gt" in merged.columns:
        y_true = merged[f"{truth_col}_gt"]
    else:
        raise ValueError(f"Could not find ground truth column '{truth_col}' in merged data")
    
    print(f"DEBUG: y_pred sample (first 5): {y_pred.head().tolist()}")
    print(f"DEBUG: y_true sample (first 5): {y_true.head().tolist()}")
    print(f"DEBUG: y_pred unique values: {y_pred.unique()}")
    print(f"DEBUG: y_true unique values: {y_true.unique()}")
    
    # Calculate F1 score
    try:
        f1 = f1_score(y_true, y_pred, average="macro")
        print(f"DEBUG: Calculated F1 score: {f1}")
    except Exception as e:
        print(f"DEBUG: Error calculating F1 score: {e}")
        raise
    
    return {"validation_f1_score": f1}


def calculate_scores_pair(ideal_path: Path, perturbed_path: Path):
    """
    Compute ideal, perturbed F1 and robustness gap
    """
    f1_ideal = calculate_scores(ideal_path)["validation_f1_score"]
    f1_pert = calculate_scores(perturbed_path)["validation_f1_score"]
    robustness_gap = f1_ideal - f1_pert
    return {
        "validation_f1_ideal": f1_ideal,
        "validation_f1_perturbed": f1_pert,
        "robustness_gap": robustness_gap
    }
