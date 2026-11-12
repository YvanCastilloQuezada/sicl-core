from api.main import create_app
from api.routes.projects import router as projects_router


def test_core_routers_are_registered():
    paths = create_app().openapi()["paths"]

    required = {
        ("/health", "get"),
        ("/projects", "get"),
        ("/projects", "post"),
        ("/projects/{project_id}", "get"),
        ("/projects/{project_id}", "put"),
        ("/projects/{project_id}", "delete"),
        ("/v1/projects", "get"),
        ("/v1/projects", "post"),
    }

    missing = [
        f"{method.upper()} {path}"
        for path, method in required
        if method not in paths.get(path, {})
    ]

    assert not missing, (
        "Faltan operaciones en OpenAPI: " + ", ".join(missing)
    )


def test_projects_post_route_is_registered_once():
    matches = [
        route
        for route in projects_router.routes
        if getattr(route, "path", None) == "/projects"
        and "POST" in (getattr(route, "methods", set()) or set())
    ]

    assert len(matches) == 1, (
        f"Se esperaba un POST /projects; se encontraron {len(matches)}"
    )

    assert matches[0].name == "create_project"


def test_projects_and_v1_projects_are_distinct_contracts():
    paths = create_app().openapi()["paths"]

    assert "post" in paths["/projects"]
    assert "post" in paths["/v1/projects"]

    project_operation = paths["/projects"]["post"]
    v1_operation = paths["/v1/projects"]["post"]

    assert (
        project_operation["operationId"]
        != v1_operation["operationId"]
    )
