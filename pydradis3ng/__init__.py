#####################################################################################
#                  PyDradis3-ng: Python API Wrapper for Dradis                      #
#                          Maintained by no-sec-marko (2021)                        #
#                       Updated by  GoVanguard (2018)                               #
#              Origionally developed by Pedro M. Sosa, Novacast                     #
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


class PyDradis3ng:
    # End Nodes#
    login_endpoint = "/pro/login"
    sessions_endpoint = "/pro/session"
    team_endpoint = "/pro/api/teams"
    project_endpoint = "/pro/api/projects"
    node_endpoint = "/pro/api/nodes"
    issue_endpoint = "/pro/api/issues"
    evidence_endpoint = "/pro/api/nodes/<ID>/evidence"
    note_endpoint = "/pro/api/nodes/<ID>/notes"
    attachment_endpoint = "/pro/api/nodes/<ID>/attachments"
    content_blocks_endpoint = "/pro/api/content_blocks"
    document_properties_endpoint = "/pro/api/document_properties"

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

        # URL
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

    # Get Team List
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

    def get_team(self, team_id: str) -> dict:
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
        Creates a team. Pass the name of the team.
        Return the new created team id.
        """

        url = self.__url + self.team_endpoint
        data = {"team": {"name": team_name}}

        r = self.contact_dradis(url, self.__headerCt, "POST", "201", json.dumps(data))

        if r is None:
            self.__logger.warning(f'Creation of the team fails. See response for further info:\n{r}.')
            return -1

        return r['id']

    def update_team(self, team_id: str, new_team_name: str):
        """
        Creates a team. Pass the name of the team.
        Return the new created team id.
        """

        url = f'{self.__url}{self.team_endpoint}/{team_id}'
        data = {"team": {"name": new_team_name}}

        r = self.contact_dradis(url, self.__headerCt, "PUT", "200", json.dumps(data))

        if r is None:
            self.__logger.warning(f'Update of the team fails. See response for further info:\n{r}.')
            return -1

        return r['id']

    def delete_team(self, team_id: str) -> bool:
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
        Search for Team by team name
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

    def get_project(self, pid: str) -> dict:
        """
        Retrieves a single project.
        """

        url = f'{ self.__url }{ self.project_endpoint }/{ pid }'
        r = self.contact_dradis(url, self.__header, "GET", "200")

        if r is None:
            return {}

        return r

    def create_project(self, project_name: str, team_id=None, report_template_properties_id=None, author_ids=None, template=None) -> int:
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

    # Update Project
    def update_project(self, pid: int, new_project_name: str, new_client_id=None):

        # URL
        url = self.__url + self.project_endpoint + "/" + str(pid)

        # DATA
        data = {"project": {"name": new_project_name}}
        if (new_client_id != None):
            data = {"project": {"name": new_project_name, "client_id": str(new_client_id)}}

        # CONTACT DRADIS
        r = self.contact_dradis(url, self.__headerCt, "PUT", "200", json.dumps(data))

        # RETURN
        if (r == None):
            return None

        return r['id']

    # Delete Project
    def delete_project(self, pid: int):

        # URL
        url = self.__url + self.project_endpoint + "/" + str(pid)

        # CONTACT DRADIS
        r = self.contact_dradis(url, self.__header, "DELETE", "200")

        # RETURN
        if (r == None):
            return None

        return True

    # Search For Project
    def find_project(self, name: str):

        # URL
        url = self.__url + self.project_endpoint

        # CONTACT DRADIS
        r = self.contact_dradis(url, self.__header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        result = []
        for i in range(0, len(r)):
            if (r[i]["name"] == name):
                return r[i]["id"]

        return None


    ####################################
    #         Nodes Endpoint           #
    ####################################

    # Get Node List
    def get_nodelist(self, pid: int):

        # URL
        url = self.__url + self.node_endpoint

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid)}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        result = []
        for i in range(0, len(r)):
            result += [[r[i]["label"], r[i]["id"]]]

        return result

    # Create Node
    def create_node(self, pid: int, label: str, type_id=0, parent_id=None, position=1):

        # URL
        url = self.__url + self.node_endpoint

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # DATA
        if (parent_id != None):  # If None (Meaning its a toplevel node) then dont convert None to string.
            parent_id = str(parent_id)
        data = {"node": {"label": label, "type_id": str(type_id), "parent_id": parent_id, "position": str(position)}}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "POST", "201", json.dumps(data))

        # RETURN
        if (r == None):
            return None

        return r['id']

    # Update Node
    def update_node(self, pid: int, node_id: str, label=None, type_id=None, parent_id=None, position=None):

        # URL
        url = self.__url + self.node_endpoint + "/" + str(node_id)

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # DATA (notice this time we are building a str not a dict)
        if (label == type_id == parent_id == position == None):
            return None

        data = '{"node":{'
        if (label != None):
            data += '"label":"' + label + '"'
        if (type_id != None):
            data += ', "type_id":"' + str(type_id) + '"'
        if (parent_id != None):
            data += ', "parent_id":"' + str(parent_id) + '"'
        if (position != None):
            data += ', "position":"' + str(position) + '"'
        data += "}}"

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "PUT", "200", data)

        # RETURN
        if (r == None):
            return None

        return r['id']

    # Delete Node
    def delete_node(self, pid: int, node_id: str):

        # URL
        url = self.__url + self.node_endpoint + "/" + str(node_id)

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "DELETE", "200")

        # RETURN
        if (r == None):
            return None

        return True

    # Find Node  :: Given a nodepath (e.g ac/dc/r) return the node id. (these change between projects)
    def find_node(self, pid: int, nodepath: str):

        # URL
        url = self.__url + self.node_endpoint

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        # Finding packet by traversing tree structure.
        nodepath = nodepath.split("/")
        parent_id = None
        for node in nodepath:
            for i in range(0, len(r)):
                found = False
                if ((r[i]["label"] == node) and (r[i]["parent_id"] == parent_id)):
                    if (self.__debug):
                        print("Found:", node, r[i]["id"])
                    parent_id = r[i]["id"]
                    found = True
                    break

            if (not found):
                return None

        if (self.__debug):
            print("Your node is:", parent_id)

        return parent_id

    # Get Node Info
    def get_node(self, pid: int, node_id: str):

        # URL
        url = self.__url + self.node_endpoint + "/" + str(node_id)

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        return r

    ####################################
    #    Content Blocks Endpoint       #
    ####################################
    def get_contentblocks(self, pid: int):
        '''
        Retrieves all of the Content Blocks in your project, ordered by the Content Block id, ascending.
        '''

        # URL
        url = self.__url + self.content_blocks_endpoint

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid)}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        result = []
        for i in range(0, len(r)):
            result += [[r[i]["title"], r[i]["block_group"], r[i]["id"]]]

        return result

    def get_contentblock(self, pid: int, block_id: int):
        '''
        Retrieves a single Content Block from your project.
        '''

        # URL
        url = self.__url + self.content_blocks_endpoint + "/" + str(block_id)

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid)}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        return r

    def find_contentblock(self, pid: int, name: str):
        '''
        Retrieves a single Content Block from your project.
        '''

        contents = self.get_contentblocks(pid=pid)
        contents_dict = {x[0]: x[1:] for x in contents}
        content = contents_dict.get(name)

        if content is None:
            return None

        return self.get_contentblock(pid=pid, block_id=content[1])

    ####################################
    #    Document Properties Endpoint  #
    ####################################
    def get_document_properties(self, pid: int):
        '''
        Retrieves all of the Document Properties associated with the specific project.
        '''

        # URL
        url = self.__url + self.document_properties_endpoint

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid)}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        result = {}
        for i in range(0, len(r)):
            result.update(r[i].items())

        return result

    ####################################
    #         Issues Endpoint          #
    ####################################

    # Get Issue List
    def get_issuelist(self, pid: int):

        # URL
        url = self.__url + self.issue_endpoint

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid)}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        result = []
        for i in range(0, len(r)):
            result += [[r[i]["title"], r[i]["id"]]]

        return result

    # Create Issue on Project
    def create_issue(self, pid: int, title: str, text: str, tags=[]):

        # URL
        url = self.__url + self.issue_endpoint

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # DATA
        taglines = ""
        if (len(tags) != 0):
            for tag in tags:
                taglines += "#[" + tag + "]#\r\n"

        data = {'issue': {
            'text': '#[Title]#\r\n' + title + '\r\n\r\n#[Description]#\r\n' + str(text) + "\r\n\r\n" + taglines}}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "POST", "201", json.dumps(data))

        # RETURN
        if (r == None):
            return None

        return r['id']

    # Create Issue on Project
    def create_issue_raw(self, pid: int, data: str):

        # URL
        url = self.__url + self.issue_endpoint

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # DATA
        data = {'issue': data}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "POST", "201", json.dumps(data))

        # RETURN
        if (r == None):
            return None

        return r['id']

    # Update Issue
    def update_issue(self, pid: int, issue_id: str, title: str, text: str, tags=[]):

        # URL
        url = self.__url + self.issue_endpoint + "/" + str(issue_id)

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # DATA
        taglines = ""
        if (len(tags) != 0):
            for tag in tags:
                taglines += "#[" + tag + "]#\r\n"

        data = {'issue': {
            'text': '#[Title]#\r\n' + title + '\r\n\r\n#[Description]#\r\n' + str(text) + "\r\n\r\n" + taglines}}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "PUT", "200", json.dumps(data))

        # RETURN
        if (r == None):
            return None

        return r['id']

    # Update Issue
    def update_issue_raw(self, pid: int, issue_id: str, data: str):

        # URL
        url = self.__url + self.issue_endpoint + "/" + str(issue_id)

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # DATA
        data = {'issue': data}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "PUT", "200", json.dumps(data))

        # RETURN
        if (r == None):
            return None

        return r['id']

    # Update Issue
    def update_issue_tags(self, pid: int, issue_id: str, tags=[]):

        # URL
        url = self.__url + self.issue_endpoint + "/" + str(issue_id)

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # Obtain original
        existingIssue = self.get_issue(pid=pid, issue_id=issue_id)
        if existingIssue:
            title = existingIssue['title']
            text = existingIssue['text']
        else:
            return None

        # Remove original
        deleteExisting = self.delete_issue(pid=pid, issue_id=issue_id)

        # DATA
        taglines = ""
        if (len(tags) != 0):
            for tag in tags:
                taglines += "#[" + tag + "]#\r\n"

        data = {'issue': {
            'text': '#[Title]#\r\n' + title + '\r\n\r\n#[Description]#\r\n' + str(text) + "\r\n\r\n" + taglines}}

        # Create new
        createIssue = self.create_issue(pid=pid, title=title, text=text, tags=taglines)

        # RETURN
        if (createIssue == None):
            return None

        return str(createIssue)

    # Delete Issue
    def delete_issue(self, pid: int, issue_id: str):

        # URL
        url = self.__url + self.issue_endpoint + "/" + str(issue_id)

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "DELETE", "200")

        # RETURN
        if (r == None):
            return None

        return True

    # Find Issue
    def find_issue(self, pid: int, keywords: str):

        # URL
        url = self.__url + self.issue_endpoint

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid)}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        # Give people the option to just input a string.
        if (type(keywords) == str):
            keywords = [keywords]

        result = []
        for i in range(0, len(r)):
            str1 = str(r[i]["text"]).upper()
            for k in keywords:
                str2 = str(k).upper()
                if (str1.find(str2) != -1):
                    result += [[r[i]["title"], r[i]["id"]]]
                    break

        return result

    # Get Issue (with issue_id)
    def get_issue(self, pid: int, issue_id: str):

        # URL
        url = self.__url + self.issue_endpoint + "/" + str(issue_id)

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid)}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        return r

    ####################################
    #         Evidence Endpoint        #
    ####################################

    # Get Evidence List
    def get_evidencelist(self, pid: int, node_id: str):

        # URL
        url = self.__url + self.evidence_endpoint.replace("<ID>", str(node_id))

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid)}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        return r

    # Create Evidence
    def create_evidence(self, pid: int, node_id: str, issue_id: str, title: str, text: str, tags=[]):

        # URL
        url = self.__url + self.evidence_endpoint.replace("<ID>", str(node_id))

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # DATA
        taglines = ""
        if (len(tags) != 0):
            for tag in tags:
                taglines += "#[" + tag + "]#\r\n"

        # DATA
        data = {'evidence': {
            'content': '#[Title]#\r\n' + title + '\r\n\r\n#[Description]#\r\n' + str(text) + "\r\n\r\n" + taglines,
            "issue_id": str(issue_id)}}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "POST", "201", json.dumps(data))

        # RETURN
        if (r == None):
            return None

        return r['id']

    # Create Evidence
    def create_evidence_raw(self, pid: int, node_id: str, issue_id: str, data: str):

        # URL
        url = self.__url + self.evidence_endpoint.replace("<ID>", str(node_id))

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # DATA
        data = {'evidence': {'content': data, "issue_id": str(issue_id)}}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "POST", "201", json.dumps(data))

        # RETURN
        if (r == None):
            return None

        return r['id']

    # Update Evidence
    def update_evidence(self, pid: int, node_id: str, issue_id: str, evidence_id: str, title: str, text: str, tags=[]):

        # URL
        url = self.__url + self.evidence_endpoint.replace("<ID>", str(node_id)) + "/" + str(evidence_id)

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # DATA
        taglines = ""
        if (len(tags) != 0):
            for tag in tags:
                taglines += "#[" + tag + "]#\r\n"

        data = {'evidence': {
            'content': '#[Title]#\r\n' + title + '\r\n\r\n#[Description]#\r\n' + str(text) + "\r\n\r\n" + taglines,
            "issue_id": str(issue_id)}}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "PUT", "200", json.dumps(data))

        # RETURN
        if (r == None):
            return None

        return r['id']

    # Delete Evidence
    def delete_evidence(self, pid: int, node_id: str, evidence_id: str):

        # URL
        url = self.__url + self.evidence_endpoint.replace("<ID>", str(node_id)) + "/" + str(evidence_id)

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "DELETE", "200")

        # RETURN
        if (r == None):
            return None

        return True

    # Find Evidence
    def find_evidence(self, pid: int, node_id: str, keywords: str):

        # URL
        url = self.__url + self.evidence_endpoint.replace("<ID>", str(node_id))

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid)}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        # Give people the option to just input a string.
        if (type(keywords) == str):
            keywords = [keywords]

        result = []
        for i in range(0, len(r)):
            str1 = str(r[i]["content"]).upper()
            for k in keywords:
                str2 = str(k).upper()
                if (str1.find(str2) != -1):
                    result += [r[i]]
                    break

        return result

    # Get Evidence Info
    def get_evidence(self, pid: int, node_id: str, evidence_id: str):

        # URL
        url = self.__url + self.evidence_endpoint.replace("<ID>", str(node_id)) + "/" + str(evidence_id)

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid)}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        return r

    ####################################
    #         Notes Endpoint           #
    ####################################

    # Get Note List
    def get_notelist(self, pid: int, node_id: str):

        # URL
        url = self.__url + self.note_endpoint.replace("<ID>", str(node_id))

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid)}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        result = []
        for i in range(0, len(r)):
            result += [[r[i]["title"], r[i]["id"]]]

        return result

    # Create a note on a project
    def create_note(self, pid: int, node_id: str, title: str, text: str, tags=[], category=0):

        # URL
        url = self.__url + self.note_endpoint.replace("<ID>", str(node_id))

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # DATA
        taglines = ""
        if (len(tags) != 0):
            for tag in tags:
                taglines += "#[" + tag + "]#\r\n"

        data = {'note': {
            'text': '#[Title]#\r\n' + title + '\r\n\r\n#[Description]#\r\n' + str(text) + "\r\n\r\n" + taglines,
            "category_id": str(category)}}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "POST", "201", json.dumps(data))

        # RETURN
        if (r == None):
            return None

        return r['id']

    # Create a note on a project
    def create_note_raw(self, pid: int, node_id: str, data: str):

        # URL
        url = self.__url + self.note_endpoint.replace("<ID>", str(node_id))

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # DATA
        data = {'note': {'text': data}}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "POST", "201", json.dumps(data))

        # RETURN
        if (r == None):
            return None

        return r['id']

    # Update Note
    def update_note(self, pid: int, node_id: str, note_id: str, title: str, text: str, tags=[], category=1):

        # URL
        url = self.__url + self.note_endpoint.replace("<ID>", str(node_id)) + "/" + str(note_id)

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # DATA
        taglines = ""
        if (len(tags) != 0):
            for tag in tags:
                taglines += "#[" + tag + "]#\r\n"

        data = {'note': {
            'text': '#[Title]#\r\n' + title + '\r\n\r\n#[Description]#\r\n' + str(text) + "\r\n\r\n" + taglines,
            "category_id": str(category)}}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "PUT", "200", json.dumps(data))

        # RETURN
        if (r == None):
            return None

        return r['id']

    # Update Note
    def update_note_raw(self, pid: int, node_id: str, data):

        # URL
        url = self.__url + self.note_endpoint.replace("<ID>", str(node_id)) + "/" + str(data.note_id)

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # DATA
        taglines = ""
        if (len(data.tags) != 0):
            for tag in data.tags:
                taglines += "#[" + tag + "]#\r\n"

        data = {'note': {
            'text': '#[Title]#\r\n' + data.title + '\r\n\r\n#[Description]#\r\n' + str(
                data.text) + "\r\n\r\n" + taglines,
            "category_id": str(data.category)}}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "PUT", "200", json.dumps(data))

        # RETURN
        if (r == None):
            return None

        return r['id']

    # Delete Note
    def delete_note(self, pid: int, node_id: str, note_id: str):

        # URL
        url = self.__url + self.note_endpoint.replace("<ID>", str(node_id)) + "/" + str(note_id)

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "DELETE", "200")

        # RETURN
        if (r == None):
            return None

        return True

    # Find Note
    def find_note(self, pid: int, node_id: str, keywords: str):

        # URL
        url = self.__url + self.note_endpoint.replace("<ID>", str(node_id))

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid)}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        # Give people the option to just input a string.
        if (type(keywords) == str):
            keywords = [keywords]

        result = []
        for i in range(0, len(r)):
            str1 = str(r[i]["text"]).upper()
            for k in keywords:
                str2 = str(k).upper()
                if (str1.find(str2) != -1):
                    result += [[r[i]["title"], r[i]["id"]]]
                    break

        return result

    # Get Note Info
    def get_note(self, pid: int, node_id: str, note_id: str):

        # URL
        url = self.__url + self.note_endpoint.replace("<ID>", str(node_id)) + "/" + str(note_id)

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid)}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        return r

    ####################################
    #       Attachments Endpoint       #
    ####################################

    # Get Attachments
    def get_attachmentlist(self, pid: int, node_id: str):
        # URL
        url = self.__url + self.attachment_endpoint.replace("<ID>", str(node_id))

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid)}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        # RETURN
        if (r == None):
            return None

        result = []
        for i in range(0, len(r)):
            result += [[r[i]["filename"], r[i]["link"]]]

        return result

    # Get (Download) Attachment
    def download_attachment(self, pid: int, node_id: str, attachment_name: str, cookie: str, output_file=None):
        '''
        Donwload a single attachment from a Node in your project. Fetching the file / attachment from the
        the API is not possible. Therefore, a valid '_dradis_session' cookie is necessary. The value can
        be fetched from the function self.get_dradis_cookie().
        '''
        # URL
        url = self.__url + self.attachment_endpoint.replace("<ID>", str(node_id)) + "/" + attachment_name

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid)}
        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "GET", "200")

        cookies = {'_dradis_session': cookie}

        try:
            download = r["link"]

            response = requests.get(self.__url + download, cookies=cookies, stream=True, verify=self.__verify)
            if (output_file is None):
                output_file = r["filename"]

            with open(output_file, "wb") as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
        except Exception as err:
            print("Unexpected exception: {0}".format(err))
            return None

        return True

    # Post Attachment
    def post_attachment(self, pid: int, node_id: str, attachment_filename: str):
        # URL
        url = self.__url + self.attachment_endpoint.replace("<ID>", str(node_id))

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid)}

        try:

            # FILES
            files = [('files[]', open(attachment_filename, 'rb'))]

            r = requests.post(url, headers=header, files=files, verify=self.__verify)
            if (r.status_code != 201):
                return None
            else:
                r = r.json()
                return [r[0]["filename"], r[0]["link"]]
        except:
            return None

        return True

    # Rename Attachment
    def rename_attachment(self, pid: int, node_id: str, attachment_name: str, new_attachment_name: str):
        # URL
        url = self.__url + self.attachment_endpoint.replace("<ID>", str(node_id)) + "/" + attachment_name

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Content-type': 'application/json',
                  'Dradis-Project-Id': str(pid)}

        # DATA
        data = {"attachment": {"filename": new_attachment_name}}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "PUT", "200", json.dumps(data))

        # RETURN
        if (r == None):
            return None

        return [r['filename'], r["link"]]

    # Delete Attachment
    def delete_attachment(self, pid: int, node_id: str, attachment_name: str):
        # URL
        url = self.__url + self.attachment_endpoint.replace("<ID>", str(node_id)) + "/" + attachment_name

        # HEADER
        header = {'Authorization': 'Token token="' + self.__apiToken + '"', 'Dradis-Project-Id': str(pid),
                  'Content-type': 'application/json'}

        # CONTACT DRADIS
        r = self.contact_dradis(url, header, "DELETE", "200")

        # RETURN
        if (r == None):
            return None

        return True
