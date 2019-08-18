from .views import (
    ListResourcesOnScreenView,
    ListResourcesView,
    ResourceView,
    UploadResourcesView
)


def resources_routes(app):
    app.router.add_route('GET', '/resources/', ListResourcesView)
    app.router.add_route('GET', '/resources/list/', ListResourcesOnScreenView)
    app.router.add_route('POST', '/resources/', ResourceView)
    app.router.add_route('GET', '/resources/{id}/', ResourceView)
    app.router.add_route('PUT', '/resources/{id}/', ResourceView)
    app.router.add_route('PATCH', '/resources/{id}/', ResourceView)
    app.router.add_route('DELETE', '/resources/{id}/', ResourceView)
    app.router.add_route('POST', '/resources/csv_import/', UploadResourcesView)
