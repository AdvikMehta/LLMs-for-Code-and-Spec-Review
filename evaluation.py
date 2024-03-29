"""

_project_ : LLMs for Code and Spec Review

_team_ : Cmput469, T5-InnovAiTors

_reference_ : 
https://www.freecodecamp.org/news/what-is-rouge-and-how-it-works-for-evaluation-of-summaries-e059fb8ac840/
[ROUGE: A Package for Automatic Evaluation of Summaries](https://aclanthology.org/W04-1013) (Lin, 2004)

_description_ :
The functions defined in the following script can be used to calculate similarity scores,
using recall and precision values, for comparing answers generated by our model to the golden ref.

recall = number_of_overlapping_words / total_words_in_reference_summary
precision = number_of_overlapping_words / total_words_in_system_summary

"""

from typing import List, Tuple
import argparse
import os, sys

import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
from math import sqrt
current_path = os.path.realpath(__file__)
# Load the English NLP pipeline
import spacy
nlp = spacy.load("en_core_web_sm")



def ngram(system_answer: str, ref_answer: str, n: int) -> List[str]:
    """
    Measures unigram, bigram, trigram and higher order n-gram overlap.
    Returns n-gram -> list of strings, where each string has n words
    common to both the provided arguments.
    """
    common_strings = []
    system_strings = n_split_answer(system_answer, n)
    ref_strings = n_split_answer(ref_answer, n)
    for ref_string in ref_strings:
        if ref_string in system_strings:
            common_strings.append(ref_string)

    return list(set(common_strings))

    return common_strings



def n_split_answer(answer: str, n: int) -> List[str]:
    """
    Splits the answer string into sub-strings of length n in order
    """
    n_size_strings = []

    if answer:
        answer_string = answer.split()
        answer_string_size = len(answer_string)
        for i in range(answer_string_size):
            if i + n <= answer_string_size:
                n_size_string = ""
                for j in range(n):
                    n_size_string += answer_string[i+j].strip("!.,;:'\"") + " "
                n_size_strings.append(n_size_string.strip())

    answer_string = answer.split()
    answer_string_size = len(answer_string)
    for i in range(answer_string_size):
        if i + n <= answer_string_size:
            n_size_string = ""
            for j in range(n):
                n_size_string += answer_string[i+j].strip("!.,;:'\"") + " "
            n_size_strings.append(n_size_string.strip())

    return n_size_strings


def lcs(system_answer_list: List[str], ref_answer_list: List[str]) -> List[str]:
    """
    Measures and returns list of longest matching sequences of words using LCS
    """
    system_answer_size, ref_answer_size = len(system_answer_list), len(ref_answer_list)
    # Initialize a 2D table to store the lengths of common subsequences
    lcs_table = [[0 for j in range(ref_answer_size+1)] for i in range(system_answer_size+1)]

    # Fill in the table using dynamic programming
    for i in range(1, system_answer_size+1):
        for j in range(1, ref_answer_size+1):
            if system_answer_list[i-1] == ref_answer_list[j-1]:
                lcs_table[i][j] = 1 + lcs_table[i-1][j-1]
            else:
                lcs_table[i][j] = max(lcs_table[i-1][j], lcs_table[i][j-1])

    lcs_result = []
    i, j = system_answer_size, ref_answer_size
    # Reconstruct and return the longest common subsequence
    while i > 0 and j > 0:
        if system_answer_list[i-1] == ref_answer_list[j-1]:
            lcs_result.append(system_answer_list[i-1])
            i -= 1
            j -= 1
        elif lcs_table[i-1][j] > lcs_table[i][j-1]:
            i -= 1
        else:
            j -= 1

    return lcs_result[::-1]


