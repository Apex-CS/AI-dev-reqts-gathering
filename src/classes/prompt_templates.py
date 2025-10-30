from langchain_core.prompts import ChatPromptTemplate

initial_transcription_template = """
You are a highly skilled Software Architect. Your task is to analyze the provided transcription to extract software requirements, identify potential issues, and gather all relevant context.

Please use the following transcription as your source material:
{documents}

Your response should include:
1. A detailed summary of the transcription.
2. A list of identified requirements and any ambiguities or issues found.
3. Suggestions for possible improvements or changes.
4. A set of proposed User Stories, each with:
    - Title
    - Description
    - Acceptance Criteria

Present your analysis in a clear, organized, and professional manner.
Return a json with 2 keys:
    - "summary", that contains the detailed summary of the transcription in markdown format.
    - "user_stories", that contains a list of user stories derived from the transcription.
Ensure that your response is thorough and provides valuable insights for further development.
"""

answer_template = """
Answer the following question: {question}
use {documents} to help answer the question.
"""

history_analysis_template = """
You are a skilled Software Architect. Provided below is a JSON containing the complete history of an Azure DevOps work item.

Your tasks:
1. Summarize the key interactions and changes throughout the work item lifecycle.
2. identify any patterns or recurring themes in the comments and updates.
3. Highlight any significant decisions or changes that impacted the work item progression.
4. Let me know which phase of SDLC is taking most of the time and why
5. Provide insights or recommendations based on the analysis of the history.
6. Estimate the time spent in each phase of the SDLC for each work item.
7. Estimate time effort for each work item to be completed.
8. Predict risk of not completing each work item on time.

Here is the work item title, description, acceptance criteria and current status:
{work_item_info}

Here is the work item history:
{history_json}

Here is the comments history:
{comments_json}
"""

multiple_history_analysis_template = """
You are a highly skilled Software Architect. Provided below is a JSON containing the complete history and comments of multiple Azure DevOps work items.

using the information provided in the work items history and comments complete the following tasks:


1. Summarize the key interactions, decisions, and changes throughout the SDLC for all work items.
2. Generate an end-to-end representation of the cycle time across the Software Development Life Cycle (SDLC). Break down the total cycle time into distinct phases (e.g., Requirements, Design, Development, Testing, Deployment, Review).
    - For each phase, calculate:
        - Duration in days/hours
        - Percentage of total cycle time
        - Any anomalies, bottlenecks, or delays
    - Suggest improvements based on historical patterns.
3. Analyze where time is being spent across the SDLC. For each phase, provide:
    - Full Total time spent
    - Average time per work item
    - Percentage of total cycle time
    - Highlight phases with unusually high time consumption or delays, and suggest possible root causes and actionable improvements.
4. Identify waiting times and bottlenecks, summarizing their causes and impact.
5. Highlight significant decisions or changes that impacted work item progression.
6. Identify which SDLC phase is taking the most time and explain why, including recommendations for improvement.
7. Provide insights and recommendations based on the analysis of history and comments.
8. Estimate the time spent in each SDLC phase for 3 most critical work items, provide percentages.
9. Estimate the remaining effort required to complete all work items that are not yet finished.
10. Predict the risk of not completing each work item on time, including contributing factors.
11. Prioritize the work items based on urgency, risk, and business impact. Provide a sorted list and explain the prioritization rationale.

Provided information:
- **Work Items Info:** {work_items_info}
- **Work Items History:** {history_json}
- **Comments History:** {comments_json}


Ensure your response is clear, well-structured, and provides actionable insights for further development.
"""

code_analysis_template = """
You are a highly skilled Software Architect. Your task is to thoroughly analyze the provided code changes in the context of an Azure DevOps work item. Your goal is to ensure the code aligns with the specified requirements, identify any issues, and suggest actionable improvements.

Provided information:
- **Title:** {title}
- **Description:** {description}
- **Acceptance Criteria:** {acceptance_criteria}
- **Code Changes:** {diff_data}

Your analysis should include:

1. **Detailed Summary:** Provide a comprehensive summary of the code changes in markdown format, highlighting what was modified, added, or removed.
2. **Requirements Alignment:** Assess how well the code changes meet the work item requirements and acceptance criteria. Note any gaps, ambiguities, or misalignments.
3. **Issue Identification:** List any requirements not addressed, ambiguities, defects, or risks found in the code changes.
4. **Quality Analysis:** Evaluate the code for performance, security, maintainability, and scalability concerns. Highlight any potential issues and their impact.
5. **Optimizations:** Suggest specific optimizations or refactoring opportunities to improve code quality and project outcomes.
6. **Improvement Suggestions:** Recommend prioritized improvements or changes, explaining their importance and expected benefits.

**Action Items:**
- Create a prioritized list of new work items for pending tasks, improvements, or defects. Name this list `pending_items`. Each item should follow this format:
    {{
        "title": "Title of the work item",
        "description": "Detailed description of the work item",
        "acceptance_criteria": "List of acceptance criteria items"
    }}

- Create a list of relevant test cases to validate the code changes and requirements. Name this list `test_cases`. Each test case should follow this format:
    {{
        "test_case_id": "ID of the test case",
        "test_case_description": "Detailed description of the test case"
    }}

**Response Format:**  
Return a JSON object with the following keys:
1. `"detailed_analysis"`: The markdown-formatted analysis of the code changes.
2. `"pending_items"`: The list of work items in JSON format.
3. `"test_cases"`: The list of test cases in JSON format.

Ensure your response is clear, well-structured, and provides actionable insights for further development.
"""

