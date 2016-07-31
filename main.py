from connectors.jira_connector import JiraGreenHopper
from connectors.callendar_connector import Callendar
from connectors.tipboard_connector import Tipboard
from pprint import pprint as pp


class Main(object):

    def __init__(self, *args, **kwargs):
        self.jira = JiraGreenHopper()
        self.calendar = Callendar()
        self.tipboard = Tipboard()

    def run(self, number=1):
        # TODO google calendar
        # self.calendar.do()

        data = self.jira.get_data(n=number)
        self.tipboard.push_one_sprint(data)

        last_sprints = [data]
        for i in range(2):
            last_number = number + i + 1
            last_data = self.jira.get_data(
                n=last_number,
                render_all=False
            )
            last_sprints.append(last_data)

        self.tipboard.push_sprints(last_sprints)


if __name__ == '__main__':
    draw = Main()
    draw.run()
