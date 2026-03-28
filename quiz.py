import os
from typing import Optional

from auth import create_account, login
from quiz_engine import (
    load_questions,
    select_questions,
    ask_question,
    collect_feedback,
    record_quiz_result,
    show_user_stats,
)


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def main_menu() -> Optional[str]:
    while True:
        print("=== Cybersecurity Quiz Application ===")
        print("1. Log in")
        print("2. Create a new account")
        print("3. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            user = login()
            if user:
                return user
        elif choice == "2":
            user = create_account()
            if user:
                return user
        elif choice == "3":
            print("Goodbye.")
            return None
        else:
            # “If the user enters an invalid menu option… prompts the user again…”
            print("Invalid option. Please enter 1, 2, or 3.\n")


def get_num_questions() -> int:
    # “The user is prompted to choose how many questions they want to answer out of 5.”
    while True:
        resp = input("How many questions would you like to answer (1-5)? ").strip()
        if not resp.isdigit():
            print("Invalid input. Please enter a number between 1 and 5.")
            continue
        n = int(resp)
        if n < 1 or n > 5:
            print("Invalid number. Please choose between 1 and 5.")
            continue
        return n


def get_difficulty_choice() -> str:
    while True:
        print("\nSelect difficulty level:")
        print("1. Easy")
        print("2. Medium")
        print("3. Hard")
        print("4. All difficulties")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            return "easy"
        elif choice == "2":
            return "medium"
        elif choice == "3":
            return "hard"
        elif choice == "4":
            return "all"
        else:
            print("Invalid option. Please enter 1, 2, 3, or 4.")


def run_quiz(username: str) -> None:
    questions = load_questions()
    if not questions:
        print("No questions available. Please check questions.json.")
        return

    while True:
        clear_screen()
        print(f"=== Quiz for {username} ===")
        num_questions = get_num_questions()
        difficulty_choice = get_difficulty_choice()

        selected = select_questions(questions, difficulty_choice, num_questions)
        if len(selected) < num_questions:
            # “If there are not enough questions available for the selected difficulty level,
            # the program displays a message and returns the user to the quiz setup menu.”
            print(
                "\nNot enough questions available for the selected difficulty level. "
                "Returning to quiz setup menu."
            )
            continue

        score = 0
        max_score = 0
        num_correct = 0

        for q in selected:
            correct, points = ask_question(q)
            max_score += points  # max score is sum of difficulty-based points
            if correct:
                score += points
                num_correct += 1
            collect_feedback(q)

        print("\n=== Quiz Complete ===")
        print(f"Total score: {score} / {max_score}")
        accuracy = (num_correct / len(selected)) * 100 if selected else 0.0
        print(f"Questions correct: {num_correct} / {len(selected)} ({accuracy:.2f}% accuracy)")

        # “The results and updated statistics are saved securely to a local file.”
        record_quiz_result(username, score, max_score, num_correct, len(selected))
        show_user_stats(username)

        while True:
            again = input("\nWould you like to take another quiz? (y/n): ").strip().lower()
            if again in ["y", "yes"]:
                break
            elif again in ["n", "no"]:
                print("Exiting quiz. Goodbye.")
                return
            else:
                print("Invalid input. Please enter 'y' or 'n'.")


def main() -> None:
    clear_screen()
    user = main_menu()
    if user is None:
        return
    run_quiz(user)


if __name__ == "__main__":
    main()