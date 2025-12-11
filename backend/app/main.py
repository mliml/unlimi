from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health, auth, onboarding, sessions, users, admin, emo_scores, therapists, captcha, invitation
# from app.api.routes import protected_example  # Uncomment to enable example protected routes
import logging
logging.basicConfig(
    level=logging.INFO,   # 注意这里是 INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

print(">>> FastAPI app loaded")   # 控制台一定显示
logging.info(">>> Logging system initialized")

app = FastAPI(title="AI Therapy Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/api")
app.include_router(captcha.router, prefix="/api")
app.include_router(invitation.router, prefix="/api")
app.include_router(onboarding.router, prefix="/api/onboarding", tags=["onboarding"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(therapists.router, prefix="/api", tags=["therapists"])
app.include_router(sessions.router, prefix="/api", tags=["sessions"])
app.include_router(admin.router, prefix="/api", tags=["admin"])
app.include_router(emo_scores.router, prefix="/api", tags=["emo-score"])
# app.include_router(protected_example.router, prefix="/api")  # Uncomment to enable example


def get_app() -> FastAPI:
    return app
