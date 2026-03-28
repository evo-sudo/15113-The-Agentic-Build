## Behavior Description
This project is a command-line Python quiz application focused on cybersecurity topics. Users can create an account or log in locally, they can take quizzes generated from a JSON-based question bank and they can track their performance over time. The application includes a secure login system, score tracking stored in a non-readable format and a feedback system that allows users to rate questions. The quiz also includes difficulty levels easy, medium, hard, which affect both question selection and scoring.    
When the application starts, it displays a menu prompting the user to log in, create a new. If the user chooses to create an account, they are prompted to enter a username and password. The username must be unique. If the user logs in, they must enter a valid username and password combination. After logging in, the application loads the question bank from a JSON file. The user is prompted to choose how many questions they want to answer out of 5. The user selects a difficulty level: easy, medium, hard, or all difficulties. The application selects questions randomly based on the chosen difficulty and adjusts selection based on previous user feedback. Each question is displayed one at a time. The user enters their answer depending on the question type. The application checks the answer and immediately informs the user if they are correct or incorrect. After each question, the user is asked to provide feedback. Once all questions are completed, the application displays the user’s total score and performance statistics. The results and updated statistics are saved securely to a local file. The user is then given the option to take another quiz or exit the application.

##Data Format

{
"questions": [
{
"question": "What does VPN stand for?",
"type": "multiple_choice",
"options": ["Virtual Private Network", "Variable Protection Node", "Virtual Public Network", "Virtual Protocol Network"],
"answer": "Virtual Private Network",
"category": "Networking",
"difficulty": "easy"
},
{
"question": "A strong password should include uppercase letters, lowercase letters, numbers, and symbols.",
"type": "true_false",
"answer": "true",
"category": "Security Basics",
"difficulty": "easy"
},
{
"question": "What is the name of the type of attack that tricks users into revealing sensitive information through fake emails or websites?",
"type": "short_answer",
"answer": "phishing",
"category": "Social Engineering",
"difficulty": "medium"
},
{
"question": "Which protocol is used to securely browse websites?",
"type": "multiple_choice",
"options": ["HTTP", "WWW", "HTTPS", "SMTP"],
"answer": "HTTPS",
"category": "Web Security",
"difficulty": "medium"
},
{
"question": "What encryption method uses the same key for both encryption and decryption?",
"type": "short_answer",
"answer": "symmetric encryption",
"category": "Cryptography",
"difficulty": "hard"
}
]
}

## File Structure

quiz.py:
The main program that runs the application. It handles user interaction, quiz flow, scoring, and calls helper functions.
questions.json:
A readable file that stores all quiz questions. This file can be edited to add or modify questions.
users.dat:
Stores user account information, this including usernames and hashed passwords and this file is not human readable.
history.dat:
Stores user quiz history and performance statistics such as scores and accuracy This file is also not human-readable.
SPEC.md
The specification file describing the design and behavior of the application.

## Error Handling

Invalid user input:
If the user enters an invalid menu option or answer choice the program displays an error message and prompts the user again until they give a valid input.

Duplicate username:
If a user tries to create an account with a username that already exists, the program prompts them to enter a different username.

Incorrect password:
If a user enters the wrong password, the program allows them to retry login.

Not enough questions for selected difficulty:
If there are not enough questions available for the selected difficulty level, the program displays a message and returns the user to the quiz setup menu.
