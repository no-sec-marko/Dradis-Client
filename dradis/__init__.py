#####################################################################################
#                  Dradis-Client: Python API Wrapper for Dradis                     #
#                   Reworked and Maintained by no-sec-marko (2021)                  #
#                       Updated by  GoVanguard (2018)                               #
#              Originally developed by Pedro M. Sosa, Novacast                      #
#####################################################################################
# This file is part of Pydradis.                                                    #
#                                                                                   #
#     Pydradis is free software: you can redistribute it and/or modify              #
#     it under the terms of the GNU Lesser General Public License as published by   #
#     the Free Software Foundation, either version 3 of the License, or             #
#     (at your option) any later version.                                           #
#                                                                                   #
#     Pydradis is distributed in the hope that it will be useful,                   #
#     but WITHOUT ANY WARRANTY; without even the implied warranty of                #
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                 #
#     GNU Lesser General Public License for more details.                           #
#                                                                                   #
#     You should have received a copy of the GNU Lesser General Public License      #
#     along with Pydradis.  If not, see <http://www.gnu.org/licenses/>.             #
#####################################################################################
import requests
from requests_html import HTMLSession
import json
import shutil
import logging


class DradisClient:
    login_endpoint = '/pro/login'
    sessions_endpoint = '/pro/session'
    team_endpoint = '/pro/api/teams'
    user_endpoint = '/pro/api/users'
    project_endpoint = '/pro/api/projects'
    node_endpoint = '/pro/api/nodes'
    issue_endpoint = '/pro/api/issues'
    evidence_endpoint = '/pro/api/nodes/{id}/evidence'
    note_endpoint = '/pro/api/nodes/{id}/notes'
    attachment_endpoint = '/pro/api/nodes/{id}/attachments'
    content_blocks_endpoint = '/pro/api/content_blocks'
    document_properties_endpoint = '/pro/api/document_properties'
    issue_library_endpoint = '/pro/api/addons/issuelib/entries'

    def __init__(self, api_token: str, url: str, debug=False, verify=True):
        self.__apiToken = api_token  # API Token
        self.__url = url  # Dradis URL (eg. https://your_dradis_server.com)
        self.__header = {'Authorization': f'Token token={self.__apiToken}'}
        self.__headerCt = {'Authorization': f'Token token={self.__apiToken}', 'Content-type': 'application/json'}
        self.__debug = debug  # Debugging True?
        self.__verify = verify  # Path to SSL certificate
        self.__logger = self._set_logging()  # configure logging

    def debug(self, val: bool):
        self.__debug = val

    def _set_logging(self):
        logger = logging.getLogger('PyDradis3ng')
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        if self.__debug:
            logger.setLevel(logging.DEBUG)
            ch.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(ch)
        return logger

    def contact_dradis(self, url: str, header: dict, req_type: str, response_code: str, data=""):
        """
        Send Requests to Dradis (& DebugCheck for Error Codes)
        """
        r = requests.Request(req_type, url, headers=header, data=data)
        r = r.prepare()

        s = requests.Session()
        results = s.send(r, verify=self.__verify)

        print(results)
        self.__logger.debug(f'Server Response:\n{results.status_code}\n---\n{results.content}')

        if str(results.status_code) != str(response_code):
            return None

        return results.json()

    def get_dradis_cookie(self, username: str, password: str):
        """
        Receive the dradis session cookie '_dradis_cookie' from the login page.
        The function calls the web login method using username and password and
        fetches the cookie from the response.
        """
        login_url = self.__url + self.login_endpoint
        sessions_url = self.__url + self.sessions_endpoint

        session = HTMLSession(verify=self.__verify)
        init_resp = session.get(login_url)
        token = init_resp.html.xpath('//meta[@name="csrf-token"]/@content')

        if token is None:
            self.__logger.warning('PyDradis3ng was not able to fetch CSRF token from login page.')
            return None

        data = f'utf8=%E2%9C%93&authenticity_token={requests.utils.quote(token[0])}&login={username}&password={password}'
        login_resp = session.post(url=sessions_url, data=data)

        if login_resp.status_code == 200:
            return login_resp.cookies.get('_dradis_session')
        else:
            return None

    ####################################
    #         Teams Endpoint           #
    ####################################

    def get_teams_list(self) -> list:
        """
        Retrieves all teams as list, reduced by name and team id.
        """
        url = self.__url + self.team_endpoint
        r = self.contact_dradis(url, self.__headerCt, "GET", "200")

        if r is None:
            self.__logger.warning(f'No teams found.')
            return []

        result = []
        for i in r:
            result.append([[i["name"], i["id"]]])

        return result

    def get_team(self, team_id: int) -> dict:
        """
        Retrieves a single team.
        """
        url = f'{self.__url}{self.team_endpoint}/{team_id}'
        r = self.contact_dradis(url, self.__headerCt, "GET", "200")

        if r is None:
            self.__logger.warning(f'No team with team id {team_id} found.')
            return {}

        return r

    def create_team(self, team_name: str) -> int:
        """
        # Creates a team based on the name.
        Returns the new created team id.
        """
        url = self.__url + self.team_endpoint
        data = {"team": {"name": team_name}}

        r = self.contact_dradis(url, self.__headerCt, "POST", "201", json.dumps(data))

        if r is None:
            self.__logger.warning(f'Creation of the team fails. See response for further info:\n{r}.')
            return -1

        return r['id']

    def update_team(self, team_id: int, team_name: str) -> int:
        """
        Updates a team. Pass the name of the team.
        Return the new created team id.
        """
        url = f'{self.__url}{self.team_endpoint}/{team_id}'
        data = {"team": {"name": team_name}}

        r = self.contact_dradis(url, self.__headerCt, "PUT", "200", json.dumps(data))

        if r is None:
            self.__logger.warning(f'Update of the team fails. See response for further info:\n{r}.')
            return -1

        return r['id']

    def delete_team(self, team_id: int) -> bool:
        """
        Deletes a team.
        """
        url = f'{self.__url}{self.team_endpoint}/{team_id}'
        r = self.contact_dradis(url, self.__header, "DELETE", "200")

        if r is None:
            return False

        return True

    def find_team_by_name(self, team_name: str) -> dict:
        """
        Search for Team by team name.
        """
        url = self.__url + self.team_endpoint
        r = self.contact_dradis(url, self.__headerCt, "GET", "200")

        if not r:
            self.__logger.warning(f'No team with team name {team_name} found.')
            return {}

        result = list((filter(lambda x: x.get('name') == team_name, r)))

        if result:
            return result[0]
        else:
            self.__logger.warning(f'No team with team name {team_name} found.')
            return {}

    ####################################
    #         Users Endpoint           #
    ####################################

    def get_users_list(self) -> list:
        """
        Retrieves all users.
        """
        url = self.__url + self.user_endpoint
        r = self.contact_dradis(url, self.__headerCt, "GET", "200")

        if r is None:
            self.__logger.warning(f'No users found.')
            return []

        result = []
        for i in r:
            result.append([[i["name"], i["id"]]])

        return result

    def get_user(self, user_id: int) -> dict:
        """
        Retrieves a single user.
        """
        url = f'{self.__url}{self.user_endpoint}/{user_id}'
        r = self.contact_dradis(url, self.__headerCt, "GET", "200")

        if r is None:
            self.__logger.warning(f'No team with team id {user_id} found.')
            return {}

        return r

    ####################################
    #         Projects Endpoint        #
    ####################################

    def get_project_list(self) -> list:
        """
        Retrieves all projects, reduced by name and project id.
        """
        url = self.__url + self.project_endpoint
        r = self.contact_dradis(url, self.__header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No projects found.')
            return []

        result = []
        for i in r:
            result.append([[i["name"], i["id"]]])

        return result

    def get_project(self, pid: int) -> dict:
        """
        Retrieves a single project.
        """
        url = f'{self.__url}{self.project_endpoint}/{pid}'
        r = self.contact_dradis(url, self.__header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No project with project id {pid} found.')
            return {}

        return r

    def create_project(self, project_name: str, team_id=None, report_template_properties_id=None, author_ids=None,
                       template=None) -> int:
        """
        Creates a project.
        @project_name: Pass it the name of the project you want to create within Dradis
        @team_id: Assigns the project to a client. Pass it the ID number of the client the project should be associated with within Dradis.
        @report_template_properties_id: Assigns a default report template to the project
        @author_ids: Assigns users as authors to the project. If not specified, only the user performing the request will be added as author.
        @template: Associate with a project template to pre-populate the project with data. Pass this the project template name.
        """
        url = self.__url + self.project_endpoint
        data = {"project": {"name": project_name}}

        if team_id is not None:
            data['project']['team_id'] = str(team_id)

        if report_template_properties_id is not None:
            data['project']['report_template_properties_id'] = str(report_template_properties_id)

        if author_ids is list and not None:
            data['project']['author_ids'] = author_ids

        if template is not None:
            data['project']['template'] = str(template)

        r = self.contact_dradis(url, self.__headerCt, "POST", "201", json.dumps(data))

        if r is None:
            self.__logger.warning(f'Creation of the project fails. See response for further info:\n{r}.')
            return -1

        return r['id']

    def update_project(self, pid: int, project_name: str, team_id=None, report_template_properties_id=None,
                       author_ids=None, template=None) -> int:
        """
        Updates a project.
        """
        url = f'{self.__url}{self.project_endpoint}/{pid}'
        data = {"project": {"name": project_name}}

        if team_id is not None:
            data['project']['team_id'] = str(team_id)

        if report_template_properties_id is not None:
            data['project']['report_template_properties_id'] = str(report_template_properties_id)

        if author_ids is list and not None:
            data['project']['author_ids'] = author_ids

        if template is not None:
            data['project']['template'] = str(template)

        r = self.contact_dradis(url, self.__headerCt, "PUT", "200", json.dumps(data))

        if r is None:
            self.__logger.warning(f'Update of the project with the project id {pid} fails. See response for further '
                                  f'info:\n{r}.')
            return -1

        return r['id']

    def delete_project(self, pid: int) -> bool:
        """
        Deletes a project.
        """
        url = f'{self.__url}{self.project_endpoint}/{pid}'
        r = self.contact_dradis(url, self.__header, "DELETE", "200")

        if r is None:
            return False

        return True

    def find_project_by_name(self, project_name: str) -> dict:
        """
        Search for a Project by project name
        """
        url = self.__url + self.project_endpoint
        r = self.contact_dradis(url, self.__header, "GET", "200")

        if not r:
            self.__logger.warning(f'No project with project name {project_name} found.')
            return {}

        result = list((filter(lambda x: x.get('name') == project_name, r)))

        if result:
            return result[0]
        else:
            self.__logger.warning(f'No project with project name {project_name} found.')
            return {}

    ####################################
    #         Nodes Endpoint           #
    ####################################

    def get_node_list(self, pid: int) -> list:
        """
        Retrieves all the Nodes in your specific project, reduced by label and node id.
        """
        url = self.__url + self.node_endpoint
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid)}

        r = self.contact_dradis(url, header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No nodes found.')
            return []

        result = []
        for i in r:
            result.append([[i["label"], i["id"]]])

        return result

    def get_node(self, pid: int, node_id: int) -> dict:
        """
        Retrieves a single Node from your specified project and displays all the Evidence and Notes associated with the Node.
        """
        url = f'{self.__url}{self.node_endpoint}/{node_id}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}
        r = self.contact_dradis(url, header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No node with node id {node_id} found.')
            return {}

        return r

    def create_node(self, pid: int, label: str, type_id=0, parent_id=None, position=1) -> int:
        """
        Creates a Node in the specified project.

        @label: Pass it the name of the Node you want to create within your Dradis project.
        @type_id: Pass type_id a value of 0 to create a Default Node or a value of 1 to create a Host Node.
        @parent_id: Pass parent_id the ID of your desired parent Node to create a subnode. Or, use "parent_id": null, to create a top-level Node.
        @position: Pass position a numeric value to insert the new Node at a specific location within the existing Node structure
        """
        url = self.__url + self.node_endpoint
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        if parent_id != None:  # If None (Meaning its a toplevel node) then dont convert None to string.
            parent_id = str(parent_id)

        data = {"node": {"label": label, "type_id": str(type_id), "parent_id": parent_id, "position": str(position)}}

        r = self.contact_dradis(url, header, "POST", "201", json.dumps(data))

        if r is None:
            return -1

        return r['id']

    def update_node(self, pid: int, node_id: int, label=None, type_id=None, parent_id=None, position=None) -> int:
        """
        Updates a Node in your specified project. You can update some or all of the Node attributes
        """
        url = f'{self.__url}{self.node_endpoint}/{node_id}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        if label == type_id == parent_id == position is None:
            self.__logger.warning(f'Update of the node fails. No valid data were given.')
            return -1

        node_data = {}
        if label is not None:
            node_data["label"] = str(label)
        if type_id is not None:
            node_data["type_id"] = str(type_id)
        if parent_id is not None:
            node_data["parent_id"] = str(parent_id)
        if position is not None:
            node_data["position"] = str(position)

        r = self.contact_dradis(url, header, "PUT", "200", json.dumps({"node": node_data}))

        if r is None:
            return -1

        return r['id']

    def delete_node(self, pid: int, node_id: int) -> bool:
        """
        Deletes a Node from your specified project.
        """
        url = f'{self.__url}{self.node_endpoint}/{node_id}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}
        r = self.contact_dradis(url, header, "DELETE", "200")

        if r is None:
            return False

        return True

    ####################################
    #         Issues Endpoint          #
    ####################################

    def get_issue_list(self, pid: int) -> list:
        """
        Retrieves all the Issues in your specific project, reduced by issue name and issue id.
        """
        url = self.__url + self.issue_endpoint
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid)}

        r = self.contact_dradis(url, header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No issues found.')
            return []

        result = []
        for i in r:
            result.append([[i["title"], i["id"]]])

        return result

    def get_issue(self, pid: int, issue_id: int) -> dict:
        """
        Retrieves a single Issue from your specified project.
        """
        url = f'{self.__url}{self.issue_endpoint}/{issue_id}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid)}
        r = self.contact_dradis(url, header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No issue with issue id {issue_id} found.')
            return {}

        return r

    def _issue_request(self, url: str, method: str, return_code: int, pid: int, title: str, issue_properties: dict,
                       tags=None) -> int:
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        issue_text = f'#[Title]#\r\n{title}\r\n\r\n'

        for key, value in issue_properties.items():
            issue_text += f'#[{key}]#\r\n{value}\r\n\r\n'

        if isinstance(tags, list) and tags:
            issue_text += f'#[Tags]#\r\n{",".join(tags)}'

        data = {'issue': {'text': issue_text}}

        r = self.contact_dradis(url, header, method.upper(), str(return_code), json.dumps(data))

        if r is None:
            return -1

        return r['id']

    def create_issue(self, pid: int, title: str, issue_properties: dict, tags=None) -> int:
        """
        Creates an Issue in the specified project.

        @title: Sets the title of the issue
        @text: Pass it the content of the Issue. issue_properties is a dict that renders
        field names with the #[ ]# syntax: #[key]#\r\n value  \r\n\r\n
        """
        url = self.__url + self.issue_endpoint
        return self._issue_request(url=url, method='POST', return_code=201, pid=pid, title=title,
                                   issue_properties=issue_properties, tags=tags)

    def update_issue(self, pid: int, issue_id: int, title: str, issue_properties: dict, tags) -> int:
        """
        Updates an Issue in the specified project.
        """
        url = f'{self.__url}{self.issue_endpoint}/{issue_id}'
        return self._issue_request(url=url, method='PUT', return_code=200, pid=pid, title=title,
                                   issue_properties=issue_properties, tags=tags)

    def delete_issue(self, pid: int, issue_id: int) -> bool:
        """
        Deletes an Issue from your specified project.
        """
        url = f'{self.__url}{self.issue_endpoint}/{issue_id}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}
        r = self.contact_dradis(url, header, "DELETE", "200")

        if r is None:
            return False

        return True

    ####################################
    #         Evidence Endpoint        #
    ####################################

    def get_evidence_list(self, pid: int, node_id: int) -> list:
        """
        Retrieves all the Evidence associated with the specific Node in your project,
        """
        url = self.__url + self.evidence_endpoint.format(id=node_id)
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid)}
        r = self.contact_dradis(url, header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No evidences found.')
            return []

        return r

    def get_evidence(self, pid: int, node_id: int, evidence_id: int) -> dict:
        """
        Retrieves a single piece of Evidence from a Node in your project.
        """
        url = f'{self.__url}{self.evidence_endpoint.format(id=node_id)}/{evidence_id}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid)}

        r = self.contact_dradis(url, header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No evidences with evidence id {evidence_id} found.')
            return {}

        return r

    def _evidence_request(self, url: str, method: str, return_code: int, pid: int, issue_id: int,
                          evidence_properties: dict, tags=None) -> int:
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        evidence_content = ''

        for key, value in evidence_properties.items():
            evidence_content += f'#[{key}]#\r\n{value}\r\n\r\n'

        if isinstance(tags, list) and tags:
            evidence_content += f'#[Tags]#\r\n{",".join(tags)}'

        data = {'evidence': {
            'content': evidence_content,
            "issue_id": str(issue_id)}}

        r = self.contact_dradis(url, header, method, str(return_code), json.dumps(data))

        if r is None:
            return -1

        return r['id']

    def create_evidence(self, pid: int, node_id: int, issue_id: int, evidence_properties: dict, tags=None) -> int:
        """
        Creates a piece of Evidence on the specified Node in your project.
        """
        url = self.__url + self.evidence_endpoint.format(id=node_id)
        return self._evidence_request(url=url, method='POST', return_code=201, pid=pid, issue_id=issue_id,
                                      evidence_properties=evidence_properties, tags=tags)

    def update_evidence(self, pid: int, node_id: str, issue_id: int, evidence_id: str, evidence_properties: dict,
                        tags=None) -> int:
        """
        Updates a specific piece of Evidence on a Node in your project.
        """
        url = f'{self.__url}{self.evidence_endpoint.format(id=node_id)}/{evidence_id}'
        return self._evidence_request(url=url, method='PUT', return_code=200, pid=pid, issue_id=issue_id,
                                      evidence_properties=evidence_properties, tags=tags)

    def delete_evidence(self, pid: int, node_id: int, evidence_id: int) -> bool:
        """
        Deletes a piece of Evidence from the specified Node in your project.
        """
        url = f'{self.__url}{self.evidence_endpoint.format(id=node_id)}/{evidence_id}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}
        r = self.contact_dradis(url, header, "DELETE", "200")

        if r is None:
            return False

        return True

    ####################################
    #    Content Blocks Endpoint       #
    ####################################
    def get_content_blocks(self, pid: int) -> list:
        '''
        Retrieves all of the Content Blocks in your project, ordered by the Content Block id, ascending.
        '''
        url = self.__url + self.content_blocks_endpoint
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid)}
        r = self.contact_dradis(url, header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No content blocks found.')
            return []

        result = []
        for i in r:
            result.append([[i["title"], i["block_group"], i["id"]]])

        return result

    def get_content_block(self, pid: int, block_id: int) -> dict:
        '''
        Retrieves a single Content Block from your project.
        '''
        url = f'{self.__url}{self.content_blocks_endpoint}/{block_id}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid)}
        r = self.contact_dradis(url, header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No content block with block id {block_id} found.')
            return {}

        return r

    def _content_block_request(self, url: str, method: str, return_code: int, pid: int,
                               block_properties: dict, block_group=None) -> int:
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        block_content = ''

        for key, value in block_properties.items():
            block_content += f'#[{key}]#\r\n{value}\r\n\r\n'

        data = {'content_block': {'content': block_content}}

        if block_group:
            data["content_block"]["block_group"] = block_group

        r = self.contact_dradis(url, header, method, str(return_code), json.dumps(data))

        if r is None:
            return -1

        return r['id']

    def create_content_block(self, pid: int, block_properties: dict, block_group=None) -> int:
        """
        Creates a Content Block in your project.

        @block_properties: Pass it the content of the Content Block
        @block_group (optional): Pass this the name of the Block Group you want to assign to your Content Block.
        """
        url = self.__url + self.content_blocks_endpoint
        return self._content_block_request(url=url, method='POST', return_code=201, pid=pid,
                                           block_properties=block_properties, block_group=block_group)

    def update_content_block(self, pid: int, block_id: int, block_properties: dict, block_group=None) -> int:
        """
        Updates a specific Content Block in your project.

        @block_properties: Pass it the content of the Content Block
        @block_group (optional): Pass this the name of the Block Group you want to assign to your Content Block.
        """
        url = f'{self.__url}{self.content_blocks_endpoint}/{block_id}'
        return self._content_block_request(url=url, method='PUT', return_code=200, pid=pid,
                                           block_properties=block_properties, block_group=block_group)

    def delete_content_block(self, pid: int, block_id: int) -> bool:
        """
        Deletes a specific Content Block from your project.
        """
        url = f'{self.__url}{self.content_blocks_endpoint}/{block_id}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}
        r = self.contact_dradis(url, header, "DELETE", "200")

        if r is None:
            return False

        return True

    ####################################
    #         Notes Endpoint           #
    ####################################

    def get_note_list(self, pid: int, node_id: int) -> list:
        """
        Retrieves all of the Notes associated with the specific Node in your project.
        """
        url = f'{self.__url}{self.note_endpoint.format(id=node_id)}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid)}
        r = self.contact_dradis(url, header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No notes found.')
            return []

        result = []
        for i in r:
            result.append([[i["title"], i["id"]]])

        return result

    def get_note(self, pid: int, node_id: int, note_id: int) -> dict:
        """
        Retrieves a single Note from the specific Node in your project.
        """
        url = f'{self.__url}{self.note_endpoint.format(id=node_id)}/{note_id}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid)}
        r = self.contact_dradis(url, header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No notes with note id {note_id} on node id {node_id} found.')
            return {}

        return r

    def _note_request(self, url: str, method: str, return_code: int, pid: int,
                      note_properties: dict, category_id=0) -> int:
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        note_content = ''

        for key, value in note_properties.items():
            note_content += f'#[{key}]#\r\n{value}\r\n\r\n'

        data = {'note': {'text': note_content, 'category_id': str(category_id)}}

        r = self.contact_dradis(url, header, method, str(return_code), json.dumps(data))

        if r is None:
            return -1

        return r['id']

    def create_note(self, pid: int, node_id: int, note_properties: dict, category=0) -> int:
        """
        Creates a Note on the specified Node in your project.

        @text: Pass it the content of the Note.
        @category_id (optional):  	Pass this the numeric value of the category you want to assign to your Note.
        For example, pass it a value of 1 to set your Note to the AdvancedWordExport ready category.
        """
        url = self.__url + self.note_endpoint.format(id=node_id)
        return self._note_request(url=url, method="POST", return_code=201, pid=pid, note_properties=note_properties,
                                  category_id=category)

    def update_note(self, pid: int, node_id: int, note_id: int, note_properties: dict, category=0) -> int:
        """
        Updates a Note on the specified Node in your project.
        """
        url = f'{self.__url}{self.note_endpoint.format(id=node_id)}/{note_id}'
        return self._note_request(url=url, method="PUT", return_code=200, pid=pid, note_properties=note_properties,
                                  category_id=category)

    def delete_note(self, pid: int, node_id: int, note_id: int) -> bool:
        """
        Deletes a Note from the specified Node in your project.
        """
        url = f'{self.__url}{self.note_endpoint.format(id=node_id)}/{note_id}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}
        r = self.contact_dradis(url, header, "DELETE", "200")

        if r is None:
            return False

        return True

    ####################################
    #    Document Properties Endpoint  #
    ####################################

    def get_document_properties(self, pid: int) -> list:
        """
        Retrieves all of the Document Properties associated with the specific project.
        """
        url = self.__url + self.document_properties_endpoint
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid)}
        r = self.contact_dradis(url, header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No document properties found.')
            return []

        return r

    def get_document_property(self, pid: int, property_key: str) -> dict:
        """
        Retrieves a single Document Property from the specific Node in your project.
        """
        url = f'{self.__url}{self.document_properties_endpoint}/{property_key}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid)}
        r = self.contact_dradis(url, header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No property with document property id {property_key} found.')
            return {}

        return r

    def create_document_properties(self, pid: int, document_properties: dict) -> bool:
        """
        Creates a Document Property in your project.
        """
        url = self.__url + self.document_properties_endpoint
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        data = {'document_properties': document_properties}

        r = self.contact_dradis(url, header, 'POST', '201', json.dumps(data))

        if r is None:
            self.__logger.warning(f'It was not possible to create document properties. See response for further '
                                  f'details: {r}')
            return False

        return True

    def update_document_property(self, pid: int, property_key: str, property_value: str) -> int:
        """
        Updates a Note on the specified Node in your project.
        """
        url = f'{self.__url}{self.document_properties_endpoint}/{property_key}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        data = {'document_property': {'value': property_value}}

        r = self.contact_dradis(url, header, 'PUT', '200', json.dumps(data))

        if r is None:
            self.__logger.warning(f'It was not possible to update document properties. See response for further '
                                  f'details: {r}')
            return False

        return True

    def delete_document_property(self, pid: int, property_key: str) -> bool:
        """
        Deletes a Document Property in your project.
        """
        url = f'{self.__url}{self.document_properties_endpoint}/{property_key}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}
        r = self.contact_dradis(url, header, "DELETE", "200")

        if r is None:
            return False

        return True

    ####################################
    #       Attachments Endpoint       #
    ####################################

    def get_attachment_list(self, pid: int, node_id: int) -> list:
        """
        Retrieves all the Attachments associated with the specific Node in your project.
        """
        url = self.__url + self.attachment_endpoint.format(id=node_id)
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid)}
        r = self.contact_dradis(url, header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No attachments found.')
            return []

        return r

    def get_attachment(self, pid: int, node_id: int, attachment_name: str) -> dict:
        """
        Retrieves a single attachment from a Node in your project.
        """
        url = f'{self.__url}{self.attachment_endpoint.format(id=node_id)}/{attachment_name}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid)}
        r = self.contact_dradis(url, header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No attachments found.')
            return {}

        return r

    def download_attachment(self, pid: int, node_id: int, attachment_name: str, cookie: str, output_file=None) -> bool:
        '''
        Download a single attachment from a Node in your project. Fetching the file / attachment from the
        the API is not possible. Therefore, a valid '_dradis_session' cookie is necessary. The value can
        be fetched from the function self.get_dradis_cookie().
        '''
        url = f'{self.__url}{self.attachment_endpoint.format(id=node_id)}/{attachment_name}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid)}
        r = self.contact_dradis(url, header, "GET", "200")

        cookies = {'_dradis_session': cookie}

        try:
            download = r["link"]

            response = requests.get(self.__url + download, cookies=cookies, stream=True, verify=self.__verify)
            if output_file is None:
                output_file = r["filename"]

            with open(output_file, "wb") as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
        except Exception as err:
            self.__logger.warning("Unexpected exception: {0}".format(err))
            return False

        return True

    def create_attachment(self, pid: int, node_id: int, attachment_filename: str) -> list:
        """
        Creates an Attachment on the specified Node in your project.
        """
        url = self.__url + self.attachment_endpoint.format(id=node_id)
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid)}

        try:
            files = [('files[]', open(attachment_filename, 'rb'))]

            r = requests.post(url, headers=header, files=files, verify=self.__verify)
            if r.status_code != 201:
                self.__logger.warning(
                    f'It was not possible to rename the attachment {attachment_filename}. See the response '
                    f'for further details:\n{r}')
                return []
            else:
                r = r.json()
                return [r[0]["filename"], r[0]["link"]]
        except Exception as err:
            self.__logger.warning("Unexpected exception: {0}".format(err))
            return []

    def rename_attachment(self, pid: int, node_id: int, attachment_filename: str, new_attachment_filename: str) -> dict:
        """
        Renames a specific Attachment on a Node in your project.
        """
        url = f'{self.__url}{self.attachment_endpoint.format(id=node_id)}/{attachment_filename}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Content-type': 'application/json',
                  'Dradis-Project-Id': str(pid)}

        data = {"attachment": {"filename": new_attachment_filename}}
        r = self.contact_dradis(url, header, "PUT", "200", json.dumps(data))

        if r is None:
            self.__logger.warning(
                f'It was not possible to rename the attachment {attachment_filename}. See the response '
                f'for further details:\n{r}')
            return {}

        return r

    def delete_attachment(self, pid: int, node_id: int, attachment_name: str) -> bool:
        """
        Deletes an Attachment from the specified Node in your project.
        """
        url = f'{self.__url}{self.attachment_endpoint.format(id=node_id)}/{attachment_name}'
        header = {'Authorization': f'Token token="{self.__apiToken}"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        r = self.contact_dradis(url, header, "DELETE", "200")

        if r is None:
            return False

        return True

    ####################################
    #       IssueLibrary Endpoint      #
    ####################################

    def get_issue_library_list(self) -> list:
        url = self.__url + self.issue_library_endpoint
        r = self.contact_dradis(url, self.__header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No issues in IssueLibrary were found.')
            return []

        return r

    def get_issue_library_entry(self, issuelib_id: int) -> dict:
        """
        Retrieves a single IssueLibrary entry.
        """
        url = f'{self.__url}{self.issue_library_endpoint}/{issuelib_id}'
        r = self.contact_dradis(url, self.__header, "GET", "200")

        if r is None:
            self.__logger.warning(f'No library issue with issuelib id {issuelib_id} found.')
            return {}

        return r

    def _issue_library_request(self, url: str, method: str, return_code: int, issue_library_properties: dict) -> int:

        issue_library_content = ''

        for key, value in issue_library_properties.items():
            issue_library_content += f'#[{key}]#\r\n{value}\r\n\r\n'

        data = {'entry': {'content': issue_library_content}}

        r = self.contact_dradis(url, self.__headerCt, method, str(return_code), json.dumps(data))

        if r is None:
            return -1

        return r['id']

    def create_issue_library_entry(self, issue_library_properties: dict) -> int:
        """
        Creates an IssueLibrary entry.

        @content: Pass it the content of the IssueLibrary entry to be created.
        """
        url = self.__url + self.issue_library_endpoint
        return self._issue_library_request(url=url, method="POST", return_code=201,
                                           issue_library_properties=issue_library_properties)

    def update_issue_library_entry(self, issue_library_properties: dict, issuelib_id: int) -> int:
        """
        Updates a specific IssueLibrary entry.
        """
        url = f'{self.__url}{self.issue_library_endpoint}/{issuelib_id}'
        return self._issue_library_request(url=url, method="PUT", return_code=200,
                                           issue_library_properties=issue_library_properties)

    def delete_issue_library_entry(self, issuelib_id: int) -> bool:
        """
        Deletes a specific IssueLibrary entry from your instance.
        """
        url = f'{self.__url}{self.issue_library_endpoint}/{issuelib_id}'
        r = self.contact_dradis(url, self.__header, "DELETE", "200")

        if r is None:
            return False

        return True