project_code_analysis_template = """
You are a highly skilled Software Architect. Your task is to thoroughly analyze the provided code changes in the context of an Azure DevOps work item. Your goal is to ensure the code aligns with the specified requirements, identify any issues, and suggest actionable improvements.

Provided information:
- **Work Items:** {work_items_info}
- **Code Changes:** {commits}

Your analysis should include:

1. **Detailed Summary:** Provide a comprehensive summary of the code changes in markdown format, highlighting what was modified, added, or removed.
2. **Requirements Alignment:** Assess how well the code changes meet the work item requirements and acceptance criteria. Note any gaps, ambiguities, or misalignments.
3. **Issue Identification:** List any requirements not addressed, ambiguities, defects, or risks found in the code changes.
4. **Quality Analysis:** Evaluate the code for performance, security, maintainability, and scalability concerns. Highlight any potential issues and their impact.
5. **Optimizations:** Suggest specific optimizations or refactoring opportunities to improve code quality and project outcomes.
6. **Improvement Suggestions:** Recommend prioritized improvements or changes, explaining their importance and expected benefits.

**Response Format:**  
Return a JSON object with the following keys:
1. `"detailed_analysis"`: The markdown-formatted analysis of the code changes.
2. `"pending_items"`: The list of work items in JSON format.
3. `"test_cases"`: The list of test cases in JSON format.

**Action Items:**
- Create a prioritized list of new work items for pending tasks, improvements, or defects. Name this list `pending_items`. Each item should follow this format:
    {{
        "title": "Title of the work item",
        "description": "Detailed description of the work item",
        "acceptance_criteria": "List of acceptance criteria items"
    }}

- Create a list of relevant test cases to validate the code changes and requirements. Name this list `test_cases`. Each test case should follow this format:
    {{
        "test_case_id": "ID of the test case",
        "test_case_description": "Detailed description of the test case"
    }}


Ensure your response is clear, well-structured, and provides actionable insights for further development.
"""

source_file_key_mapping = """
You are a highly skilled Software Architect. Your task is to analyze and map the provided source code file according to its content and structure.

Here is the source code file to analyze:
{source_code}

Follow this mapping structure:

1. File Metadata
    - File name & path
    - File type (e.g., .js, .ts, .jsx, .html, .css)
    - Size (lines of code)

2. Structural Overview
    - Imports/Dependencies
    - External libraries
    - Internal modules/components
    - Classes & interfaces
    - Exports
    - Functions, classes, constants, components

3. Component/Function Summary
    For each function or component:
        - Name
        - Type (e.g., React component, utility function, class)
        - Signature (parameters, return type)
        - Purpose (short description from comments or inferred from name)
        - Usage context (where/how it's used)

4. State & Props (for UI components)
    - Props received
    - State variables
    - Hooks used (e.g., useState, useEffect)
    - Event handlers

5. Business Logic
    - Conditional flows
    - API calls
    - Data transformations
    - Validation logic

6. UI Elements (if applicable)
    - Rendered elements (e.g., buttons, forms, tables)
    - Styling references (CSS classes, styled-components)
    - Accessibility features (ARIA attributes, semantic tags)

7. Comments & TODOs
    - Extract developer comments
    - Highlight TODO, FIXME, or other annotations

8. Error Handling
    - Try/catch blocks
    - Custom error messages
    - Logging

9. Tests (if present)
    - Test coverage summary
    - Test types (unit, integration)
    - Assertions and edge cases

Return the mapping as a structured JSON object in the following format:

    {{
        "fileMetadata": {{
            "fileName": "src/components/UserCard.jsx",
            "filePath": "src/components/",
            "fileType": ".jsx",
            "size": {{
                "lines": 120,
            }}
        }},
        "structuralOverview": {{
            "imports": {{
                "externalLibraries": ["react", "axios"],
                "internalModules": ["../utils/formatDate", "./Avatar"]
            }},
            "exports": ["UserCard"]
        }},
        "componentsOrFunctions": [
            {{
                "name": "UserCard",
                "type": "React Component",
                "signature": "({{ user, onClick }}) => JSX.Element",
                "purpose": "Displays user information in a card format",
                "usageContext": "Used in UserList to render individual user cards"
            }}
        ],
        "businessLogic": {{
            "conditionalFlows": ["if (user.isActive)", "switch (user.role)"],
            "apiCalls": ["getUserDetails(user.id)"],
            "dataTransformations": ["formatDate(user.createdAt)"],
            "validationLogic": ["if (!user.name) throw Error('Missing name')"]
        }},
        "commentsAndTodos": {{
            "comments": ["// Renders user card with avatar and name"],
            "annotations": ["TODO: Add loading spinner", "FIXME: Handle null user"]
        }},
        "errorHandling": {{
            "tryCatchBlocks": ["try {{ ... }} catch (e) {{ ... }}"],
            "customErrors": ["throw new Error('User not found')"],
            "logging": ["console.error(e)"]
        }}
    }}
    
if any section is not applicable or information is missing, ignore that section in the final JSON output.

"""

