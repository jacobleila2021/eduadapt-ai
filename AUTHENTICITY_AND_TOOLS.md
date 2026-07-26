# EduAdapt AI — Authenticity & Development Tools Statement

**Project:** EduAdapt AI  
**Developer:** jacobleila2021  
**Date:** June 2026  

---

## Official repository (source of truth)

**GitHub:** https://github.com/jacobleila2021/eduadapt-ai  

All application code is version-controlled on GitHub. Judges can verify file history, commits, and project structure at this link.

**Live demo:** https://eduadapt-ai.streamlit.app  

---

## Tools used to build this project

| Tool | Used? | Role |
|------|-------|------|
| **Cursor** | Yes | Primary IDE; AI-assisted coding, debugging, deployment setup, and documentation |
| **Lovable** | No | Not used for this project |
| **Emergent** | No | Not used for this project |
| **Streamlit** | Yes | Web application framework |
| **OpenAI API** | Yes | GPT model for lesson differentiation |
| **Python 3** | Yes | Backend language |
| **GitHub** | Yes | Code hosting and submission |
| **Streamlit Community Cloud** | Yes | Live deployment for judges |

---

## Authenticity statement

This project was developed by the submitter with **Cursor** as the development environment. AI assistance in Cursor was used to:

- Scaffold the Streamlit application structure
- Implement PDF/DOCX parsing, analytics, and OpenAI integration
- Debug API key configuration and deployment to Streamlit Cloud
- Create pitch deck assets and submission documentation

**All code resides in the public/private GitHub repository above.** The submitter reviewed, tested, and deployed the application. Custom logic includes lesson parsing, differentiation prompts, analytics engine, and EdTech UI design.

**No code was generated solely by Lovable or Emergent** for this submission.

---

## How judges can verify

1. **GitHub repo** — Inspect `app.py`, `ai_generator.py`, `requirements.txt`, commit history  
2. **Live app** — Test at https://eduadapt-ai.streamlit.app (Use Sample Lesson → Generate)  
3. **Local run** — Clone repo, add `OPENAI_API_KEY` in `.env`, run `run.bat`  
4. **Dependencies** — Listed in `requirements.txt` (standard Python packages)

---

## What is NOT in the repository (by design)

- `.env` — Contains private OpenAI API key (excluded via `.gitignore`)
- API keys in Streamlit Cloud Secrets only (not in source code)

---

## Contact

GitHub: https://github.com/jacobleila2021  
