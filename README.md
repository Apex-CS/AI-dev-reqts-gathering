# AI-dev-reqts-gathering

Convert meeting transcripts, work item histories and repository changes into clear, actionable software requirements and code-quality insights using guided LLM prompts and a lightweight Streamlit UI.

## One-line summary
Turn conversations and code change context into verified user stories, requirements, and code analysis — saving time in backlog grooming and reducing rework.

## What this project does
AI-dev-reqts-gathering ingests meeting transcripts, ALM work-item data and source repositories, then:
- Summarizes discussions or code changes.
- Extracts explicit and implicit software requirements.
- Flags ambiguities, missing information and risks.
- Generates actionable User Stories with titles, descriptions and acceptance criteria.
- Produces code and repository analysis aligned to work items (quality, gaps, migration planning).
- Supports human-in-the-loop review through the Streamlit UI.

This tool helps teams rapidly transform raw meeting notes and code diffs into structured requirements and suggested work items, accelerating planning and reducing overlooked details.

## Highlights / Features
- LLM-driven analysis using structured prompt templates.
- Streamlit UI with:
  - Repository Analysis (code quality, migration planning, overall analysis).
  - Requirements Analysis (suggested titles, descriptions and acceptance criteria).
  - Project Panel (ALM tool integration and work-item analysis).
  - Global Settings (LLM config, project administration).
- Prompt templates that return JSON-ready outputs for automation.
- ALM tool connector hooks (save tool configuration; extend to create issues/tickets).
- Configurable analysis types: Code Quality, Security Vulnerabilities, Dependency Analysis, Migration Planning, and more.

## Architecture (high level)
- UI: Streamlit pages under pages/*.py (Repository_Analysis, Project_Panel, Requirements_Analysis, Global_Settings).
- Prompt engine: src/classes/prompt_templates.py (all major LLM prompts).
- Settings and persistence: src/functions/settings.py (project/tool settings, DB-backed).
- Helpers: src/functions/* for invoking the LLM, extracting JSON from responses and handling history.
- Extensible outputs: prompts are designed to produce structured JSON so outputs can be exported to JIRA/GitHub/Confluence.

## Quickstart (local)
Prerequisites:
- Python 3.10+ recommended
- pip or poetry
- LLM provider credentials (e.g., OpenAI key or equivalent)
- Git access to repositories you want to analyze

Install:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run locally:
```bash
streamlit run pages/Repository_Analysis.py
# or run the repository root app entrypoint if present
```

Configuration:
- Set your LLM credentials as environment variables (e.g., OPENAI_API_KEY).
- Use Global Settings page to add projects and ALM tool configurations (URLs/tokens).

## Example prompt (concept)
You are a highly skilled Software Architect. Your task is to analyze the provided transcription to extract software requirements, identify potential issues, and gather all relevant context.

Please use the following transcription as your source material:
{documents}

Your response should include:
1. A detailed summary of the transcription.
2. A list of identified requirements and any ambiguities or issues found.
3. Suggestions for possible improvements or changes.
4. A set of proposed User Stories (Title, Description, Acceptance Criteria) in structured form.

## Expected outputs
- Human-readable summary (Markdown).
- Structured JSON lists of:
  - Extracted requirements (explicit and implicit).
  - Ambiguities and suggested clarifying questions.
  - User stories with acceptance criteria.
- Optional: code-quality analysis JSON (quality issues, suggested improvements, refactoring opportunities).

## Recommendations for users / operators
- Provide clear, high-quality transcripts (or integrate STT with speaker diarization) — analysis quality depends on input clarity.
- Validate LLM outputs via the UI before exporting to ALM systems — prompts can hallucinate; use provenance links to transcript segments.
- Create domain templates (finance, healthcare, e-commerce) to bias extraction toward relevant terminology and constraints.
- For sensitive data, run the application in an isolated network or on-premise environment.

## Suggested next improvements (roadmap)
- Add automated audio → transcript pipeline with timestamps and speaker diarization.
- Display provenance and confidence scores for each generated requirement (link to transcript lines/timestamps).
- Add export connectors (JIRA, GitHub Issues, Confluence) with one-click create.
- Build human-in-the-loop editor and approval workflow in the UI.
- Add unit tests / CI and a sample data folder with transcripts and golden outputs.

## Contributing
Contributions are welcome — please open issues for feature requests and bug reports. If you plan to contribute, please:
- Add unit tests for new functions.
- Document changes to any prompt templates or outputs.

## Security & Privacy
Handle transcripts and repository data as sensitive. Consider:
- Encrypting data at rest and in transit.
- Deploying on-premise for highly sensitive code or meeting audio.
- Limiting LLM access to sanitized or anonymized inputs where necessary.

## License
(Choose and add a license, e.g., MIT, Apache-2.0)

## Contact
For questions and help: open an issue or contact the maintainer(s) in the repository.
