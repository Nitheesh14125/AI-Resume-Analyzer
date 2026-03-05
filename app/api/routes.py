from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database.db_connection import get_db
from app.services.nlp_processor import preprocess_text
from app.services.resume_parser import extract_resume_text, save_upload_file
from app.services.resume_validator import validate_resume_document
from app.services.role_graph_service import get_supported_role_names
from app.services.scoring_engine import calculate_best_role_score, calculate_resume_score
from app.services.skill_extractor import extract_skills_from_resume

router = APIRouter(prefix="/api", tags=["Resume Analyzer"])
public_router = APIRouter(tags=["Resume Analyzer"])


@router.post("/resumes/upload")
def upload_resume(file: UploadFile = File(...)):
    try:
        saved_file_path = save_upload_file(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "message": "Resume uploaded successfully.",
        "stored_filename": saved_file_path.name,
        "file_path": str(saved_file_path),
    }


@router.post("/resumes/analyze")
def analyze_resume_for_role(
    role_name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        saved_file_path = save_upload_file(file)
        resume_text = extract_resume_text(saved_file_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text could not be extracted.")

    validation_result = validate_resume_document(resume_text)
    if not validation_result.is_valid:
        raise HTTPException(
            status_code=422,
            detail={
                "message": validation_result.message,
                "resume_confidence_score": validation_result.confidence_score,
                "detected_sections": validation_result.detected_sections,
                "missing_sections": validation_result.missing_sections,
            },
        )

    processed_text = preprocess_text(resume_text)
    extracted_skills = extract_skills_from_resume(
        token_set=processed_text["token_set"],
        normalized_resume_text=processed_text["normalized_text"],
        db=db,
    )

    try:
        score_result = calculate_resume_score(role_name=role_name, resume_skills=extracted_skills, db=db)
    except ValueError as exc:
        detail = str(exc)
        status_code = 404 if "not found" in detail.lower() else 400
        raise HTTPException(status_code=status_code, detail=detail) from exc

    return {
        "stored_filename": saved_file_path.name,
        "analysis_mode": "validate_role",
        "resume_confidence_score": validation_result.confidence_score,
        "detected_resume_sections": validation_result.detected_sections,
        "role_name": score_result["role_name"],
        "resume_score": score_result["resume_score"],
        "matched_skills": score_result["matched_skills"],
        "missing_skills": score_result["missing_skills"],
        "suggestion": score_result["suggestion"],
        "suggestions": score_result.get("suggestions", []),
        "learning_paths": score_result.get("learning_paths", []),
        "recommended_courses": score_result.get("recommended_courses", []),
        "group_breakdown": score_result.get("group_breakdown", []),
        "detected_resume_skills": score_result["detected_resume_skills"],
        "required_role_skills": score_result["required_role_skills"],
    }


@public_router.post("/analyze-resume")
@router.post("/analyze-resume")
def analyze_resume(
    file: UploadFile = File(...),
    role_name: str | None = Form(default=None),
    analysis_mode: str = Form(default="validate_role"),
    db: Session = Depends(get_db),
):
    try:
        saved_file_path = save_upload_file(file)
        resume_text = extract_resume_text(saved_file_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text could not be extracted.")

    validation_result = validate_resume_document(resume_text)
    if not validation_result.is_valid:
        raise HTTPException(
            status_code=422,
            detail={
                "message": validation_result.message,
                "resume_confidence_score": validation_result.confidence_score,
                "detected_sections": validation_result.detected_sections,
                "missing_sections": validation_result.missing_sections,
            },
        )

    processed_text = preprocess_text(resume_text)
    extracted_skills = extract_skills_from_resume(
        token_set=processed_text["token_set"],
        normalized_resume_text=processed_text["normalized_text"],
        db=db,
    )

    try:
        normalized_mode = analysis_mode.strip().lower()
        if normalized_mode == "validate_role":
            if not role_name:
                raise ValueError("role_name is required when analysis_mode is 'validate_role'.")
            score_result = calculate_resume_score(role_name=role_name, resume_skills=extracted_skills, db=db)
        elif normalized_mode == "discover_roles":
            score_result = calculate_best_role_score(resume_skills=extracted_skills, db=db, resume_text=resume_text)
        else:
            raise ValueError("analysis_mode must be either 'validate_role' or 'discover_roles'.")
    except ValueError as exc:
        detail = str(exc)
        status_code = 404 if "not found" in detail.lower() else 400
        raise HTTPException(status_code=status_code, detail=detail) from exc

    suggestions = score_result.get("suggestions", [])
    if not suggestions and score_result.get("suggestion"):
        suggestions = [str(score_result["suggestion"])]

    return {
        "analysis_mode": analysis_mode,
        "resume_confidence_score": validation_result.confidence_score,
        "detected_resume_sections": validation_result.detected_sections,
        "resume_score": score_result["resume_score"],
        "predicted_role": score_result["role_name"],
        "matched_skills": score_result["matched_skills"],
        "missing_skills": score_result["missing_skills"],
        "suggestions": suggestions,
        "learning_paths": score_result.get("learning_paths", []),
        "recommended_courses": score_result.get("recommended_courses", []),
        "top_role_insights": score_result.get("top_role_insights", []),
        "role_scores": score_result.get("role_scores", []),
        "profile_experience_years": score_result.get("profile_experience_years", 0),
    }


@public_router.get("/roles")
@router.get("/roles")
def list_supported_roles():
    return {"roles": get_supported_role_names()}
