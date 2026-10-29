import uuid

from fastapi import status

from src.domains.analytics.models import Visit


class TestVisitsEndpoint:

    def test_records_cv_visit(self, client, db_session):
        visitor_id = uuid.uuid4()

        response = client.post("/visits", json={"from_cv": True, "visitor_id": str(visitor_id)})

        assert response.status_code == status.HTTP_204_NO_CONTENT
        visit = db_session.query(Visit).one()
        assert visit.from_cv is True
        assert visit.visitor_id == visitor_id

    def test_from_cv_defaults_to_false(self, client, db_session):
        response = client.post("/visits", json={"visitor_id": str(uuid.uuid4())})

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert db_session.query(Visit).one().from_cv is False

    def test_ignores_bots(self, client, db_session):
        response = client.post(
            "/visits",
            json={"from_cv": True, "visitor_id": str(uuid.uuid4())},
            headers={"User-Agent": "LinkedInBot/1.0 (compatible; Mozilla/5.0)"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert db_session.query(Visit).count() == 0

    def test_rejects_invalid_visitor_id(self, client, db_session):
        response = client.post("/visits", json={"from_cv": True, "visitor_id": "not-a-uuid"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert db_session.query(Visit).count() == 0
