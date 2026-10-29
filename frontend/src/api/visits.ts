import api from ".";

export interface VisitCreateRequest {
  from_cv: boolean;
  visitor_id: string;
}

export const visitsApi = {
  async recordVisit(data: VisitCreateRequest): Promise<void> {
    await api.post("/visits", data);
  },
};
