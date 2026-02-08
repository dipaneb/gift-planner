export interface FetchParams {
  sort?: 'default' | 'asc' | 'desc';
  limit?: number;
  page?: number;
}

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasPrev: boolean;
  hasNext: boolean;
}