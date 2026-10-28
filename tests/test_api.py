"""API tests for project and task workflows."""


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_project(client):
    created = client.post(
        "/api/v1/projects",
        json={"name": "DevTrack", "description": "Personal task tracker"},
    )
    assert created.status_code == 201
    project = created.json()
    assert project["name"] == "DevTrack"
    assert project["id"] > 0

    fetched = client.get(f"/api/v1/projects/{project['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["description"] == "Personal task tracker"


def test_project_name_is_trimmed_and_blank_name_rejected(client):
    created = client.post("/api/v1/projects", json={"name": "  DevTrack  "})
    assert created.status_code == 201
    assert created.json()["name"] == "DevTrack"

    rejected = client.post("/api/v1/projects", json={"name": "   "})
    assert rejected.status_code == 422


def test_project_update_and_missing_project(client):
    created = client.post("/api/v1/projects", json={"name": "Old name"})
    project_id = created.json()["id"]

    updated = client.patch(
        f"/api/v1/projects/{project_id}", json={"name": "New name"}
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "New name"

    missing = client.get("/api/v1/projects/9999")
    assert missing.status_code == 404


def test_task_lifecycle_and_status_filter(client):
    project_response = client.post("/api/v1/projects", json={"name": "Demo"})
    project_id = project_response.json()["id"]

    task_response = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Write tests", "priority": "high"},
    )
    assert task_response.status_code == 201
    task = task_response.json()
    assert task["status"] == "todo"
    assert task["priority"] == "high"

    updated = client.patch(
        f"/api/v1/projects/{project_id}/tasks/{task['id']}",
        json={"status": "done"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "done"

    done_tasks = client.get(
        f"/api/v1/projects/{project_id}/tasks", params={"status_filter": "done"}
    )
    assert done_tasks.status_code == 200
    assert len(done_tasks.json()) == 1

    todo_tasks = client.get(
        f"/api/v1/projects/{project_id}/tasks", params={"status_filter": "todo"}
    )
    assert todo_tasks.json() == []


def test_task_requires_existing_project_and_is_scoped(client):
    missing_project = client.post(
        "/api/v1/projects/9999/tasks", json={"title": "Orphan task"}
    )
    assert missing_project.status_code == 404

    first = client.post("/api/v1/projects", json={"name": "First"}).json()
    second = client.post("/api/v1/projects", json={"name": "Second"}).json()
    task = client.post(
        f"/api/v1/projects/{first['id']}/tasks", json={"title": "Scoped task"}
    ).json()

    response = client.get(f"/api/v1/projects/{second['id']}/tasks/{task['id']}")
    assert response.status_code == 404


def test_invalid_task_status_is_rejected(client):
    project = client.post("/api/v1/projects", json={"name": "Demo"}).json()
    response = client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={"title": "Invalid", "status": "blocked"},
    )
    assert response.status_code == 422


def test_deleting_project_deletes_its_tasks(client):
    project = client.post("/api/v1/projects", json={"name": "Temporary"}).json()
    task = client.post(
        f"/api/v1/projects/{project['id']}/tasks", json={"title": "Child task"}
    ).json()

    deleted = client.delete(f"/api/v1/projects/{project['id']}")
    assert deleted.status_code == 204
    task_lookup = client.get(f"/api/v1/projects/{project['id']}/tasks/{task['id']}")
    assert task_lookup.status_code == 404
