from api.api_v1.endpoints import documents, reports, login, users


def endpoints(app):
    documents.endpoints(app)
    reports.endpoints(app)
    login.endpoints(app)
    users.endpoints(app)
    return app