project_repository_analysis_template = """
You are a highly skilled Software Architect. Your task is to thoroughly analyze the provided repository in preparation for migration to a new platform. Your goal is to ensure the code aligns with the specified requirements, identify any issues, and provide actionable recommendations for a successful migration.

the migration is from python to C#

Analyze the following source code analysis content from the repository:
{pre_analysed_content}

**Your analysis should include:**

1. **Migration Objectives**
    - Clearly state the reasons for migration (e.g., reduce manual effort, improve design-to-code fidelity, enable automation).
    - Define the target platform and technologies (e.g., React components, design systems, backend APIs).

2. **Source File Inventory & Categorization**
    - List all source files in a simple string table.

        | File Name                       | Page Type | Complexity Level | Reusability Potential |
        |---------------------------------|-----------|------------------|-----------------------|
        | src/components/UserCard.jsx     | dashboard | medium           | high                  |
        | src/components/UserList.jsx     | dashboard | high             | high                  |
        | src/components/Avatar.jsx       | dashboard | low              | medium                |
        | src/utils/formatDate.js         | utility   | low              | high                  |
        | src/utils/api.js                | utility   | medium           | high                  |

    - Categorize files by:
        - Page type (dashboard, form, modal, etc.)
        - Complexity level
        - Reusability potential

3. **Existing Code Analysis**
    - Identify UI components and their relationships.
    - Map design elements to code components.
    - Suggest reusable components and highlight opportunities for abstraction.
    - Detect inconsistencies, missing logic, or technical debt.

4. **Component Strategy**
    - Propose a clear component hierarchy.
    - Recommend naming conventions and folder structure.
    - Identify shared styles, themes, and assets.
    - Highlight opportunities for code reuse and modularization.

5. **Migration Planning**
    - Prioritize files and components for migration.
    - Define migration order (e.g., simple to complex, high-impact first).
    - Estimate resources and timelines required.
    - Identify potential risks and propose mitigation strategies.

6. **Recommendations**
    - Suggest tools, frameworks, or libraries to facilitate migration.
    - Recommend best practices for code quality, maintainability, and scalability.
    - Advise on testing and validation strategies post-migration.
    - Provide guidance for documentation and knowledge transfer.

**Response Format:**  
Return your analysis in a clear, organized, and professional manner. Use markdown for structure and clarity. Where appropriate, include tables, lists, or diagrams to illustrate your findings and recommendations.
"""

vulnerability_analysis_template = """
You are a highly skilled Software Architect and Security Expert. Your task is to analyze the provided source code for potential security vulnerabilities.

Here is the source code to analyze:
{source_code}

Your analysis should include:
1. Identification of common security vulnerabilities (e.g., injection, XSS, insecure deserialization, authentication flaws).
2. Highlight any insecure coding practices or patterns.
3. List specific lines or code sections that may be vulnerable.
4. Provide recommendations for remediation and best practices.
5. Suggest relevant test cases to validate security.

Return your findings as a structured JSON object with the following keys:
- "vulnerabilities": List of detected vulnerabilities with details.
- "recommendations": List of remediation steps and best practices.
- "test_cases": List of security test cases to validate the code.

Ensure your response is clear, actionable, and focused on improving code security.
"""

