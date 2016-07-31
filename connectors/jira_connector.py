import collections
from jira.client import GreenHopper, JIRA
from config import Config


class JiraGreenHopper(Config):

    def __init__(self, *args, **kwargs):
        super(JiraGreenHopper, self).__init__(*args, **kwargs)
        self.auth = (self.LOGIN, self.PASSWORD)
        self.jira = self.get_jira()

    def get_last_sprint(self, gh, n=0):
        sprints = gh.sprints(self.BOARD)
        sprints.sort(key=lambda x: x.id)
        while n != -1:
            sprint = sprints.pop()
            if sprint.name.lower() not in ['do wyceny', 'sprint 2']:
                n -= 1
        return sprint

    def get_connection(self):
        return GreenHopper({'server': self.HOST}, basic_auth=self.auth)

    def get_jira(self):
        return JIRA({'server': self.HOST}, basic_auth=self.auth)

    def get_issues_data(self, issues):
        types = []
        story_points = {}
        status_list = []
        ids = []
        for issue in issues:
            raw = issue.raw
            types.append(raw['typeName'])
            ids.append(raw['id'])

        if ids:
            query = 'id in {}'.format(str(tuple(ids)))
            jira_issues = self.jira.search_issues(
                query, fields='customfield_10008,status')
            for jira_issue in jira_issues:
                jira_raw = jira_issue.raw

                raw_sp = jira_raw['fields']['customfield_10008']
                sp = raw_sp if raw_sp else 0
                status = jira_raw['fields']['status']['name']
                status_list.append(status)
                if status in story_points.keys():
                    story_points[status] += sp
                else:
                    story_points[status] = sp
            sp_all = sum(story_points.values())
        else:
            sp_all = 0

        story_points[u'All'] = sp_all
        return {
            'count': len(issues),
            'story_points': story_points,
            'types': dict(collections.Counter(types)),
            'status': dict(collections.Counter(status_list))
        }

    def prepare_sprint_data(self, gh, spr_id, render_all):
        data = {}
        raw = {}

        raw['completed'] = gh.completed_issues(self.BOARD, spr_id)
        if render_all:
            raw['incompleted'] = gh.incompleted_issues(self.BOARD, spr_id)
        for name, obj in raw.items():
            data[name] = self.get_issues_data(obj)

        data['info'] = gh.sprint_info(self.BOARD, spr_id)
        return data

    def get_data(self, n=0, render_all=True):
        gh = self.get_connection()
        sprint = self.get_last_sprint(gh, n)
        data = self.prepare_sprint_data(gh, sprint.id, render_all)
        return data
