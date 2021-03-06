# file containing functions related to bad evaluations
from datetime import datetime


class BadEvaluation:
    """Class containing the strict minimum information about a bad evaluation."""

    def __init__(self, scale_id, corrector=None, correctorid=None, corrected=None, correctedid=None, detection=None,
                 time=None, project_id=None, project_name=None):
        """Construct a new BadEvaluation object

        :param int scale_id: scale id of the scale_team
        :param str corrector: login of the corrector
        :param int correctorid: id of the corrector
        :param str corrected: login of the corrected
        :param int correctedid: id of the corrected
        :param int detection: number of the rule that detected the bad evaluation
        :param str time: time at which the evaluation started
        :param int project_id: number of the project (ex: 1 -> libft)
        :param str project_name: name of the project
        """
        self.scale_id = scale_id
        self.corrector = corrector
        self.correctorid = correctorid
        self.corrected = corrected
        self.correctedid = correctedid
        self.detection = detection
        self.time = time
        self.project_id = project_id
        self.project_name = project_name
        self.date = datetime.now()

    def set_date(self):
        """Set date variable to avoid error in __init__"""
        self.date = datetime.fromisoformat(self.time[:-1])

    def print(self):  # bad eval: nsondag corrected tcastron's 42sh on time and it was detected bad by rule number
        """Print the bad_evaluation in the console"""
        print(f'bad evaluation: {self.corrector}({self.correctorid}) ', end='')
        print(f'corrected {self.corrected}({self.correctedid})\'s {self.project_name} ', end='')
        print(f'on {self.date.strftime("%b")} {self.date.day} {self.date.year} ', end='')
        print(f'at {self.date.hour}:{self.date.strftime("%M")} ', end='')
        print(f'and it was considered bad by rule number {self.detection}.')

    def sql_tuple(self):
        return self.scale_id, self.correctorid, self.corrector, self.correctedid, self.corrected, self.project_name, \
               self.project_id, self.detection, self.date


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
    bad.project_id = evaluation['team']['project_id']
    bad.project = '{}'.format(bad.project_id)
    # Set date to avoid problem at creation of object
    bad.set_date()
    return bad
