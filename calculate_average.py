import pandas as pd

# read data
def calculate_model_scores(file_name):
    df = pd.read_csv(file_name)
    # Group the DataFrame by the 'Model' column and compute the mean of the relevant columns
    model_scores = df.groupby('model_name')[["bert_score_text_generated_summary", "bert_score_summary_generated_summary","rouge1_scores_summary_generated_summary", "rouge1_scores_text_generated_summary", "rouge2_scores_summary_generated_summary", "rouge2_scores_text_generated_summary", "rougeL_scores_summary_generated_summary", "rougeL_scores_text_generated_summary"]].mean()
    model_scores.reset_index(inplace=True)
    ranks = model_scores.rank(method='min').mean(axis=1)
    best_model = ranks.idxmin()
    worst_model = ranks.idxmax()

    print(f"Best model: {best_model}")
    print(f"Worst model: {worst_model}")

    model_scores.to_csv(f"scores_{file_name}.csv", index=False)
    return model_scores


if __name__ == "__main__":
    scores = calculate_model_scores("final_hugging_face_param_search.csv")
    print(scores)