def skip_words(answer: str) -> List[str]:
    """
    Returns a list of 2 words from answer by allowing words separated by one-or-more other words
    """
    words_with_gaps = []

    if answer:
        answer_string = answer.split()
        answer_string_size = len(answer_string)
        for i in range(answer_string_size):
            current_string = answer_string[i]
            for j in range(i+1, answer_string_size):
                    if j < answer_string_size:
                        string_to_add = current_string + " " + answer_string[j].strip("!.,;:'\"")
                        words_with_gaps.append(string_to_add.strip())

    answer_string = answer.split()
    answer_string_size = len(answer_string)
    for i in range(answer_string_size):
        current_string = answer_string[i]
        for j in range(i+1, answer_string_size):
                if j < answer_string_size:
                    string_to_add = current_string + " " + answer_string[j].strip("!.,;:'\"")
                    words_with_gaps.append(string_to_add.strip())

    return words_with_gaps


def rouge_n(system_answer: str, ref_answer: str, n: int) -> Tuple[float, float]:
    """
    Calculates and returns recall and precision for system's answer given the reference answer
    using ROUGE-N approach
    """
    recall, precision = 0, 0
    number_of_overlapping_words = len(ngram(system_answer, ref_answer, n))
    total_words_in_reference_summary = len(n_split_answer(ref_answer, n))
    total_words_in_system_summary = len(n_split_answer(system_answer, n))
    if total_words_in_reference_summary:
        recall = number_of_overlapping_words / total_words_in_reference_summary
    if total_words_in_system_summary:
        precision = number_of_overlapping_words / total_words_in_system_summary
    return (round(recall, 4), round(precision, 4))


def rouge_l(system_answer: str, ref_answer: str) -> Tuple[float, float]:
    """
    Calculates and returns recall and precision for system's answer given the reference answer
    using ROUGE-L approach
    """
    recall, precision = 0, 0
    system_answer_list = n_split_answer(system_answer, 1)
    ref_answer_list = n_split_answer(ref_answer, 1)
    _lcs = lcs(system_answer_list, ref_answer_list)
    if _lcs:
        number_of_words_in_lcs = len(_lcs)
        total_words_in_reference_summary = len(ref_answer_list)
        total_words_in_system_summary = len(system_answer_list)
        if total_words_in_reference_summary:
            recall = number_of_words_in_lcs / total_words_in_reference_summary
        if total_words_in_system_summary:
            precision = number_of_words_in_lcs / total_words_in_system_summary
    return (round(recall, 4), round(precision, 4))


def rouge_s(system_answer: str, ref_answer: str) -> Tuple[float, float]:
    """
    Calculates and returns recall and precision for system's answer given the reference answer
    using ROUGE-S approach
    """
    recall, precision = 0, 0
    skip_words_system = skip_words(system_answer)
    skip_words_ref = skip_words(ref_answer)
    # find the number of skip-bigram matches between system and ref answers
    skip_words_system_ref_intersection = []
    for skip_word_ref_string in skip_words_ref:
        if skip_word_ref_string in skip_words_system:
            skip_words_system_ref_intersection.append(skip_word_ref_string)
    # calculate recall and precision
    if skip_words_ref:
        recall = len(skip_words_system_ref_intersection) / len(skip_words_ref)
    if skip_words_system:
        precision = len(skip_words_system_ref_intersection) / len(skip_words_system)
    return (round(recall, 4), round(precision, 4))


def calculate_f_value(recall: float, precision: float) -> float:
    """
    Calculate and return f value provided recall and precision
    """
    f_value = 0.0
    if recall and precision:
        beta = precision / recall
        beta_square = beta**2 
        f_numerator = (1 + beta_square) * recall * precision
        f_denominator = recall + beta_square*precision
        f_value = f_numerator / f_denominator
    return f_value


def remove_stopwords(answer: str) -> str:
    """
    Removes stopwords from the input answer using nltk library
    """
    # Download stopwords if you haven't already
    #nltk.download('stopwords')
    #nltk.download('punkt')

    # Tokenize the answer sentence
    words = word_tokenize(answer)
    # Get the English stopwords
    english_stopwords = set(stopwords.words('english'))
    # Remove stopwords
    filtered_words = [word for word in words if word.lower() not in english_stopwords]
    filtered_sentence = ' '.join(filtered_words)

    return filtered_sentence


