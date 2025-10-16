### LM Studio (Qwen3-4B-2507)

- **Base URL (Tailscale):** `http://desktop.taile9300d.ts.net:1234/v1`
- **Model:** `"qwen/qwen3-4b-2507"`
- MCP Server running with the following tools



The tools exposed via this model are designed to assist with various operations related to GitHub repositories, including managing issues, pull requests, code analysis, file operations, notifications, and more. Below is a detailed breakdown of the tools, their uses, examples, and their endpoints.

---

### 1. **File Operations**
These tools help manage files in a repository, including reading, writing, and deleting.

#### a. `read_file`, `read_text_file`, `read_media_file`, `read_multiple_files`
- **Use**: Read the content of files (text, media, or multiple files).
- **Examples**:
  - `read_text_file("path/to/file.txt")` → Returns the content of a text file.
  - `read_media_file("path/to/image.png")` → Returns base64-encoded data and MIME type of an image.
- **Endpoints**: 
  - `read_text_file(path)`  
  - `read_media_file(path)`  
  - `read_multiple_files(paths)` → Reads multiple files simultaneously.

#### b. `write_file`, `edit_file`
- **Use**: Create or modify files.
- **Examples**:
  - `write_file("path/to/newfile.txt", "Hello, World!")` → Creates a new file or overwrites an existing one.
  - `edit_file("path/to/file.txt", edits=[{"oldText": "old", "newText": "new"}])` → Replaces specific lines in a file.
- **Endpoints**:
  - `write_file(path, content)`  
  - `edit_file(path, edits)`  

#### c. `create_directory`, `move_file`, `list_directory`, `list_directory_with_sizes`, `directory_tree`, `search_files`, `get_file_info`
- **Use**: Manage directory structures, list files/directories, and search for files.
- **Examples**:
  - `create_directory("path/to/newdir")` → Creates a new directory.
  - `list_directory("path/to/dir")` → Returns a list of files and directories.
  - `search_files("path/to/search", "pattern")` → Finds files matching a pattern.
- **Endpoints**:
  - `create_directory(path)`  
  - `list_directory(path)`  
  - `list_directory_with_sizes(path, sortBy="name")`  
  - `directory_tree(path)`  
  - `search_files(path, pattern)`  
  - `get_file_info(path)`  

---

### 2. **Repository Management**
These tools help create, fork, and manage repositories.

#### a. `create_repository`, `fork_repository`
- **Use**: Create or fork a new repository.
- **Examples**:
  - `create_repository(name="myproject", private=True)` → Creates a private repository.
  - `fork_repository(owner="github", repo="my-repo")` → Forks an existing repository.
- **Endpoints**:
  - `create_repository(name, description, organization, private)`  
  - `fork_repository(owner, repo, organization)`  

#### b. `push_files`
- **Use**: Push multiple files to a repository in a single commit.
- **Examples**:
  - `push_files(branch="main", files=[{"path": "file.txt", "content": "content"}], message="Initial commit")` → Pushes files to a branch.
- **Endpoints**:
  - `push_files(branch, files, message, owner, repo)`  

---

### 3. **Issue and Pull Request Management**
These tools handle issues, pull requests, and their reviews.

#### a. `create_issue`, `update_issue`, `get_issue`, `list_issues`, `search_issues`
- **Use**: Create, update, or retrieve issues.
- **Examples**:
  - `create_issue(owner="github", repo="my-repo", title="Bug report", body="Description")` → Creates a new issue.
  - `update_issue(owner="github", repo="my-repo", issue_number=1, title="Updated title")` → Updates an issue.
- **Endpoints**:
  - `create_issue(owner, repo, title, body, labels, assignees, milestone)`  
  - `update_issue(owner, repo, issue_number, title, body, labels, assignees, state, state_reason)`  
  - `get_issue(owner, repo, issue_number)`  
  - `list_issues(owner, repo, state="open", labels=["bug"])`  

#### b. `create_pull_request`, `update_pull_request`, `get_pull_request`, `list_pull_requests`, `search_pull_requests`
- **Use**: Create, update, or retrieve pull requests.
- **Examples**:
  - `create_pull_request(owner="github", repo="my-repo", title="Feature request", head="feature-branch", base="main")` → Creates a PR.
  - `get_pull_request(owner="github", repo="my-repo", pullNumber=1)` → Retrieves PR details.
- **Endpoints**:
  - `create_pull_request(owner, repo, title, head, base, body, draft)`  
  - `update_pull_request(owner, repo, pullNumber, title, body, reviewers, state, base, draft)`  
  - `get_pull_request(owner, repo, pullNumber)`  
  - `list_pull_requests(owner, repo, state="open")`  

#### c. `merge_pull_request`, `submit_pending_pull_request_review`, `create_pending_pull_request_review`
- **Use**: Merge PRs or submit reviews.
- **Examples**:
  - `merge_pull_request(owner="github", repo="my-repo", pullNumber=1, merge_method="merge")` → Merges a PR.
  - `create_pending_pull_request_review(owner="github", repo="my-repo", pullNumber=1)` → Creates a pending review.
- **Endpoints**:
  - `merge_pull_request(owner, repo, pullNumber, commit_message, commit_title, merge_method)`  
  - `create_pending_pull_request_review(owner, repo, pullNumber)`  
  - `submit_pending_pull_request_review(owner, repo, pullNumber, event="APPROVE")`  

---

### 4. **Code Analysis and Security**
These tools analyze code for quality, security, and vulnerabilities.

