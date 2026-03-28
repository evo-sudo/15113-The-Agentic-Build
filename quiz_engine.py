import json
import random
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

from storage import load_history, save_history

QUESTION_FILE = "questions.json"


def load_questions() -> List[Dict[str, Any]]:
    with open(QUESTION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("questions", [])


def _difficulty_score(difficulty: str) -> int:
    # “The quiz also includes difficulty levels easy, medium, hard,
    # which affect both question selection and scoring.”
    if difficulty == "easy":
        return 1
    if difficulty == "medium":
        return 2
    if difficulty == "hard":
        return 3
    return 1


def _get_feedback_map() -> Dict[str, List[int]]:
    history = load_history()
    return history.get("_feedback", {})


def _save_feedback_map(feedback_map: Dict[str, List[int]]) -> None:
    history = load_history()
    history["_feedback"] = feedback_map
    save_history(history)


def _question_key(q: Dict[str, Any]) -> str:
    # Use question text as key
    return q["question"]


def _average_rating(ratings: List[int]) -> float:
    if not ratings:
        return 0.0
    return sum(ratings) / len(ratings)


def select_questions(
    all_questions: List[Dict[str, Any]],
    difficulty_choice: str,
    num_questions: int,
) -> List[Dict[str, Any]]:
    feedback_map = _get_feedback_map()

    if difficulty_choice == "all":
        pool = all_questions
    else:
        pool = [q for q in all_questions if q.get("difficulty") == difficulty_choice]

    if not pool:
        return []

    # “The application selects questions randomly based on the chosen difficulty
    # and adjusts selection based on previous user feedback.”
    weights = []
    for q in pool:
        key = _question_key(q)
        ratings = feedback_map.get(key, [])
        avg = _average_rating(ratings)
        # Base weight 1, plus a boost from average rating (1–5)
        weight = 1.0 + (avg / 5.0)
        weights.append(weight)

    k = min(num_questions, len(pool))
    selected = random.choices(pool, weights=weights, k=k)
    return selected


def ask_question(q: Dict[str, Any]) -> Tuple[bool, int]:
    print("\nCategory:", q.get("category", "Unknown"))
    print("Difficulty:", q.get("difficulty", "Unknown"))
    print("Question:", q["question"])

    q_type = q["type"]
    correct_answer = q["answer"]
    difficulty = q.get("difficulty", "easy")
    points = _difficulty_score(difficulty)

    user_correct = False

    if q_type == "multiple_choice":
        options = q.get("options", [])
        for idx, opt in enumerate(options, start=1):
            print(f"{idx}. {opt}")
        while True:
            choice = input("Enter the number of your choice: ").strip()
            if not choice.isdigit():
                # “If the user enters an invalid menu option or answer choice
                # the program displays an error message and prompts the user again…”
                print("Invalid input. Please enter a valid option number.")
                continue
            idx = int(choice)
            if idx < 1 or idx > len(options):
                print("Invalid option. Please choose a number from the list.")
                continue
            selected = options[idx - 1]
            user_correct = (selected.strip().lower() == correct_answer.strip().lower())
            break

    elif q_type == "true_false":
        while True:
            ans = input("Enter 'true' or 'false': ").strip().lower()
            if ans in ["true", "t"]:
                user_ans = "true"
            elif ans in ["false", "f"]:
                user_ans = "false"
            else:
                print("Invalid input. Please enter 'true' or 'false'.")
                continue
            user_correct = (user_ans == str(correct_answer).strip().lower())
            break

    elif q_type == "short_answer":
        ans = input("Your answer: ").strip().lower()
        user_correct = (ans == str(correct_answer).strip().lower())
    else:
        print("Unknown question type; treating as incorrect.")
        user_correct = False

    if user_correct:
        print("Correct!")
        return True, points
    else:
        print(f"Incorrect. The correct answer was: {correct_answer}")
        return False, 0


def collect_feedback(q: Dict[str, Any]) -> None:
    key = _question_key(q)
    feedback_map = _get_feedback_map()

    # “After each question the user is asked to provide feedback but they can skip.”
    while True:
        resp = input("Rate this question 1-5 (or press Enter to skip): ").strip()
        if resp == "":
            return
        if not resp.isdigit():
            print("Invalid input. Please enter a number between 1 and 5, or press Enter to skip.")
            continue
        rating = int(resp)
        if rating < 1 or rating > 5:
            print("Invalid rating. Please enter a number between 1 and 5.")
            continue
        feedback_map.setdefault(key, []).append(rating)
        _save_feedback_map(feedback_map)
        print("Thank you for your feedback.")
        return


def record_quiz_result(
    username: str,
    score: int,
    max_score: int,
    num_correct: int,
    num_questions: int,
) -> None:
    history = load_history()
    user_history = history.get(username, [])
    accuracy = (num_correct / num_questions) * 100 if num_questions > 0 else 0.0

    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "score": score,
        "max_score": max_score,
        "num_correct": num_correct,
        "num_questions": num_questions,
        "accuracy": accuracy,
    }
    user_history.append(entry)
    history[username] = user_history
    save_history(history)


def show_user_stats(username: str) -> None:
    history = load_history()
    user_history = history.get(username, [])
    if not user_history:
        print("No quiz history available yet.")
        return

    total_quizzes = len(user_history)
    total_score = sum(h["score"] for h in user_history)
    total_max = sum(h["max_score"] for h in user_history)
    avg_accuracy = sum(h["accuracy"] for h in user_history) / total_quizzes

    print("\nYour performance statistics:")
    print(f"  Total quizzes taken: {total_quizzes}")
    print(f"  Cumulative score: {total_score} / {total_max}")
    print(f"  Average accuracy: {avg_accuracy:.2f}%")
    print("  Most recent attempts:")
    for h in user_history[-5:]:
        print(
            f"    {h['timestamp']}: "
            f"Score {h['score']}/{h['max_score']} "
            f"({h['num_correct']}/{h['num_questions']} correct, {h['accuracy']:.1f}% accuracy)"
        )