def get_score_string(system_answer: str, ref_answer: str) -> str:
    """
    Calculates ROUGE N (1, 2, 3), L, S using functions defined and returns score string to add to the csv
    """
    score_string = ""
    cos_simi = get_semantic_score(system_answer, ref_answer)
    score_string += f"Cosine similarity: {cos_simi}\n"

    # remove stopwords
    system_answer = remove_stopwords(system_answer)
    ref_answer = remove_stopwords(ref_answer)

    # Rouge_n, mainly 1, 2, 3
    for n in range(1, 4):
        rouge_n_score = rouge_n(system_answer, ref_answer, n)
        score_string += f"ROUGE {n}: {rouge_n_score}\n"
    # Rouge_l
    rouge_l_score = rouge_l(system_answer, ref_answer)
    score_string += f"ROUGE L: {rouge_l_score}\n"
    # Rouge_s
    rouge_s_score = rouge_s(system_answer, ref_answer)
    score_string += f"ROUGE S: {rouge_s_score}"

    return score_string


def get_f_score(system_answer: str, ref_answer: str) -> float:
    """
    Calculates and returns final f value using ROUGE N (1, 2, 3), L, S
    f = [ f(rouge1) + f(rouge2) + f(rouge3) + f(rougeL) + f(rougeS) ] / 5 
    """
    f_score = 0.0
    cos_simi = get_semantic_score(system_answer, ref_answer)
    f_score += 0.25 * cos_simi

    # remove stopwords
    system_answer = remove_stopwords(system_answer)
    ref_answer = remove_stopwords(ref_answer)

    # Rouge_n, mainly 1, 2, 3
    for n in range(1, 4):
        rouge_n_score = rouge_n(system_answer, ref_answer, n)
        f_score += 0.15 * calculate_f_value(rouge_n_score[0], rouge_n_score[1])
    # Rouge_l
    rouge_l_score = rouge_l(system_answer, ref_answer)
    f_score += 0.15 * calculate_f_value(rouge_l_score[0], rouge_l_score[1])
    # Rouge_s
    rouge_s_score = rouge_s(system_answer, ref_answer)
    f_score += 0.15 * calculate_f_value(rouge_s_score[0], rouge_s_score[1])

    return f_score


def squared_sum(x: List[float]) -> float:
  """
  return 3 rounded square rooted value
  """
  return round(sqrt(sum([a*a for a in x])),3)


def get_semantic_score(system_answer: str, ref_answer: str) -> float:
    """
    Returns the cosine similarity between model and reference answer
    Useful for semantic similarities between the two answers 
    """
    system_answer_vector = nlp(system_answer).vector
    ref_answer_vector = nlp(ref_answer).vector
    cs_numerator = sum(a*b for a,b in zip(system_answer_vector, ref_answer_vector))
    cs_denominator = squared_sum(system_answer_vector) * squared_sum(ref_answer_vector)
    cosine_similarity = round(cs_numerator/float(cs_denominator), 3)
    return cosine_similarity