#### a. `analyze_code`
- **Use**: Analyze code for quality, security, and architectural issues.
- **Examples**:
  - `analyze_code(code="function add(a, b) { return a + b; }", language="javascript")` → Analyzes JavaScript code.
- **Endpoints**:
  - `analyze_code(code, language)`  

#### b. `get_code_scanning_alert`, `list_code_scanning_alerts`
- **Use**: Retrieve or list code scanning alerts.
- **Examples**:
  - `get_code_scanning_alert(owner="github", repo="my-repo", alertNumber=1)` → Gets details of a specific alert.
- **Endpoints**:
  - `get_code_scanning_alert(owner, repo, alertNumber)`  
  - `list_code_scanning_alerts(owner, repo, severity="high", state="open")`  

#### c. `get_dependabot_alert`, `list_dependabot_alerts`
- **Use**: Retrieve or list dependabot alerts.
- **Examples**:
  - `list_dependabot_alerts(owner="github", repo="my-repo", severity="high")` → Lists high-severity alerts.
- **Endpoints**:
  - `get_dependabot_alert(owner, repo, alertNumber)`  
  - `list_dependabot_alerts(owner, repo, severity, state)`  

#### d. `get_secret_scanning_alert`, `list_secret_scanning_alerts`
- **Use**: Retrieve or list secret scanning alerts.
- **Examples**:
  - `list_secret_scanning_alerts(owner="github", repo="my-repo", state="open")` → Lists open secret alerts.
- **Endpoints**:
  - `get_secret_scanning_alert(owner, repo, alertNumber)`  
  - `list_secret_scanning_alerts(owner, repo, state, secret_type)`  

---

### 5. **Workflow and CI/CD Management**
These tools manage workflows, jobs, and logs.

#### a. `get_workflow_run`, `list_workflow_runs`, `run_workflow`, `rerun_workflow_run`, `rerun_failed_jobs`
- **Use**: Manage workflow runs and jobs.
- **Examples**:
  - `run_workflow(owner="github", repo="my-repo", workflow_id="main.yml", ref="main")` → Runs a workflow.
  - `rerun_failed_jobs(owner="github", repo="my-repo", run_id=123)` → Re-runs failed jobs.
- **Endpoints**:
  - `get_workflow_run(owner, repo, run_id)`  
  - `list_workflow_runs(owner, repo, workflow_id)`  
  - `run_workflow(owner, repo, workflow_id, ref, inputs)`  
  - `rerun_workflow_run(owner, repo, run_id)`  
  - `rerun_failed_jobs(owner, repo, run_id)`  

#### b. `get_job_logs`, `get_workflow_run_logs`
- **Use**: Retrieve logs for workflows or jobs.
- **Examples**:
  - `get_job_logs(owner="github", repo="my-repo", run_id=123, failed_only=True)` → Gets logs for failed jobs.
- **Endpoints**:
  - `get_job_logs(owner, repo, job_id, failed_only, return_content, tail_lines)`  
  - `get_workflow_run_logs(owner, repo, run_id)`  

---

### 6. **Notifications and Project Management**
These tools manage notifications and projects.

#### a. `list_notifications`, `get_notification_details`, `add_notification`, `remove_notification`
- **Use**: List, retrieve, or manage notifications.
- **Examples**:
  - `list_notifications(owner="github", repo="my-repo")` → Lists all notifications.
- **Endpoints**:
  - `list_notifications(owner, repo)`  
  - `get_notification_details(notification_id)`  

#### b. `create_project`, `update_project`, `get_project`, `list_projects`
- **Use**: Manage projects (e.g., task boards).
- **Examples**:
  - `create_project(owner="github", repo="my-repo", name="Development")` → Creates a new project.
- **Endpoints**:
  - `create_project(owner, repo, name)`  
  - `update_project(owner, repo, project_id, name)`  
  - `get_project(owner, repo, project_id)`  
  - `list_projects(owner, repo)`  

---

### 7. **Search and Discovery**
These tools help search for content across repositories.

#### a. `search_issues`, `search_pull_requests`, `search_files`
- **Use**: Search for issues, PRs, or files.
- **Examples**:
  - `search_issues(owner="github", repo="my-repo", query="bug")` → Finds issues with "bug" in the title.
- **Endpoints**:
  - `search_issues(owner, repo, query)`  
  - `search_pull_requests(owner, repo, query)`  
  - `search_files(owner, repo, query)`  

---

### 8. **Miscellaneous**
- **`add_label`, `remove_label`**: Add or remove labels from issues or PRs.
- **`assign_user`, `unassign_user`**: Assign or unassign users to issues or PRs.
- **`get_repository_stats`**: Retrieve repository statistics (e.g., stars, forks).

---

### Summary of Endpoints
| Tool Name | Endpoint Example |
|---------|------------------|
| `read_file` | `read_text_file("path/to/file.txt")` |
| `write_file` | `write_file("path/to/file.txt", "content")` |
| `create_repository` | `create_repository(name="my-repo", private=True)` |
| `create_issue` | `create_issue(owner="github", repo="my-repo", title="Bug")` |
| `create_pull_request` | `create_pull_request(owner="github", repo="my-repo", title="Feature", head="feature-branch", base="main")` |
| `analyze_code` | `analyze_code(code="...", language="javascript")` |
| `list_issues` | `list_issues(owner="github", repo="my-repo", state="open")` |
| `get_workflow_run` | `get_workflow_run(owner="github", repo="my-repo", run_id=123)` |
| `search_issues` | `search_issues(owner="github", repo="my-repo", query="bug")` |

This breakdown covers all tools, their uses, examples, and endpoints. Let me know if you'd like a more detailed explanation or integration examples! 🚀

