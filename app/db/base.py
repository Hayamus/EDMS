from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Импортируем все модели, чтобы они зарегистрировались в реестре Base
from app.users.models import User                              # noqa: E402, F401
from app.documents.models.document import Document              # noqa: E402, F401
from app.documents.models.acknowledgement import DocumentAcknowledgement  # noqa: E402, F401
from app.documents.models.version import DocumentVersion        # noqa: E402, F401
from app.comments.models import Comment                         # noqa: E402, F401
from app.auth.models import RefreshToken                        # noqa: E402, F401
from app.approvals.models import Approval                       # noqa: E402, F401
from app.notifications.models import Notification               # noqa: E402, F401
from app.audit.models import AuditLog                            # noqa: E402, F401
from app.teams.models.team import Team                  # noqa: E402, F401
from app.teams.models.team_member import TeamMember     # noqa: E402, F401