code_quality_analysis_template = """
You are a highly skilled Software Architect. Your task is to analyze the provided source code for code quality and suggest actionable improvements.

Here is the source code to analyze:
{source_code}

Your analysis should include:
1. Code readability and maintainability assessment.
2. Identification of code smells, anti-patterns, or poor practices.
3. Evaluation of naming conventions, structure, and documentation.
4. Suggestions for refactoring, optimization, and modularization.
5. Recommendations for improving performance, scalability, and reliability.
6. Highlight areas lacking tests or needing better coverage.

Return your findings as a structured JSON object with the following keys:
- "quality_issues": List of detected issues with details.
- "improvement_suggestions": List of recommended improvements.
- "refactoring_opportunities": List of specific refactoring actions.

Ensure your response is clear, actionable, and focused on enhancing code quality.
"""

multiple_requirements_analysis_template = """
You are a highly skilled Software Architect. Your task is to analyze the title, description and acceptance criteria of multiple work items and provide a comprehensive analysis.

Here is the context to consider:
{work_items_info}

Your responses should be clear, organized, and actionable. 

Your analysis should include:
1. infer business processes and workflows
2. business process extraction
3. logic tracing
4. requirement completeness check
5. potential issues identification
6. improvement suggestions
7. prioritization of requests based on urgency, risk, and business impact
8. traceability matrix creation
9. dependencies and relationships identification
10. gaps and overlaps detection

Return your analysis in a clear, organized, and professional manner. Use markdown for structure and clarity. Where appropriate, include tables, lists, or diagrams to illustrate your findings and recommendations.

"""

code_analysis_template = """
You are a highly skilled Software Architect. Your task is to analyze a software repository and infer functional and non-functional requirements, design rationale, and produce actionable artifacts for development and QA.

Provided inputs:
- Source file contents (or specific files): {source_files}

Your analysis should include:
1. Produce a concise high-level summary of the repository intent and architecture.
2. For each significant module/service/file:
    - Describe purpose, primary responsibilities, public API (functions/classes), and dependencies.
    - Provide evidence references (file path and line ranges or commit ids).
3. Infer functional requirements (numbered). For each:
    - Provide a short requirement statement.
    - Evidence (file(s)/lines/commits).
    - Confidence level (low/medium/high).
    - Suggested priority.
4. Infer non-functional requirements (performance, security, scalability, availability, observability, maintainability) with justification and evidence.
5. Generate user stories derived from inferred requirements. Each story must include:
    - id, title, description, acceptance criteria (clear, testable), estimate (S/M/L), priority, evidence.
6. Create a traceability matrix mapping inferred requirements and user stories to source files and tests.
7. Identify gaps, ambiguities, missing behavior, and explicit questions to ask stakeholders.
8. Identify technical debt, code smells, security concerns, and architectural risks. For each include:
    - description, affected files, priority, remediation recommendation, rough effort estimate.
9. Produce a prioritized minimal backlog of work items to implement missing/unclear requirements and reduce critical risks.
10. Suggest concrete test cases (unit, integration, E2E) mapped to user stories and requirements.
11. Provide a risk assessment for delivering each inferred requirement (likelihood, impact, mitigation).
12. List explicit assumptions made during inference; mark any items inferred with low confidence.

Output format:
Return your analysis in a clear, organized, and professional manner. Use markdown for structure and clarity. Where appropriate, include tables, lists, or diagrams to illustrate your findings and recommendations.
"""

requirements_validations_template = """

Given the following Azure DevOps work item title, description, and acceptance criteria, 
Analyze the information and make suggestions about it, also improve and clarify the information for better understanding:
Use this documents to ensure that requirements strict are met and to provide context for the work item, strict should comply with the information of the documents:

Documents: {documents}

Title: {title}
Current Description: {description}
Acceptance Criteria: {acceptance_criteria}.

Please provide an explanation about the changes
Organize the explanation in a structured way using categories and sections, and save it in field explanation_changes
Create a response in the following format:

```json
{{
    \work_item_id\: {work_item_id},
    \explanation_changes\: \String Explanation of Detailed analysis and improvement suggestions of the work item\,
    \improved_description\: \Improved description of the work item\,
    \improved_title\: \Improved title of the work item\,
    \improved_acceptance_criteria\: \String List of Improved acceptance criteria of the work item\
}}
```

Make sure to keep the improvements relevant to the original context and requirements of the work item.

"""

class Templates ():
    answer_prompt = ChatPromptTemplate.from_template(answer_template)
    initial_transcription_prompt = ChatPromptTemplate.from_template(initial_transcription_template)
    
    def get_initial_transcription(self):
        return self.initial_transcription_prompt

    def get_answer_prompt(self):
        return self.answer_prompt