import json
import random
from typing import List, Dict, Any, Tuple
from datetime import datetime

from storage import load_history, save_history

QUESTION_FILE = "questions.json"


# ---------------------------------------------------------
# Count questions by difficulty (used in quiz.py)
# ---------------------------------------------------------
def count_questions_by_difficulty(all_questions):
    counts = {"easy": 0, "medium": 0, "hard": 0}
    for q in all_questions:
        diff = q.get("difficulty")
        if diff in counts:
            counts[diff] += 1
    return counts


# ---------------------------------------------------------
# Load questions
# ---------------------------------------------------------
def load_questions() -> List[Dict[str, Any]]:
    with open(QUESTION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("questions", [])


# ---------------------------------------------------------
# Difficulty scoring
# ---------------------------------------------------------
def _difficulty_score(difficulty: str) -> int:
    if difficulty == "easy":
        return 1
    if difficulty == "medium":
        return 2
    if difficulty == "hard":
        return 3
    return 1


# ---------------------------------------------------------
# Feedback storage helpers
# ---------------------------------------------------------
def _get_feedback_map() -> Dict[str, List[int]]:
    history = load_history()
    return history.get("_feedback", {})


def _save_feedback_map(feedback_map: Dict[str, List[int]]) -> None:
    history = load_history()
    history["_feedback"] = feedback_map
    save_history(history)


def _question_key(q: Dict[str, Any]) -> str:
    return q["question"]


def _average_rating(ratings: List[int]) -> float:
    if not ratings:
        return 0.0
    return sum(ratings) / len(ratings)


# ---------------------------------------------------------
# Select questions (feedback‑weighted)
# ---------------------------------------------------------
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

    # Weight questions by feedback
    weights = []
    for q in pool:
        key = _question_key(q)
        ratings = feedback_map.get(key, [])
        avg = _average_rating(ratings)
        weight = 1.0 + (avg / 5.0)
        weights.append(weight)

    # random.choices allows duplicates — quiz.py prevents that by checking availability first
    k = min(num_questions, len(pool))
    selected = random.choices(pool, weights=weights, k=k)
    return selected


# ---------------------------------------------------------
# Ask a question
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# Feedback collection
# ---------------------------------------------------------
def collect_feedback(q: Dict[str, Any]) -> None:
    key = _question_key(q)
    feedback_map = _get_feedback_map()

    while True:
        resp = input("Rate this question 1-5 (or press Enter to skip): ").strip()
        if resp == "":
            return
        if not resp.isdigit():
            print("Invalid input. Please enter a number between 1 and 5.")
            continue
        rating = int(resp)
        if rating < 1 or rating > 5:
            print("Invalid rating. Please enter a number between 1 and 5.")
            continue

        feedback_map.setdefault(key, []).append(rating)
        _save_feedback_map(feedback_map)
        print("Thank you for your feedback.")
        return


# ---------------------------------------------------------
# Record quiz result
# ---------------------------------------------------------
def record_quiz_result(username: str, score: int, max_score: int, num_correct: int, num_questions: int) -> None:
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


# ---------------------------------------------------------
# Show user stats
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# Main application
# ---------------------------------------------------------
def main():
    from auth import create_account, login

    print("Welcome to the Cybersecurity Quiz Application!")

    username = None
    while username is None:
        print("\n1. Login")
        print("2. Create Account")
        print("3. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            username = login()
        elif choice == "2":
            username = create_account()
        elif choice == "3":
            print("Goodbye!")
            return
        else:
            print("Invalid choice. Please try again.")

    # Load questions
    all_questions = load_questions()
    if not all_questions:
        print("No questions available. Please check questions.json.")
        return

    while True:
        print(f"\nLogged in as: {username}")
        print("Quiz Setup:")
        print("Number of questions: 5")  # Fixed as per spec

        # Show difficulty counts
        counts = count_questions_by_difficulty(all_questions)
        print("Available questions by difficulty:")
        print(f"  Easy: {counts['easy']}")
        print(f"  Medium: {counts['medium']}")
        print(f"  Hard: {counts['hard']}")

        # Choose difficulty
        while True:
            print("\nChoose difficulty:")
            print("1. Easy")
            print("2. Medium")
            print("3. Hard")
            print("4. All")
            diff_choice = input("Enter choice: ").strip()
            if diff_choice == "1":
                difficulty = "easy"
            elif diff_choice == "2":
                difficulty = "medium"
            elif diff_choice == "3":
                difficulty = "hard"
            elif diff_choice == "4":
                difficulty = "all"
            else:
                print("Invalid choice.")
                continue
            break

        # Select questions
        selected = select_questions(all_questions, difficulty, 5)
        if len(selected) < 5:
            print(f"Only {len(selected)} questions available for the selected difficulty. Please choose a different difficulty.")
            continue

        # Take quiz
        score = 0
        max_score = 0
        num_correct = 0
        for q in selected:
            correct, points = ask_question(q)
            if correct:
                num_correct += 1
            score += points
            max_score += _difficulty_score(q.get("difficulty", "easy"))
            collect_feedback(q)

        # Record result
        record_quiz_result(username, score, max_score, num_correct, 5)

        # Show results
        print("\nQuiz completed!")
        print(f"Score: {score} / {max_score}")
        print(f"Correct answers: {num_correct} / 5")

        # Show stats
        show_user_stats(username)

        # Another quiz?
        while True:
            again = input("\nTake another quiz? (y/n): ").strip().lower()
            if again in ["y", "yes"]:
                break
            elif again in ["n", "no"]:
                print("Goodbye!")
                return
            else:
                print("Please enter y or n.")


if __name__ == "__main__":
    main()