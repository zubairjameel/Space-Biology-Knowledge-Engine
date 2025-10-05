import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

interface SearchResultItem {
  title: string;
  url: string;
  similarity_score: number;
  summary: string;
}

interface SearchResponse {
  query?: string;
  total_results?: number;
  results?: SearchResultItem[];
  error?: string;
}

interface TopicSummaryResponseSource {
  title: string;
  url: string;
  summary: string;
  similarity_score: number;
}

interface TopicSummaryResponse {
  query?: string;
  summary?: string;
  sources?: TopicSummaryResponseSource[];
  error?: string;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  private http = inject(HttpClient);

  title = 'NASA Space Biology Knowledge Engine';
  query = '';
  topK = 3;
  loading = false;
  error: string | null = null;
  results: SearchResultItem[] = [];
  // topic-summary state
  topicSummary: string | null = null;
  topicSources: TopicSummaryResponseSource[] = [];

  async doSearch() {
    const q = this.query?.trim();
    if (!q) {
      this.error = 'Please enter a question to search.';
      this.results = [];
      return;
    }
    this.loading = true;
    this.error = null;
    this.results = [];
    try {
      const resp = await this.http.get<SearchResponse>(`/search`, {
        params: { query: q, top_k: this.topK.toString() }
      }).toPromise();
      if (resp?.error) {
        this.error = resp.error;
      }
      this.results = resp?.results || [];
    } catch (e: any) {
      this.error = 'Failed to fetch results. Ensure backend is running on http://localhost:8000';
    } finally {
      this.loading = false;
    }
  }

  async getTopicSummary() {
    const q = this.query?.trim();
    if (!q) {
      this.error = 'Please enter a topic to summarize.';
      this.topicSummary = null;
      this.topicSources = [];
      return;
    }
    this.loading = true;
    this.error = null;
    this.topicSummary = null;
    this.topicSources = [];
    try {
      const resp = await this.http.get<TopicSummaryResponse>(`/topic-summary`, {
        params: { query: q, top_k: Math.max(this.topK, 3).toString() }
      }).toPromise();
      if (resp?.error) {
        this.error = resp.error;
      }
      this.topicSummary = resp?.summary || null;
      this.topicSources = resp?.sources || [];
    } catch (e: any) {
      this.error = 'Failed to fetch topic summary. Ensure backend is running on http://localhost:8000';
    } finally {
      this.loading = false;
    }
  }
}
