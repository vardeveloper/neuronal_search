from api.api_v1.endpoints import documents, reports, login, users, customers


def endpoints(app):
    documents.endpoints(app)
    reports.endpoints(app)
    login.endpoints(app)
    users.endpoints(app)
    customers.endpoints(app)
    return app
