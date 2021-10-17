Dradis-Client
==

Reworked and Maintained by no-sec-marko (DradisClient - 2021).

Updated by GoVanguard (PyDradis3 - 2018).

Originally created by Novacoast (PyDradis).

## About Dradis-Client
This is a wrapper for the [Dradis Pro API](https://dradisframework.com/support/guides/rest_api/) written in Python 3.
The original project was developed by Novacoast and updated by GoVanguard. In `Dradis-Client`, all API calls were updated 
to the latest version of Dradis Pro API (currently v4.0).

## Installation
Install pulling from this repo:

```bash
git clone https://github.com/no-sec-marko/Dradis-Client.git
```

Local installation
```bash
chmod +x packageIt.sh
./packageIt.sh
python3 -m pip install ./dist/dradis-client-1.0.0.tar.gz
```

## Usage

Initial setup of `DradisClient`:

```python
from dradis import DradisClient

debug = True  # Do you want to see debug info?
verify = True  # Force ssl certificate verification?
api_token = '<DRADIS API KEY>'
server_url = '<DRADIS SERVER URL>'
client = DradisClient(api_token, server_url, debug, verify)
```

All endpoints have 6 functions that work roughly the same:

- *Get:* Given an element id, returns the element info.

- *Get Lists:* Returns list of Clients, Projects, etc.

- *Create:* Creates elements and returns their id.

- *Update:* Updates elements and returns their id.

- *Delete:* Deletes elements and returns True if successful.

- *Find:* Given keyword(s), return a list of possible elements.

### Teams Endpoint

```python
team_id = 1
# Retrieves all teams as list, reduced by name and team id.
teams = client.get_teams_list()
# Retrieves a single team.
team_by_id = client.get_team(team_id=team_id)
# Creates a team based on the name.
new_team_id = client.create_team(team_name='Test Team 1')
# Updates a team. Pass the name of the team.
updated_team_id = client.update_team(team_id=new_team_id, team_name='Test Team 1 - Updated')
# Search for Team by team name.
test_team_1_u = client.find_team_by_name(team_name='Test Team 1 - Updated')
# Deletes a team.
is_team_deleted = client.delete_team(team_id=updated_team_id)
```

### Users Endpoint

```python
# Retrieves all users.
users = client.get_users_list()
# Retrieves a single user.
user = client.get_user(users[0][0][1])
```

### Project Endpoint

```python
# Retrieves all projects
project_list = client.get_project_list
# Retrieves a single project.
project = client.get_project(pid=36)
# Creates a project.
new_project_id = client.create_project(project_name='Test Project 4', team_id=1, report_template_properties_id=4,
                                       template='Welcome Project Template')
# Updates a project.
new_updated_project_id = client.update_project(pid=new_project_id, project_name='Test Project 4 - Updated',
                                               team_id=1, report_template_properties_id=8,
                                               template='Welcome Project Template')
# Finds a project by name.
updated_project = client.find_project_by_name(project_name='Test Project 4 - Updated')
# Deletes a project.
is_project_deleted = client.delete_project(pid=new_updated_project_id)
```

### Node Endpoint

```python
pid = 36
# Retrieves all the Nodes in your specific project
node_list = client.get_node_list(pid=pid)
# Retrieves a single Node from your specified project and displays all the Evidence and Notes associated with the Node.
node = client.get_node(pid=pid, node_id=544)
# Creates a Node in the specified project.
new_node = client.create_node(pid=pid, label='New Node')
# Updates a Node in your specified project.
updated_node = client.update_node(pid=pid, node_id=new_node, label='Updated Test Node', type_id=1, position=2)
# Deletes a Node from your specified project.
is_node_deleted = client.delete_node(pid=pid, node_id=updated_node)
```

###  Issues Endpoint

```python
pid = 36
# Retrieves all the Issues in your specific project.
all_issues = client.get_issue_list(pid=pid)
assert all_issues is not None
# Retrieves a single Issue from your specified project.
issue = client.get_issue(pid=pid, issue_id=all_issues[0][0][1])
assert issue is not None

new_issue_text = {"Title": "Dangerous HTTP methods: TRACE",
                  "Rating": "Medium",
                  "Description": "The TRACE HTTP method is used as a debugging mechanism that allows the client to "
                                 "see what is being received at the other end of the request chain and use that data "
                                 "for testing and diagnostic information."}
tags = ['en', 'mobile']
# Creates an Issue in the specified project.
new_issue_id = client.create_issue(pid=pid, title="New Issue", issue_properties=new_issue_text, tags=tags)
assert new_issue_id > 0
updated_issue_text = {"Title": "Updated Issue Title",
                  "Rating": "Medium",
                  "Description": "Updated sample Issue description."}
# Updates an Issue in the specified project.
updated_issue_id = client.update_issue(pid=pid, issue_id=new_issue_id, title="Updated Issue Title",
                                       issue_properties=updated_issue_text, tags=tags)
assert updated_issue_id > 0
# Deletes an Issue from your specified project.
is_issue_deleted = client.delete_issue(pid=pid, issue_id=updated_issue_id)
```


### Evidence Endpoint

```python
pid = 36
node_id = 544
issue_id = 1819
new_evidence_props = {"Description": "bc. Placeholder evidence content."}
updated_evidence_props = {"Description": "bc. Updated evidence content."}
# Retrieves all the Evidence associated with the specific Node in your project
evidences = client.get_evidence_list(pid=pid, node_id=node_id)
assert evidences is not None
# Retrieves a single piece of Evidence from a Node in your project.
evidence = client.get_evidence(pid=pid, node_id=node_id, evidence_id=8017)
assert evidence is not None
# Creates a piece of Evidence on the specified Node in your project.
new_evidence_id = client.create_evidence(pid=pid, node_id=node_id, issue_id=issue_id,
                                         evidence_properties=new_evidence_props)
assert new_evidence_id > 0
# Updates a specific piece of Evidence on a Node in your project.
updated_evidence_id = client.update_evidence(pid=pid, node_id=node_id, issue_id=issue_id, evidence_id=new_evidence_id,
                                             evidence_properties=updated_evidence_props)
assert updated_evidence_id > 0
# Deletes a piece of Evidence from the specified Node in your project.
is_evidence_deleted = client.delete_evidence(pid=pid, node_id=node_id, evidence_id=new_evidence_id)
```

### Content Block Endpoint

```python
pid = 36
cb_id = 333

cb_content = {'Title': 'New Content Block', 'Description': 'Sample content.'}
# Retrieves all of the Content Blocks in your project.
content_blocks = client.get_content_blocks(pid=pid)
assert content_blocks is not None
# Retrieves a single Content Block from your project.
content_block = client.get_content_block(pid=pid, block_id=cb_id)
assert content_block is not None
# Creates a Content Block in your project.
new_content_block_id = client.create_content_block(pid=pid, block_properties=cb_content, block_group='Conclusions')
assert new_content_block_id > 0
cb_content['Title'] = 'Updated Content Block'
updated_cb_content = cb_content
# Updates a specific Content Block in your project.
updated_content_block_id = client.update_content_block(pid=pid, block_id=new_content_block_id,
                                                       block_properties=updated_cb_content)
assert updated_content_block_id > 0
# Deletes a specific Content Block from your project.
is_content_block_deleted = client.delete_content_block(pid=pid, block_id=updated_content_block_id)
```

### Note Endpoint

```python
pid = 36
node_id = 544
new_note = {'Title': 'Host Details', 'Type': 'Details', 'Description': 'Lorem ipsum dolor sit amet, consectetur '
                                                                       'adipiscing elit. Nullam fringilla tristique '
                                                                       'nisi, id cursus elit tincidunt egestas. Nunc '
                                                                       'sagittis libero eu hendrerit aliquam.'}
# Retrieves all of the Notes associated with the specific Node in your project.
notes = client.get_note_list(pid=pid, node_id=node_id)
assert notes is not None
# Retrieves a single Note from the specific Node in your project.
note = client.get_note(pid=pid, node_id=node_id, note_id=notes[0][0][1])
assert note is not None
# Creates a Note on the specified Node in your project.
new_note_id = client.create_note(pid=pid, node_id=node_id, note_properties=new_note, category=0)
assert new_note_id > 0
new_note['Title'] = 'Updated Host Details'
updated_note = new_note
# Updates a Note on the specified Node in your project.
updated_note_id = client.update_note(pid=pid, node_id=node_id, note_id=new_note_id, note_properties=updated_note,
                                     category=1)
assert updated_note_id > 0
# Deletes a Note from the specified Node in your project.
is_note_deleted = client.delete_note(pid=pid, node_id=node_id, note_id=updated_note_id)
```

### Document Properties Endpoint

```python
pid = 36
new_doc_props = {'dradis.client': 'ACME Ltd.', 'dradis.project': 'Test'}
# Retrieves all of the Document Properties associated with the specific project.
doc_props = client.get_document_properties(pid=pid)
# Retrieves a single Document Property from the specific Node in your project.
doc_prop = client.get_document_property(pid=pid, property_key='dradis.projectname')
# Creates a Document Property in your project.
is_doc_props_created = client.create_document_properties(pid=pid, document_properties=new_doc_props)
updated_doc_prop = {'dradis.project': 'Test'}
# Updates a Note on the specified Node in your project.
is_doc_prop_updated = client.update_document_property(pid=pid, property_key='dradis.project', property_value='Updated Value')
# Deletes a Document Property in your project.
is_doc_prop_deleted_1 = client.delete_document_property(pid=pid, property_key='dradis.project')
is_doc_prop_deleted_2 = client.delete_document_property(pid=pid, property_key='dradis.client')
```

### Attachment Endpoint

```python
pid = 36
node_id = 544
# Retrieves all the Attachments associated with the specific Node in your project.
attachments = client.get_attachment_list(pid=pid, node_id=node_id)
# Retrieves a single attachment from a Node in your project.
attachment = client.get_attachment(pid=pid, node_id=node_id, attachment_name=attachments[0]['filename'])
# Creates an Attachment on the specified Node in your project.
new_attachment = client.create_attachment(pid=pid, node_id=node_id, attachment_filename='testfile.png')
# Renames a specific Attachment on a Node in your project.
updated_attachment_name = client.rename_attachment(pid=pid, node_id=node_id,
                                                   attachment_filename=new_attachment[0],
                                                   new_attachment_filename='renamed-testfile.png')
cookie = client.get_dradis_cookie(username='no-sec-marko', password='P4ssw0rd!')
# Downloads a specific Attachment on a Node in your project but needs a valid Dradis session cookie.
is_attachment_downloaded = client.download_attachment(pid=pid, node_id=node_id,
                                                      attachment_name=updated_attachment_name['filename'],
                                                      cookie=cookie, output_file='./attachment.png')
# Deletes an Attachment from the specified Node in your project.
is_attachment_deleted = client.delete_attachment(pid=pid, node_id=node_id,
                                                 attachment_name=updated_attachment_name['filename'])
```

### IssueLibrary Endpoint

```python
# Retrieves all of the IssueLibrary entries from your instance.
library = client.get_issue_library_list()
# Retrieves a single IssueLibrary entry.
issue_entry = client.get_issue_library_entry(issuelib_id=library[0]['id'])

new_lib_issue = {'Title': 'Dangerous HTTP methods: TRACE', 'Rating': 'Medium', 'Description': 'The TRACE HTTP method is '
                                                                                          'used as a debugging '
                                                                                          'mechanism that allows the '
                                                                                          'client to see what is '
                                                                                          'being received at the '
                                                                                          'other end of the request '
                                                                                          'chain and use that data '
                                                                                          'for testing and diagnostic '
                                                                                          'information.'}

updated_lib_issue = {'Title': 'Dangerous HTTP methods: TRACE', 'Rating': 'Medium', 'Description': 'Updated sample '
                                                                                              'IssueLibrary entry '
                                                                                              'description'}
# Creates an IssueLibrary entry.
new_lib_issue_id = client.create_issue_library_entry(issue_library_properties=new_lib_issue)
# Updates a specific IssueLibrary entry.
updated_lib_issue_id = client.update_issue_library_entry(issuelib_id=new_lib_issue_id, issue_library_properties=updated_lib_issue)
# Deletes a specific IssueLibrary entry from your instance.
is_lib_issue_deleted = client.delete_issue_library_entry(issuelib_id=updated_lib_issue_id)
```

## License
Dradis-Client is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Dradis-Client is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with PyDradis3-ng.  If not, see <http://www.gnu.org/licenses/>.
