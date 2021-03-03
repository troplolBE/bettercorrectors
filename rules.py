from datetime import datetime, timedelta
from bad_evaluation import create_bad_eval


def rule1(evaluation):
    """Function that detects if the evaluation is considered bad or not following case 1

    :param evaluation: the evaluation that needs to be checked
    :return: whether of not the eval is bad according to this rule
    """
    final_mark = evaluation['final_mark']
    project_mark = evaluation['team']['final_mark']

    if final_mark is None:
        print(evaluation)
        return False

    if (final_mark - project_mark) >= 10:
        return True
    return False


def rule2(evaluation):
    """Function that detects if the evaluation is considered bad or not following case 2

    :param evaluation: the evaluation that needs to be checked
    :return: whether of not the eval is bad according to this rule
    """
    pass


def rule3(evaluation):
    """Function that detects if the evaluation is considered bad or not following case 3

    :param evaluation: the evaluation that needs to be checked
    :return: whether of not the eval is bad according to this rule
    """
    duration = evaluation['scale']['duration'] / 60
    if evaluation['begin_at'] is not None:
        begin = datetime.fromisoformat(evaluation['begin_at'][:-1])
    else:
        begin = None
    if evaluation['filled_at'] is not None:
        end = datetime.fromisoformat(evaluation['filled_at'][:-1])
    else:
        end = None

    if not all([duration, begin, end]):
        return False

    diff = end - begin
    diff = diff / timedelta(minutes=1)
    if diff < duration:
        if diff < round(duration / 2):
            return True
    return False


def detect_bad_eval(evaluation):
    """Function that takes an evaluation as parameter and will use multiple rules to detect if
    the evaluation is considered bad or not. It returns a bad_evaluation object in case one of the
    return positive.

    :param evaluation: an evaluation that needs to be checked
    :return: BadEvaluation if bad, False otherwise
    """
    rules = [rule1, rule2, rule3]

    for index, rule in enumerate(rules, 1):
        if rule(evaluation):
            return create_bad_eval(evaluation, index)
    return False
