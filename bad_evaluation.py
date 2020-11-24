# file containing functions related to bad evaluations
from datetime import datetime

"""
list of needed things to show to user:
- scale id
- login corrector
- login corrected
- number detection rule
- time
"""


class BadEvaluation:
    """Class containing the strict minimum information about a bad evaluation."""

    def __init__(self, scale_id, corrector=None, correctorid=None, corrected=None, correctedid=None, detection=None,
                 time=None, project=None):
        """Construct a new BadEvaluation object

        :param int scale_id: scale id of the scale_team
        :param str corrector: login of the corrector
        :param int correctorid: id of the corrector
        :param str corrected: login of the corrected
        :param int correctedid: id of the corrected
        :param int detection: number of the rule that detected the bad evaluation
        :param str time: time at which the evaluation started
        :param int project: number of the project (ex: 1 -> libft)
        """
        self.scale_id = scale_id
        self.corrector = corrector
        self.correctorid = correctorid
        self.corrected = corrected
        self.correctedid = correctedid
        self.detection = detection
        self.time = time
        self.project = project
        self.date = datetime.now()

    def set_date(self):
        """Set date variable to avoid error in __init__"""
        self.date = datetime.fromisoformat(self.time[:-1])

    def print(self):  # bad eval: nsondag corrected tcastron's 42sh on time and it was detected bad by rule number
        print(f'bad evaluation: {self.corrector}({self.correctorid}) ', end='')
        print(f'corrected {self.corrected}({self.correctedid})\'s {self.project} ', end='')
        print(f'on {self.date.month} {self.date.day} {self.date.year} at {self.date.hour}:{self.date.minute} ', end='')
        print(f'and it was considered bad by rule number {self.detection}.', end='')


def create_bad_eval(evaluation, rule):
    """Create a BadEvaluation object based on the evaluation passed as argument

    :param evaluation: evaluation which has been detected as bad (scale_team endpoint)
    :param int rule: number of the rule that detected the bad evaluation
    :return: BadEvaluation object
    """
    bad = BadEvaluation(int(evaluation['id']))
    bad.corrector = evaluation['corrector']['login']
    bad.correctorid = evaluation['corrector']['id']
    bad.corrected = evaluation['correcteds'][0]['login']
    bad.correctedid = evaluation['correcteds'][0]['id']
    bad.detection = rule
    bad.time = evaluation['begin_at']
    bad.project = evaluation['team']['project_id']
    bad.set_date()
    return bad
