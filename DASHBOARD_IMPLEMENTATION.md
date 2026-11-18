# FlowWise dashboard implementation

## Purpose

FlowWise is an Applicant Tracking System (ATS). Its backend stores candidates,
CV files, parsed CV data, jobs, applications, and recruitment statuses. The
dashboard endpoint provides the frontend with the data needed to analyze one
candidate and that candidate's applications.

The dashboard does not calculate an ATS score from raw CV text yet. It reads
the score saved on each application. The matching engine can populate those
fields later.

## Request flow

```text
Frontend
  -> GET /api/v1/dashboard/candidates/{candidate_id}
FastAPI route: src/routes/dashboard_router.py
  -> DashboardRepository
SQLAlchemy query
  -> PostgreSQL
Candidate -> CV file -> Application -> Job
  -> Pydantic response schema
  -> JSON response to the frontend
```

## Dashboard endpoint

The endpoint is declared in `src/routes/dashboard_router.py`:

```text
GET /api/v1/dashboard/candidates/{candidate_id}
GET /api/v1/dashboard/candidates/{candidate_id}?job_id={job_id}
```

The response includes candidate identity, applications, job information,
application status, ATS score, score breakdown, parsed CV profile data,
timestamps, status counts, funnel yield ratios, and offer-to-hired rate.

The response shape is defined in `src/schema/dashboard_schema.py`.

## Why the score belongs to an application

An ATS score depends on the job. A candidate may be an excellent match for
one job and a weak match for another:

```text
Candidate A -> Backend Developer -> 91
Candidate A -> Data Scientist    -> 64
```

For that reason, `ats_score` and `score_breakdown` are stored on the
`applications` table in `src/models/db/flow_wise/schema/application.py`.

The database migration is:

`src/models/db/flow_wise/alembic/versions/c2d4e8b7a901_add_ats_scores_to_applications.py`

## Database relationships

The application does not directly store `candidate_id`. The relationship is:

```text
Candidate.id -> CvFile.candidate_id
CvFile.id    -> Application.cv_file_id
Application.job_id -> Job.id
```

Therefore the dashboard repository joins the CV file table when it searches
for applications belonging to a candidate. `CvParsed` is related one-to-one
with `CvFile` and contains extracted profile JSON.

## Repository behavior

`src/repositories/dashboard_repository.py` is responsible only for database
retrieval:

1. Find the candidate by ID.
2. Return no candidate and an empty list if it does not exist.
3. Join applications to their CV files.
4. Filter CV files by the requested candidate.
5. Eagerly load the related job and parsed CV.
6. Order applications from newest to oldest.
7. Optionally filter by job ID.
8. Return SQLAlchemy model objects to the route.

The repository does not know about HTTP status codes or frontend chart
formatting.

## Router behavior

`src/routes/dashboard_router.py` is responsible for the API layer:

1. Receive the candidate ID and optional job ID.
2. Receive a database session through FastAPI dependency injection.
3. Call the dashboard repository.
4. Return HTTP 404 when the candidate does not exist.
5. Count application statuses.
6. Calculate funnel percentages safely, including zero totals.
7. Convert database models into Pydantic response models.
8. Return JSON validated against `CandidateDashboardResponse`.

The current funnel ratios are:

```text
received -> screened
screened -> shortlisted
shortlisted -> interview
interview -> offer
offer -> hired
```

The current `offer_acceptance_rate` uses hired applications divided by offer
applications. The data model has `OFFER` and `HIRED`, but not a separate
`OFFER_ACCEPTED` status yet.

## Job requirement correction

Migration `aa7da30d5100` replaced the old job-requirement columns `type`,
`content`, and `required` with a JSONB column called `schema_definition`.
The request and response schemas now match the actual database model. This
prevents the repository from passing fields to SQLAlchemy that no longer exist
on the `JobRequirement` model.

The repository package export was also corrected from the nonexistent
`JobRequirement` symbol to `JobRequirementRepository`.

## Merge conflict correction

The branch was in an interrupted merge state. Conflicts existed in
`src/main.py` and `src/models/db/flow_wise/schema/candidate.py`.

The final resolution keeps the dashboard router, HR authentication routes, HR
admin routes, HR member routes, and the read-only candidate-to-application
relationship used by dashboard data.

## Migration ordering correction

The ATS-score migration was originally connected directly to `bdf653dcab64`,
while `aa7da30d5100` was already the later job-requirement migration from that
revision. The ATS migration now follows `aa7da30d5100`, giving Alembic one
linear migration path instead of two competing heads.

## Testing and validation

Run these commands from the repository root:

```powershell
git status
rg -n "^(<<<<<<<|=======|>>>>>>>)" src
C:/Users/pc/anaconda3/envs/flow-wise/python.exe -m compileall -q src
```

If dependencies are installed, run an application import check:

```powershell
$env:PYTHONPATH = "src"
C:/Users/pc/anaconda3/envs/flow-wise/python.exe -c "from main import app; print(app.routes)"
```

For a real dashboard request, the database must be running, migrations must
be applied, and a candidate, CV file, job, and application must exist.

## Known remaining product work

- The ATS matching engine still needs to calculate and save scores.
- The CV processing endpoint still needs to parse uploads and populate
  `CvParsed.parsed_data`.
- Application creation and status-transition endpoints need complete API
  coverage.
- Authentication and authorization should protect dashboard access in
  production.
- Uploaded test PDFs should remain local or be ignored by Git rather than
  committed as source files.
