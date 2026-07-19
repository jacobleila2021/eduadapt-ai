"""Knowledge Ingestion Engine — end-to-end pipeline orchestrator."""

from __future__ import annotations

import json
import tempfile
import uuid
from pathlib import Path
from typing import Any

from engines.knowledge_ingestion_engine.adapters import parsers
from engines.knowledge_ingestion_engine.normalization import normalize_board, normalize_hierarchy
from engines.knowledge_ingestion_engine.schemas import CurriculumTag, KnowledgePackage
from engines.knowledge_ingestion_engine.stages.extract import (
    accessibility_metadata,
    extract_equations,
    extract_objectives_and_vocab,
    extract_questions,
    semantic_chunks,
)
from engines.knowledge_ingestion_engine.stages.indexing import index_knowledge_package
from engines.knowledge_ingestion_engine.stages.validate import validate_document
from knowledge.paths import INGEST_DIR
from knowledge.pilot_config import ACTIVE_PILOT


PACKAGE_DIR = INGEST_DIR / "kie_packages"


class KnowledgeIngestionPipeline:
    """
    Trusted entry point for educational content entering Alora AI.

    Stages: validate → parse → figures/tables → equations → objectives →
    questions → metadata → chunk → index → verified package.
    """

    def ingest(
        self,
        source: str | Path,
        *,
        board: str | None = None,
        grade: str | None = None,
        subject: str | None = None,
        curriculum: str | None = None,
        reindex: bool = True,
        extract_figures: bool = True,
    ) -> dict[str, Any]:
        path = Path(source)
        validation = validate_document(path)
        if not validation["ok"]:
            return {"ok": False, "stage": "validate", "validation": validation}

        board_n = normalize_board(board or ACTIVE_PILOT.board)
        grade_n = grade or ACTIVE_PILOT.grade
        subject_n = subject or ACTIVE_PILOT.subject
        curriculum_n = curriculum or ("NCERT" if board_n in ("CBSE", "NCERT") else board_n)

        # ZIP expands to members
        members = [path]
        tmp: Path | None = None
        if path.suffix.lower() == ".zip":
            tmp = Path(tempfile.mkdtemp(prefix="kie_zip_"))
            members = parsers.parse_zip_package(path, tmp)

        packages: list[dict[str, Any]] = []
        warnings: list[str] = list(validation.get("warnings") or [])

        for member in members:
            ext = member.suffix.lower()
            if ext not in {
                ".pdf",
                ".docx",
                ".pptx",
                ".epub",
                ".txt",
                ".html",
                ".htm",
                ".md",
                ".markdown",
                ".png",
                ".jpg",
                ".jpeg",
                ".webp",
            }:
                continue
            pkg = self._ingest_one(
                member,
                content_hash=validation["content_hash"] if member == path else "",
                board=board_n,
                grade=grade_n,
                subject=subject_n,
                curriculum=curriculum_n,
                extract_figures=extract_figures,
                reindex=reindex,
            )
            if pkg.get("warnings"):
                warnings.extend(pkg["warnings"])
            packages.append(pkg)

        if not packages:
            return {"ok": False, "stage": "parse", "errors": ["No supported members found"], "validation": validation}

        primary = packages[0]
        return {
            "ok": len(primary.get("errors") or []) == 0,
            "validation": validation,
            "package": primary,
            "packages": packages,
            "warnings": warnings,
            "package_path": primary.get("persisted_path"),
        }

    def _ingest_one(
        self,
        path: Path,
        *,
        content_hash: str,
        board: str,
        grade: str,
        subject: str,
        curriculum: str,
        extract_figures: bool,
        reindex: bool,
    ) -> dict[str, Any]:
        ext = path.suffix.lower()
        parsed: dict[str, Any]
        if ext == ".pdf":
            parsed = parsers.parse_pdf(path, extract_figures=extract_figures)
        elif ext == ".docx":
            parsed = parsers.parse_docx(path)
        elif ext == ".pptx":
            parsed = parsers.parse_pptx(path)
        elif ext == ".epub":
            parsed = parsers.parse_epub(path)
        elif ext in (".html", ".htm"):
            parsed = parsers.parse_html(path)
        elif ext in (".md", ".markdown"):
            parsed = parsers.parse_markdown(path)
        elif ext in (".png", ".jpg", ".jpeg", ".webp"):
            parsed = parsers.parse_image_ocr(path)
        else:
            parsed = parsers.parse_txt(path)

        errors = []
        warnings = []
        if parsed.get("error"):
            if parsed.get("warning"):
                warnings.append(str(parsed["error"]))
            else:
                errors.append(str(parsed["error"]))
        if parsed.get("warning") and isinstance(parsed.get("warning"), str):
            warnings.append(parsed["warning"])

        text = parsed.get("text") or ""
        pages = parsed.get("pages") or [{"page": 1, "text": text}]
        figures = list(parsed.get("figures") or [])
        tables = list(parsed.get("tables") or [])

        # Enrich page chapter from headings if missing
        from knowledge.ncert_pipeline import detect_chapter_and_headings

        chapter = 0
        chapter_title = ""
        for p in pages:
            meta = detect_chapter_and_headings(p.get("text") or "")
            if meta["chapter"]:
                chapter = meta["chapter"]
                chapter_title = meta["chapter_title"] or chapter_title
                p["chapter"] = chapter

        eqs = extract_equations(text)
        obj = extract_objectives_and_vocab(text)
        questions = extract_questions(text, chapter=chapter, topic=chapter_title, source=path.name)
        chunks = semantic_chunks(
            pages, board=board, grade=grade, subject=subject, source=str(path)
        )
        a11y = accessibility_metadata(text, figures)
        hierarchy = normalize_hierarchy(
            chapter=chapter,
            chapter_title=chapter_title,
            topic=chapter_title,
            concepts=obj.get("concepts"),
            learning_objectives=obj.get("learning_objectives"),
            original_labels={"board": board, "curriculum": curriculum},
        )

        tag = CurriculumTag(
            curriculum=curriculum,
            board=board,
            grade=str(grade),
            subject=subject,
            chapter=chapter,
            chapter_title=chapter_title,
            topic=chapter_title,
        )

        package_id = uuid.uuid4().hex[:12]
        pkg = KnowledgePackage(
            package_id=package_id,
            source_path=str(path),
            source_hash=content_hash,
            curriculum={**tag.to_dict(), "hierarchy": hierarchy},
            text_chunks=chunks,
            figures=figures,
            tables=tables,
            equations=eqs,
            questions=questions,
            vocabulary=obj.get("vocabulary") or [],
            learning_objectives=obj.get("learning_objectives") or [],
            concepts=obj.get("concepts") or [],
            accessibility=a11y,
            citations=[f"[{curriculum} {board} Class {grade} {subject} Ch.{chapter}]"],
            errors=errors,
            warnings=warnings,
        )

        data = pkg.to_dict()
        if reindex and not errors:
            data["index_status"] = index_knowledge_package(data)
        else:
            data["index_status"] = {"skipped": True}

        PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
        out_path = PACKAGE_DIR / f"{package_id}.json"
        out_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        data["persisted_path"] = str(out_path)
        return data

    def reprocess(self, package_id: str, **kwargs: Any) -> dict[str, Any]:
        path = PACKAGE_DIR / f"{package_id}.json"
        if not path.is_file():
            return {"ok": False, "error": "Package not found"}
        data = json.loads(path.read_text(encoding="utf-8"))
        source = data.get("source_path")
        if not source or not Path(source).is_file():
            return {"ok": False, "error": "Original source missing — cannot reprocess"}
        return self.ingest(source, **kwargs)

    def search_concepts(self, query: str, k: int = 5) -> list[dict]:
        return self._search_collection("kie_curriculum_chunks", query, k)

    def search_figures(self, query: str, k: int = 5) -> list[dict]:
        return self._search_collection("kie_figures", query, k)

    def search_formulae(self, query: str, k: int = 5) -> list[dict]:
        return self._search_collection("kie_formulas", query, k)

    def search_questions(self, query: str, k: int = 5) -> list[dict]:
        return self._search_collection("kie_question_bank", query, k)

    def _search_collection(self, name: str, query: str, k: int) -> list[dict]:
        try:
            from knowledge.paths import CHROMA_DIR
            import chromadb

            client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            col = client.get_or_create_collection(name=name)
            res = col.query(query_texts=[query], n_results=k)
            docs = (res.get("documents") or [[]])[0]
            metas = (res.get("metadatas") or [[]])[0]
            ids = (res.get("ids") or [[]])[0]
            return [
                {"id": ids[i], "document": docs[i], "metadata": metas[i]}
                for i in range(len(docs))
            ]
        except Exception:
            return []
