# HR portal – integration guide

All HR code is in new files. To switch it on, **you** make the edits below to
existing files. Nothing here has been applied to your files. The same edits were
applied to a test copy and checked end-to-end against PostgreSQL 16
(67/67 API checks passed through your real `main.py`, migration up → down → up
OK, `alembic check` clean for the new tables).

**Status (2026-11-16): fixes A–C and edits 1–7 are applied. Edit 8 was skipped (optional).**
What is left for you: create `src/.env` (see edit 7) and run `alembic upgrade head`.
Edits 5–8 are wiring/config.

---

## New files (already created)

All HR files sit in the existing folders. No new folders were created.

```
src/
├── controllers/
│   ├── hr_auth_controller.py        # register admin, login, change password
│   ├── hr_admin_controller.py       # company profile + member lifecycle
│   └── hr_member_controller.py      # job titles, postings, applicant review (+ read-only reader for the admin)
├── repositories/                    # all queries filtered by company_id; they flush, controllers commit
│   ├── hr_account_repository.py
│   ├── hr_company_repository.py
│   ├── job_title_repository.py
│   ├── posting_repository.py
│   └── applicant_repository.py
├── routes/
│   ├── hr_auth_router.py            # /api/v1/hr/auth/...
│   ├── hr_admin_router.py           # /api/v1/hr/admin/...   (HR Admin only)
│   └── hr_member_router.py          # /api/v1/hr/...         (HR Member only)
├── schema/
│   ├── hr_common_schema.py          # Page, password rules
│   ├── hr_auth_schema.py
│   ├── hr_company_schema.py
│   ├── hr_member_schema.py
│   ├── job_title_schema.py
│   ├── posting_schema.py
│   └── applicant_review_schema.py
├── helpers/
│   ├── hr_auth_settings.py          # JWT settings (reads src/.env)
│   ├── security.py                  # passlib bcrypt + PyJWT
│   ├── rbac.py                      # get_current_hr_user, require_admin, require_member
│   ├── hr_errors.py
│   └── hr_utils.py                  # UTC time helpers, LIKE escaping
├── models/enums/hr_role_enum.py
├── models/enums/hr_account_status_enum.py
├── models/db/flow_wise/schema/job_title.py
└── models/db/flow_wise/alembic/versions/c3f1a9e7b2d4_hr_rbac_and_job_titles.py
```

The new files import each other by full module path (for example
`from schema.posting_schema import PostingOut`), so the existing
`__init__.py` files of these folders do **not** need new lines.

---

## Fixes to existing code that the folders need (A–C) — ✅ ALREADY APPLIED (2026-11-16)

> These three fixes have been made in the repo. They are kept here to explain what changed and why.

Python always runs a folder's `__init__.py` before loading any file inside it.
Today `schema/__init__.py` and `repositories/__init__.py` both crash on import,
so **every** file in those folders fails to load, the new HR ones included.
These are existing bugs, not caused by the HR work; they would break your own
job/candidate/company endpoints too as soon as something imports them.

### A. `src/schema/job_requirement_schema.py`

**Why:** it imports `RequirementType` and uses `type`, `content` and `required`.
Migration `aa7da30d5100` removed all of these and replaced them with the JSONB
column `schema_definition` (plus `last_edited`). The enum no longer exists, so
the import fails: `ImportError: cannot import name 'RequirementType'`. Because
`schema/__init__.py` imports this file, the whole `schema` folder fails.

A version that matches the current `JobRequirement` model (tested). Whoever
owns job requirements should check the field rules:

```python
from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class JobRequirementCreateRequest(BaseModel):
    job_id: int = Field(..., gt=0)
    schema_definition: dict[str, Any]
    weight: float = Field(default=1.0, gt=0)


class JobRequirementUpdateRequest(BaseModel):
    schema_definition: dict[str, Any] | None = None
    weight: float | None = Field(None, gt=0)

    @model_validator(mode="after")
    def validate_non_nullable_fields(self):
        for field_name in ("schema_definition", "weight"):
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(f"{field_name} cannot be null.")

        return self


class JobRequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    schema_definition: dict[str, Any]
    weight: float
    last_edited: datetime
```

### B. `src/repositories/hr_users_repository.py` and `src/repositories/company_repository.py`

**Why:** both import `from src.models....`. The app runs from inside `src/`
(that is why `main.py` uses `from models...`), so `src` is not a module there:
`ModuleNotFoundError: No module named 'src'`. And even where `src` can be
found, it would load every model a second time under another name, which fails
with `Table 'hr_users' is already defined`.

Change, in both files:

```python
from src.models.db.flow_wise.schema.hr_user import HRUser     # hr_users_repository.py
from src.models.db.flow_wise.schema.company import Company    # company_repository.py
```
to
```python
from models.db.flow_wise.schema.hr_user import HRUser
from models.db.flow_wise.schema.company import Company
```

