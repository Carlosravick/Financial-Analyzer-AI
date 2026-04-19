export interface TemporalData {
  periodo: string;
  receita: number;
}

export interface MetricsResponse {
  receita_total: number;
  ticket_medio: number;
  taxa_inadimplencia: number;
  total_transacoes: number;
  evolucao_temporal: TemporalData[];
}

export interface ChatMessage {
  q: string;
  a: string;
}

export interface UploadResponse {
  metrics: MetricsResponse;
  insights: string[];
}
