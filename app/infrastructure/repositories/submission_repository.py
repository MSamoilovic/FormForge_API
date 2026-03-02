from typing import Dict, Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.submission_schema import SubmissionCreate
from app.application.interfaces.submission_repository import ISubmissionRepository
from app.domain.models.submission import Submission


class SubmissionRepository(ISubmissionRepository):
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def create(self, form_id: int, submission_data: SubmissionCreate) -> Submission:
        db_submission = Submission(
            form_id=form_id,
            data=submission_data.data
        )
        self.session.add(db_submission)
        await self.session.commit()
        await self.session.refresh(db_submission)
        return db_submission

    async def get_all_by_form_id(self, form_id: int, filters: Dict[str, Any] = None) -> List[type[Submission]]:
        query = select(Submission).filter(Submission.form_id == form_id)

        if filters:
            for key, value in filters.items():
                if value:
                    query = query.filter(Submission.data[key].astext().ilike(f"%{value}%"))

        query = query.order_by(Submission.submitted_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, submission_id: int) -> Optional[Submission]:
        pass

    async def update(self, submission_id: int, submission_data: SubmissionCreate) -> Optional[Submission]:
        pass

    async def delete(self, submission_id: int) -> Optional[Submission]:
        pass
