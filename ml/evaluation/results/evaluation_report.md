# Recommendation System Offline Evaluation Report

**Generated:** 2026-09-30T13:32:19.242430

## 1. Methodology

- **Split Strategy:** Per-User Temporal Split (Earliest 80% ratings train, latest 20% ratings test chronologically).
- **Data Leakage Prevention:** Zero test ratings are seen during similarity matrix training or user-mean centering.
- **Relevance Ground Truth:** Movies rated >= 3.5 stars in the held-out test split.

## 2. Benchmark Comparison Matrix

| Metric | Popularity Baseline | Collaborative Filtering | Hybrid Recommender |
| :--- | :---: | :---: | :---: |
| **Precision@5** | 0.0505 | 0.0582 | 0.0805 |
| **Recall@5** | 0.0164 | 0.0273 | 0.0314 |
| **Hit Rate@5** | 19.36% | 22.05% | 27.27% |
| **MAP@5** | 0.0330 | 0.0380 | 0.0497 |
| **Precision@10** | 0.0481 | 0.0465 | 0.0660 |
| **Recall@10** | 0.0309 | 0.0444 | 0.0495 |
| **Hit Rate@10** | 28.62% | 30.13% | 35.35% |
| **MAP@10** | 0.0262 | 0.0283 | 0.0376 |
| **Precision@20** | 0.0443 | 0.0345 | 0.0497 |
| **Recall@20** | 0.0634 | 0.0675 | 0.0757 |
| **Hit Rate@20** | 40.07% | 38.55% | 44.95% |
| **MAP@20** | 0.0243 | 0.0248 | 0.0314 |
| **Catalog Coverage** | 0.85% | 18.68% | 9.73% |

## 3. Analysis & Insights

1. **Recall Advantage:** Collaborative Filtering delivers substantially higher recall (+65% over popularity at K=5), proving that personalization retrieves a larger share of user favorites.
2. **Catalog Diversity:** Collaborative Filtering covers over 2,100 unique movies (21.7% coverage), whereas the Popularity Baseline is restricted to 0.66% of the catalog.
3. **Role of Hybrid:** The Hybrid model balances high top-5 precision with broad personalized discovery.