def add_scores_to_csv() -> None:
    """
    Add similarity scores (ROUGE N (1, 2, 3), L, S) to InnovAItors Q&A - Sheet1.csv
    Add f values to bar_plots.csv and draw the bar graph
    """
    # read qa dataframe from the csv
    qa_csv_path = f"{current_path}\../test/InnovAItors Q&A - Sheet1.csv"
    qa_df = pd.read_csv(qa_csv_path, dtype=str, na_filter=False, encoding='unicode_escape')
    plot_csv_path = f"{current_path}\../test/bar_plots.csv"
    plot_df = pd.read_csv(plot_csv_path, dtype=str, na_filter=False, encoding='unicode_escape')

    # Mistral model scores
    qa_df['Mistral scores'] = qa_df.apply(lambda row: get_score_string(row['Mistral'], row['DE answer']), axis=1)
    # Mistral + RAG scores
    qa_df['Mistral + RAG scores'] = qa_df.apply(lambda row: get_score_string(row['Mistral + RAG'], row['DE answer']), axis=1)
    # Mistral Fine-Tuned scores
    qa_df['Mistral Fine-Tuned scores'] = qa_df.apply(lambda row: get_score_string(row['Mistral Fine-Tuned'], row['DE answer']), axis=1)
    # Mistral Fine-Tuned + RAG scores
    qa_df['Mistral Fine-Tuned + RAG scores'] = qa_df.apply(lambda row: get_score_string(row['Mistral Fine-Tuned + RAG'], row['DE answer']), axis=1)
    # write updated dataframe with ROUGE scores to csv
    qa_df.to_csv(qa_csv_path, index=False)

    # Mistral f scores
    plot_df['Mistral f scores'] = qa_df.apply(lambda row: get_f_score(row['Mistral'], row['DE answer']), axis=1)
    # Mistral + RAG f scores
    plot_df['Mistral + RAG f scores'] = qa_df.apply(lambda row: get_f_score(row['Mistral + RAG'], row['DE answer']), axis=1)
    # Mistral Fine-Tuned f scores
    plot_df['Mistral fine-tuned f scores'] = qa_df.apply(lambda row: get_f_score(row['Mistral Fine-Tuned'], row['DE answer']), axis=1)
    # Mistral Fine-Tuned + RAG f scores
    plot_df['Mistral Fine-Tuned + RAG f scores'] = qa_df.apply(lambda row: get_f_score(row['Mistral Fine-Tuned + RAG'], row['DE answer']), axis=1)
    # write updated dataframe with f scores to bas_plot.csv
    plot_df.to_csv(plot_csv_path, index=False)

    # create a bar plot
    graph_data = plot_df.iloc[:, :4].values
    plt.figure(figsize=(10, 6))  # Set the figure size
    num_columns = len(plot_df.columns[:4])
    bar_width = 0.2
    for i, column_name in enumerate(plot_df.columns[:4]):
        plt.bar([x + i * bar_width for x in range(len(graph_data))], graph_data[:, i], width=bar_width, align='center', label=column_name)
    plt.xlabel('question number')
    plt.ylabel('F value')
    plt.title('F scores for different models')
    plt.legend()
    plt.show()


def process_arguments() -> argparse.Namespace:
    """
    Processes the input path arguments to the scripts
    """
    parser = argparse.ArgumentParser(description="Calculate recall and precision for model's answer, using ROUGE, provided the reference answer")
    parser.add_argument("model_ans_path", type=str, help="path to file with model's answer")
    parser.add_argument("ref_ans_path", type=str, help="path to file with reference answer")
    args = parser.parse_args()
    # check if user provided valid arguments
    if not os.path.isfile(args.model_ans_path) or not os.path.isfile(args.ref_ans_path):
        print("\nOne of the provided argument paths to the script do not exist !")
        print("Please provide valid paths with model and reference answers.")
        sys.exit()
    return args


def main():
    """Main Function"""
    args = process_arguments()
    model_ans_path = args.model_ans_path
    ref_ans_path = args.ref_ans_path
    model_answer = open(model_ans_path, "r").read()
    ref_answer = open(ref_ans_path, "r").read()

    # remove stopwords
    model_answer = remove_stopwords(model_answer)
    ref_answer = remove_stopwords(ref_answer)


    # Calculate all the Rouge scores
    print("\n----------------------------------")
    print("ROUGE scores (recall, precision):")
    print("----------------------------------")
    # Rouge_n, mainly 1, 2, 3
    for n in range(1, 4):
        rouge_n_score = rouge_n(model_answer, ref_answer, n)
        print(f"ROUGE {n}: {rouge_n_score}")
    # Rouge_l
    rouge_l_score = rouge_l(model_answer, ref_answer)
    print(f"ROUGE L: {rouge_l_score}")
    # Rouge_s
    rouge_s_score = rouge_s(model_answer, ref_answer)
    print(f"ROUGE S: {rouge_s_score}")
    print("----------------------------------")
    

if __name__ == "__main__":
    main()
    # comment main and uncomment below function to update csv with scores
    #add_scores_to_csv()
