from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id and current_question_id != 0:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    """
    Validates and stores the answer for the current question to django session.
    """
    if current_question_id is None:
        return True, ""

    if not answer:
        return False, "Please provide an answer."
    current_question = PYTHON_QUESTION_LIST[current_question_id]
    correct_answer = current_question.get("answer")
    session["answers"] = session.get("answers", {})
    session["answers"][current_question_id] = {
        "user_answer": answer.strip().lower(),
        "is_correct": answer.strip().lower() == correct_answer.lower(),
    }
    return True, ""


def get_next_question(current_question_id):
    """
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    """
    if current_question_id is None:
        next_question_id = 0
    else:
        next_question_id = current_question_id + 1

    if next_question_id < len(PYTHON_QUESTION_LIST):
        question_data = PYTHON_QUESTION_LIST[next_question_id]
        question_text = question_data["question_text"]
        options = question_data["options"]
        formatted_question = f"{question_text}<br /><br />Options:<br />" + "<br />".join(
            [f"-> {option}" for idx, option in enumerate(options)]
        )
        return formatted_question, next_question_id
    return None, None


def generate_final_response(session):
    """
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    """
    answers = session.get("answers", {})
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_answers = sum(1 for ans in answers.values() if ans["is_correct"])
    percentage_score = (correct_answers / total_questions) * 100
    if percentage_score == 100:
        remarks = "Excellent! Perfect score!"
    elif percentage_score >= 80:
        remarks = "Great job! You did very well."
    elif percentage_score >= 50:
        remarks = "Good effort! Keep practicing to improve."
    else:
        remarks = "Don't worry, you can try again and do better next time."
    return f"You scored {percentage_score:.2f}%.<br />Remarks: {remarks}"
