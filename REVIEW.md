## 1
**Spec:** "When the application starts, it displays a menu prompting the user to log in or create a new account.”  
**Status:** **[PASS]**

## 2
**Spec:**  
- “The username must be unique.”  
**Status:** **[PASS]**

## 3
**Spec:** “After logging in the application loads the question bank from a JSON file.”  
**Status:** **[PASS]**

## 4
**Spec:** “The user is prompted to choose how many questions they want to answer out of 5.”  
**Status:** **[FAIL/CHANGED]**  
**Note:** The program now prompts the user what difficulty type of questions they want to choose out of the 5 questions available

## 5
**Spec:** “The user selects a difficulty level: easy, medium, hard, or all difficulties.”  
**Status:** **[PASS]**

## 6
**Spec:**  
- “The application selects questions randomly based on the chosen difficulty.”  
- “Adjusts selection based on previous user feedback.”  
- “Not enough questions → return to setup menu.”
**Status:** **[PASS]**

## 7
**Spec:** “Not enough questions for selected difficulty → return to menu.”  
**Status:** **[PASS]**

## 8
**Spec:** “Each question is displayed one at a time. The user enters their answer depending on the question type.”  
**Status:** **[PASS]**

## 9
**Spec:** “After each question the user is asked to provide feedback but they can skip.”  
**Status:** **[PASS]**

## 10 
**Spec:** “Once all questions are completed, the application displays the user’s total score and performance statistics.”  
**Status:** **[PASS]**

## 11
**Spec:**  
- `users.dat` must be non-human-readable.  
- `history.dat` must be non-human-readable.  
- `questions.json` must be readable.
**Status:** **[PASS]**


## Issues & Warnings
Hardcoded number of questions  


