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

        :param scale_id: scale id of the scale_team
        :param corrector: login of the corrector
        :param correctorid: id of the corrector
        :param corrected: login of the corrected
        :param correctedid: id of the corrected
        :param detection: number of the rule that detected the bad evaluation
        :param time: time at which the evaluation started
        :param project: number of the project (ex: 1 -> libft)
        """
        self.scale_id = scale_id
        self.corrector = corrector
        self.correctorid = correctorid
        self.corrected = corrected
        self.correctedid = correctedid
        self.detection = detection
        self.time = time
        self.project = project
        self.date = datetime.fromisoformat(time)

    def print(self):  # bad eval: nsondag corrected tcastron's 42sh on time and it was detected bad by rule number
        print(f'bad evaluation: {self.corrector}({self.correctorid}) ')
        print(f'corrected {self.corrected}({self.correctedid})\'s {self.project} ')
        print(f'on {self.time.month} {self.time.day} {self.time.year} at {self.time.hour}:{self.time.minute} ')
        print(f'and it was considered bad by rule number {self.detection}.')


def create_bad_eval(evaluation, rule):
    """Create a BadEvaluation object based on the evaluation passed as argument

    :param evaluation: evaluation which has been detected as bad (scale_team endpoint)
    :param rule: number of the rule that detected the bad evaluation
    :return: BadEvaluation object
    """
    print('|', evaluation, '|')
    bad = BadEvaluation(int(evaluation['id']))
    bad.corrector = evaluation['corrector']['login']
    bad.correctorid = evaluation['corrector']['id']
    bad.corrected = evaluation['correcteds'][0]['login']
    bad.correctedid = evaluation['correcteds'][0]['id']
    bad.detection = rule
    bad.time = evaluation['begin_at']
    bad.project = evaluation['team']['project_id']
    return bad