### C. `src/repositories/candidate_repository.py`

**Why:** it imports `CandidateUpdateRequest`, but `schema/candidate_schema.py`
defines that class as `CandidateUpdateStatus`. The import fails, and since
`repositories/__init__.py` imports this file, the whole folder fails.

Rename `CandidateUpdateRequest` → `CandidateUpdateStatus` (2 places: the import
on line 5 and the type hint around line 53). Alternatively, rename the class in
the schema file instead; either works, as long as both use the same name.

---

## 1. `src/models/db/flow_wise/schema/hr_user.py` — ✅ APPLIED

**Why:** the RBAC logic needs role, account status, approval info and a token
version on each HR user. The migration adds these columns to the database; the
model has to declare them too.

Replace the sqlalchemy import line with:

```python
from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Index, Integer, String, text

from models.enums.hr_account_status_enum import HRAccountStatus
from models.enums.hr_role_enum import HRRole
```

Right under `__tablename__ = "hr_users"` add:

```python
    __table_args__ = (
        # only ONE admin per company
        Index(
            "uq_hr_users_one_admin_per_company",
            "company_id",
            unique=True,
            postgresql_where=text("role = 'ADMIN'"),
        ),
    )
```

Right under the `created_at = ...` line add:

```python
    # ---- HR RBAC fields (migration c3f1a9e7b2d4) ----
    role = Column(SQLEnum(HRRole, name="hr_role"), nullable=False, default=HRRole.MEMBER, server_default="MEMBER")
    status = Column(SQLEnum(HRAccountStatus, name="hr_account_status"), nullable=False, default=HRAccountStatus.PENDING, server_default="PENDING")
    approved_by_id = Column(Integer, ForeignKey("hr_users.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    token_version = Column(Integer, nullable=False, default=0, server_default="0")
```

The `password` column is kept as is; from now on it stores a bcrypt hash.

## 2. `src/models/db/flow_wise/schema/job.py` — ✅ APPLIED

**Why:** a posting must point to a job title from the company's catalog.

Add this column (e.g. just before `created_at`):

```python
    job_title_id = Column(
        Integer,
        ForeignKey("job_titles.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )
```

And this relationship (e.g. just before `requirements = relationship(`):

```python
    job_title = relationship("JobTitle")
```

## 3. `src/models/db/flow_wise/schema/candidate.py` — ✅ APPLIED (existing bug)

**Why:** `Candidate.applications` uses `back_populates="candidate"`, but
`Application` has no `candidate` relationship. Migration `bdf653dcab64` dropped
`applications.candidate_id`, so there is no direct link anymore. SQLAlchemy
raises an error the first time the mappers are configured, which breaks
**every** database query, not only the HR ones. The link now goes through
`cv_files`.

Replace the `applications = relationship(...)` block with:

```python
    # applications are linked through cv_files (applications.cv_file_id)
    applications = relationship(
        "Application",
        secondary="cv_files",
        viewonly=True,
    )
```

## 4. `src/models/db/flow_wise/schema/__init__.py` — ✅ APPLIED

**Why:** Alembic only sees models imported here. Without this line, the next
`alembic revision --autogenerate` would generate a `drop_table("job_titles")`.

Add:

```python
from .job_title import JobTitle
```

## 5. `src/main.py` — ✅ APPLIED

**Why:** FastAPI only serves routers you register. Without this, every
`/api/v1/hr/...` URL returns 404.

```python
from routes import cv_router
from routes.hr_auth_router import hr_auth_router
from routes.hr_admin_router import hr_admin_router
from routes.hr_member_router import hr_member_router

app = FastAPI()

app.include_router(cv_router)
app.include_router(hr_auth_router)
app.include_router(hr_admin_router)
app.include_router(hr_member_router)
```

Optional: if you prefer `from routes import hr_auth_router, ...`, add the three
imports to `routes/__init__.py` instead.

## 6. `src/requirements.txt` — ✅ APPLIED

**Why:** password hashing, JWT and `EmailStr` validation. `bcrypt` is pinned to
4.0.1 because passlib 1.7.4 breaks with bcrypt ≥ 4.1. `email-validator` is
already needed by your existing `schema/` files that use `EmailStr`.

```
passlib[bcrypt]==1.7.4
bcrypt==4.0.1
PyJWT==2.9.0
email-validator==2.2.0
```

## 7. `src/.env` and `src/.env.example` — ✅ `.env.example` APPLIED, `.env` is yours to create

**Why:** JWT signing secret and token lifetime. `helpers/config.py` is not
touched; `helpers/hr_auth_settings.py` reads these keys from the same `.env` file.

```
# HR auth
JWT_SECRET_KEY=change-me-to-a-long-random-string-at-least-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
# set to false after your company + admin accounts exist
ALLOW_ADMIN_REGISTRATION=true
```

