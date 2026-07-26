# Learning Analytics & Insights Engine (LAIE) — Architecture

**Date:** 2026-07-17  
**Product:** Alora AI  
**Rule:** Insights only — never mutate curriculum, answers, or accessibility decisions.

---

## 1. Audit — before LAIE v2

| Component | State |
|-----------|--------|
| `LearningAnalyticsEngine` | Thin wrap of `analytics_engine.build_analytics_report` (lesson text only) |
| Role dashboards | Missing |
| Predictive / alerts / recommendations | Lived in ALE/AME — not unified |
| Explainable insight philosophy | Missing |

---

## 2. Architecture

```
analytics_engine (lesson stats)
CIE / AME / AIE / ALE / Tutor / Gamification
              ↓
   learning_analytics_engine/*  (LAIE)
              ↓
 LearningAnalyticsEngine (VLIE v2) → report + insights + alerts + dashboards
```

Answers: What? Why? What's next? What intervention? Confidence? Evidence?

---

## 3. Folder structure

```
engines/learning_analytics_engine/
  engine.py schemas.py _sources.py
  learner_analytics.py class_analytics.py teacher_analytics.py parent_analytics.py
  special_educator_analytics.py school_analytics.py district_analytics.py executive_analytics.py
  predictive_models.py intervention_analysis.py accessibility_analysis.py
  curriculum_analysis.py mastery_analysis.py engagement_analysis.py ai_tutor_analysis.py
  dashboards.py reporting.py recommendations.py alerts.py indexing.py
  intelligence.py service.py
docs/LEARNING_ANALYTICS_INSIGHTS_ENGINE.md
tests/test_laie.py
data/knowledge/laie/reports/  (gitignored)
```

---

## 4. APIs

`api_learner_analytics`, `api_teacher_analytics`, `api_parent_analytics`,  
`api_school_analytics`, `api_district_analytics`, `api_predictive_insights`,  
`api_intervention_recommendations`, `api_engagement_metrics`, `api_accessibility_metrics`,  
`api_reporting`, `api_dashboard_summaries`, `api_alerts`, `api_rebuild_index`

---

## 5. Security

- Role dashboards are data APIs — enforce RBAC at HTTP layer  
- Teachers/parents/students scoped by caller identity  
- District/government = aggregates  
- No medical diagnoses inferred or displayed  

---

## 6. Integration

VLIE `depends_on=["adaptive_learning","assessment","accessibility","curriculum"]`  
Keeps v1 key `report` (lesson complexity / reading level / objectives).

---

## 7. Testing

`tests/test_laie.py` · smoke `LAIE_SMOKE_OK`