Generate a secret with: `python -c "import secrets; print(secrets.token_urlsafe(48))"`

## 8. `src/models/enums/__init__.py` — optional, skipped

Only for convenience (`from models.enums import HRRole`). The new code imports
the enum modules directly, so this is not needed.

```python
from .hr_role_enum import HRRole
from .hr_account_status_enum import HRAccountStatus
```

---

## Then run the migration

```bash
cd src/models/db/flow_wise
alembic upgrade head      # aa7da30d5100 -> c3f1a9e7b2d4
```

Existing `hr_users` rows become `role=MEMBER`, `status=ACTIVE`. Their passwords
are still plain text, so they **cannot log in** (the login treats a non-hash as
wrong). Reset them through `PATCH /api/v1/hr/admin/members/{id}` with a new
`password`, or delete those test rows.

---

## Not required, but worth fixing later (existing code)

| File | Problem |
|---|---|
| `hr_user.py`, `job.py`, `cv_file.py`, `cv_parsed.py`, `job_requirements.py` | ✅ FIXED 2026-11-16: the timestamp defaults were `datetime.now(timezone.utc)` (evaluated once at import, and timezone-aware on a `timestamp without time zone` column, so inserts failed). Now `lambda: datetime.now(timezone.utc).replace(tzinfo=None)`: a fresh UTC time per row, stored without time zone. No migration needed. Moving to `DateTime(timezone=True)` would be a separate migration. |
| `jobs.created_by` | `ON DELETE CASCADE`: deleting an HR user deletes their postings and applications. The HR delete endpoint blocks this (returns 409 and suggests disabling the account instead). |
| `companies.email` | Unique in the model but not in the initial migration. `alembic check` reports it. |
| `schema/hr_user_schema.py` | `HRUserCreate` accepts `company_id` from the client. The new HR endpoints never do this; they take it from the logged-in user. |

---

## Endpoint summary

| Area | Endpoint | Who |
|---|---|---|
| Auth | `POST /api/v1/hr/auth/register-admin` | public (company + admin in one call) |
| | `POST /api/v1/hr/auth/login` (form: `username`=email, `password`) | public |
| | `GET /api/v1/hr/auth/me`, `POST /api/v1/hr/auth/change-password` | any active HR user |
| Company | `GET`, `PATCH /api/v1/hr/admin/company` | Admin |
| Members | `POST`, `GET /api/v1/hr/admin/members` (`?status=&search=`) | Admin |
| | `GET`, `PATCH`, `DELETE /api/v1/hr/admin/members/{id}` | Admin |
| | `POST /api/v1/hr/admin/members/{id}/approve` / `decline` / `disable` | Admin |
| Oversight | `GET /api/v1/hr/admin/postings[/{id}[/applicants]]`, `GET /api/v1/hr/admin/applicants/{id}` | Admin (read-only) |
| Job titles | `POST`, `GET /api/v1/hr/job-titles`, `GET`, `PATCH`, `DELETE /api/v1/hr/job-titles/{id}` | Member |
| Postings | `POST`, `GET /api/v1/hr/postings`, `GET`, `PATCH /api/v1/hr/postings/{id}` | Member |
| | `POST /api/v1/hr/postings/{id}/open` / `close` | Member |
| Applicants | `GET /api/v1/hr/postings/{id}/applicants`, `GET /api/v1/hr/applicants/{id}` | Member |
| | `PATCH /api/v1/hr/applicants/{id}/status` | Member |

### Rules enforced

- **Member account:** `PENDING` → approve → `ACTIVE`. `PENDING` → decline → `DECLINED`.
  `ACTIVE` → disable → `DISABLED`. Approve also re-activates a declined or
  disabled account. Only `ACTIVE` accounts can log in or call the API.
- **Tokens:** every request reloads the user from the DB. Decline, disable,
  password change and admin password reset bump `token_version`, which signs
  out existing tokens immediately.
- **Company isolation:** every query is filtered by the logged-in user's
  company. Another company's IDs return 404 (not 403).
- **Admin vs Member:** strict separation. The Admin manages the company and
  members and can *view* postings and applicants; only Members create titles
  and postings and change applicant status.
- **One admin per company:** enforced by a partial unique index in the DB.
- **Posting:** created as `DRAFT` → open → `PUBLISHED` → close → `CLOSED`
  (it can be opened again). Closed postings cannot be edited.
- **Applicant pipeline:** received → screened → shortlisted → interview →
  offer → hired. Moving forward (skipping steps is allowed) or to `rejected` is
  allowed; going back is not. `hired` and `rejected` are final.
- **Deletes:** a member who created postings cannot be deleted (disable
  instead); a job title used by a posting cannot be deleted.
- **Passwords:** 8–72 characters (the bcrypt limit), at least one letter and
  one number.
