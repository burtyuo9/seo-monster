"""
AWS SES API Routes - API для управления рассылками
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil

router = APIRouter(prefix="/api/ses", tags=["AWS SES"])

# Import services
from services.aws_ses_service import ses_service
from services.email_content_generator import email_generator
from services.recipient_manager import recipient_manager


class AddKeyRequest(BaseModel):
    access_key_id: str
    secret_access_key: str
    region: str = "us-east-1"
    name: str = ""

class GenerateContentRequest(BaseModel):
    task: str
    format_type: str = "html"
    language: str = "ru"
    tone: str = "professional"

class ManualContentRequest(BaseModel):
    name: str
    subject: str
    html_body: str = ""
    text_body: str = ""
    preheader: str = ""
    format_type: str = "html"

class ManualListRequest(BaseModel):
    name: str
    emails: List[str]
    description: str = ""


# === AWS Keys ===

@router.get("/keys")
async def get_all_keys():
    return {"keys": ses_service.get_all_keys()}

@router.post("/keys")
async def add_key(request: AddKeyRequest):
    result = await ses_service.add_aws_key(
        request.access_key_id, request.secret_access_key,
        request.region, request.name
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.get("/keys/{key_id}")
async def get_key_info(key_id: str):
    info = ses_service.get_key_info(key_id)
    if not info:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": info}

@router.post("/keys/{key_id}/refresh")
async def refresh_key(key_id: str):
    result = await ses_service.refresh_key_info(key_id)
    return result

@router.delete("/keys/{key_id}")
async def delete_key(key_id: str):
    if ses_service.delete_key(key_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Key not found")

@router.get("/regions")
async def get_regions():
    return {"regions": ses_service.get_available_regions()}


# === Email Content ===

@router.get("/content")
async def get_all_content():
    return {"contents": email_generator.get_all_contents()}

@router.post("/content/generate")
async def generate_content(request: GenerateContentRequest):
    result = await email_generator.generate_content_ai(
        request.task, request.format_type,
        request.language, request.tone
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.post("/content/manual")
async def create_content_manual(request: ManualContentRequest):
    result = email_generator.create_content_manual(
        request.name, request.subject, request.html_body,
        request.text_body, request.preheader, request.format_type
    )
    return result

@router.post("/content/upload")
async def upload_content(file: UploadFile = File(...), name: str = Form(...)):
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    result = email_generator.upload_html_file(temp_path, name)
    os.remove(temp_path)
    return result

@router.get("/content/{content_id}")
async def get_content(content_id: str):
    content = email_generator.get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return {"content": content}

@router.delete("/content/{content_id}")
async def delete_content(content_id: str):
    if email_generator.delete_content(content_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Content not found")

@router.get("/templates")
async def get_templates():
    return {"templates": email_generator.get_builtin_templates()}


# === Recipient Lists ===

@router.get("/lists")
async def get_all_lists():
    return {"lists": recipient_manager.get_all_lists()}

@router.post("/lists/upload")
async def upload_list(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(""),
    email_column: str = Form("email"),
    delimiter: str = Form(",")
):
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    result = recipient_manager.upload_list(temp_path, name, description, email_column, delimiter)
    os.remove(temp_path)
    return result

@router.post("/lists/manual")
async def create_list_manual(request: ManualListRequest):
    result = recipient_manager.create_list_manual(request.name, request.emails, request.description)
    return result

@router.get("/lists/{list_id}")
async def get_list(list_id: str):
    lst = recipient_manager.get_list(list_id)
    if not lst:
        raise HTTPException(status_code=404, detail="List not found")
    return {"list": lst}

@router.get("/lists/{list_id}/recipients")
async def get_recipients(list_id: str, limit: int = 100, offset: int = 0):
    result = recipient_manager.get_recipients(list_id, limit, offset)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.delete("/lists/{list_id}")
async def delete_list(list_id: str):
    if recipient_manager.delete_list(list_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="List not found")

@router.get("/lists/stats")
async def get_lists_stats():
    return {"stats": recipient_manager.get_stats()}


# === Stats ===

@router.get("/stats")
async def get_ses_stats():
    return {
        "keys_count": len(ses_service.get_all_keys()),
        "contents_count": len(email_generator.get_all_contents()),
        "lists_count": len(recipient_manager.get_all_lists()),
        "total_recipients": sum(l.get("valid_count", 0) for l in recipient_manager.get_all_lists())
    }



# === A/B Testing ===

from services.email_ab_testing import ab_testing_service


class CreateABTestRequest(BaseModel):
    name: str
    campaign_id: str
    variants: List[dict]
    optimization_metric: str = "open_rate"
    test_size_percent: float = 20.0
    auto_select_winner: bool = True
    min_sample_size: int = 100
    confidence_level: float = 95.0
    max_test_duration_hours: int = 24
    description: str = ""


class RecordSendRequest(BaseModel):
    variant_id: str
    count: int = 1


class TrackConversionRequest(BaseModel):
    variant_id: str
    recipient_email: str


@router.get("/ab-tests")
async def get_all_ab_tests():
    """Получение всех A/B тестов"""
    tests = await ab_testing_service.get_all_tests()
    return {"tests": tests}


@router.post("/ab-tests")
async def create_ab_test(request: CreateABTestRequest):
    """Создание нового A/B теста"""
    test = await ab_testing_service.create_test(
        name=request.name,
        campaign_id=request.campaign_id,
        variants_config=request.variants,
        optimization_metric=request.optimization_metric,
        test_size_percent=request.test_size_percent,
        auto_select_winner=request.auto_select_winner,
        min_sample_size=request.min_sample_size,
        confidence_level=request.confidence_level,
        max_test_duration_hours=request.max_test_duration_hours,
        description=request.description
    )
    return {"success": True, "test": test.to_dict()}


@router.get("/ab-tests/stats")
async def get_ab_tests_stats():
    """Получение статистики A/B тестов"""
    stats = await ab_testing_service.get_stats()
    return {"stats": stats}


@router.get("/ab-tests/{test_id}")
async def get_ab_test(test_id: str):
    """Получение информации о тесте"""
    test = await ab_testing_service.get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return {"test": test}


@router.get("/ab-tests/{test_id}/results")
async def get_ab_test_results(test_id: str):
    """Получение результатов теста с аналитикой"""
    results = await ab_testing_service.get_test_results(test_id)
    if "error" in results:
        raise HTTPException(status_code=404, detail=results["error"])
    return results


@router.post("/ab-tests/{test_id}/start")
async def start_ab_test(test_id: str):
    """Запуск A/B теста"""
    result = await ab_testing_service.start_test(test_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/ab-tests/{test_id}/pause")
async def pause_ab_test(test_id: str):
    """Приостановка теста"""
    result = await ab_testing_service.pause_test(test_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/ab-tests/{test_id}/complete")
async def complete_ab_test(test_id: str, winner_variant_id: Optional[str] = None):
    """Завершение теста и выбор победителя"""
    result = await ab_testing_service.complete_test(test_id, winner_variant_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/ab-tests/{test_id}/record-send")
async def record_ab_test_send(test_id: str, request: RecordSendRequest):
    """Регистрация отправки писем для варианта"""
    success = await ab_testing_service.record_send(test_id, request.variant_id, request.count)
    return {"success": success}


@router.post("/ab-tests/{test_id}/track-conversion")
async def track_ab_test_conversion(test_id: str, request: TrackConversionRequest):
    """Регистрация конверсии"""
    success = await ab_testing_service.track_conversion(test_id, request.variant_id, request.recipient_email)
    return {"success": success}


@router.delete("/ab-tests/{test_id}")
async def delete_ab_test(test_id: str):
    """Удаление теста"""
    success = await ab_testing_service.delete_test(test_id)
    if not success:
        raise HTTPException(status_code=404, detail="Test not found")
    return {"success": True}


# === Tracking Endpoints ===

@router.get("/track/open/{pixel_id}")
async def track_email_open(pixel_id: str):
    """Отслеживание открытия письма (tracking pixel)"""
    await ab_testing_service.track_open(pixel_id)
    # Возвращаем прозрачный 1x1 пиксель
    from fastapi.responses import Response
    transparent_pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    return Response(content=transparent_pixel, media_type="image/gif")


@router.get("/track/click/{click_id}")
async def track_email_click(click_id: str):
    """Отслеживание клика и редирект на оригинальный URL"""
    from fastapi.responses import RedirectResponse
    original_url = await ab_testing_service.track_click(click_id)
    if original_url:
        return RedirectResponse(url=original_url)
    raise HTTPException(status_code=404, detail="Link not found")


@router.post("/ab-tests/{test_id}/generate-tracking")
async def generate_tracking_codes(test_id: str, variant_id: str, recipient_email: str, urls: List[str] = []):
    """Генерация tracking кодов для письма"""
    pixel_id = ab_testing_service.generate_tracking_pixel(test_id, variant_id, recipient_email)
    
    click_ids = {}
    for url in urls:
        click_id = ab_testing_service.generate_click_tracking_url(test_id, variant_id, recipient_email, url)
        click_ids[url] = click_id
    
    return {
        "pixel_id": pixel_id,
        "pixel_url": f"/api/ses/track/open/{pixel_id}",
        "click_tracking": {url: f"/api/ses/track/click/{cid}" for url, cid in click_ids.items()}
    }


# === Warm-up Plans ===

from services.ses_warmup import warmup_manager, WarmupStatus

class CreateWarmupRequest(BaseModel):
    key_id: str
    name: str
    strategy: str = "moderate"
    target_volume: int = 10000
    auto_mode: bool = True
    send_hour: int = 10
    send_minute: int = 0
    recipient_list_id: str = ""
    content_id: str = ""
    from_email: str = ""
    from_name: str = ""

class UpdateWarmupRequest(BaseModel):
    auto_mode: Optional[bool] = None
    send_hour: Optional[int] = None
    send_minute: Optional[int] = None
    recipient_list_id: Optional[str] = None
    content_id: Optional[str] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    max_bounce_rate: Optional[float] = None
    max_complaint_rate: Optional[float] = None
    auto_pause_on_issues: Optional[bool] = None
    name: Optional[str] = None

class RecordDayStatsRequest(BaseModel):
    day: int
    sent: int
    delivered: int
    bounced: int
    complaints: int
    opens: int = 0
    clicks: int = 0

@router.get("/warmup/stats")
async def get_warmup_stats():
    return warmup_manager.get_stats()

@router.get("/warmup/plans")
async def get_all_warmup_plans():
    plans = warmup_manager.get_all_plans()
    return {"plans": [p.to_dict() for p in plans]}

@router.get("/warmup/plans/{plan_id}")
async def get_warmup_plan(plan_id: str):
    plan = warmup_manager.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan.to_dict()

@router.get("/warmup/plans/key/{key_id}")
async def get_warmup_plans_by_key(key_id: str):
    plans = warmup_manager.get_plans_by_key(key_id)
    return {"plans": [p.to_dict() for p in plans]}

@router.post("/warmup/plans")
async def create_warmup_plan(request: CreateWarmupRequest):
    plan = warmup_manager.create_plan(
        key_id=request.key_id,
        name=request.name,
        strategy=request.strategy,
        target_volume=request.target_volume,
        auto_mode=request.auto_mode,
        send_hour=request.send_hour,
        send_minute=request.send_minute,
        recipient_list_id=request.recipient_list_id,
        content_id=request.content_id,
        from_email=request.from_email,
        from_name=request.from_name
    )
    return {"success": True, "plan": plan.to_dict()}

@router.put("/warmup/plans/{plan_id}")
async def update_warmup_plan(plan_id: str, request: UpdateWarmupRequest):
    update_data = {k: v for k, v in request.dict().items() if v is not None}
    plan = warmup_manager.update_plan_settings(plan_id, **update_data)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"success": True, "plan": plan.to_dict()}

@router.post("/warmup/plans/{plan_id}/start")
async def start_warmup_plan(plan_id: str):
    plan = warmup_manager.start_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"success": True, "plan": plan.to_dict()}

class PauseWarmupRequest(BaseModel):
    reason: str = ""

@router.post("/warmup/plans/{plan_id}/pause")
async def pause_warmup_plan(plan_id: str, request: PauseWarmupRequest = None):
    reason = request.reason if request else ""
    plan = warmup_manager.pause_plan(plan_id, reason)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"success": True, "plan": plan.to_dict()}

@router.post("/warmup/plans/{plan_id}/resume")
async def resume_warmup_plan(plan_id: str):
    plan = warmup_manager.resume_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"success": True, "plan": plan.to_dict()}

@router.post("/warmup/plans/{plan_id}/record")
async def record_warmup_day_stats(plan_id: str, request: RecordDayStatsRequest):
    plan = warmup_manager.record_day_stats(
        plan_id=plan_id,
        day=request.day,
        sent=request.sent,
        delivered=request.delivered,
        bounced=request.bounced,
        complaints=request.complaints,
        opens=request.opens,
        clicks=request.clicks
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"success": True, "plan": plan.to_dict()}

@router.get("/warmup/plans/{plan_id}/today-volume")
async def get_today_warmup_volume(plan_id: str):
    volume = warmup_manager.get_today_volume(plan_id)
    return {"volume": volume}

@router.get("/warmup/plans/{plan_id}/recommendations")
async def get_warmup_recommendations(plan_id: str):
    recommendations = warmup_manager.get_recommendations(plan_id)
    return {"recommendations": recommendations}

@router.delete("/warmup/plans/{plan_id}")
async def delete_warmup_plan(plan_id: str):
    success = warmup_manager.delete_plan(plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"success": True}

@router.get("/warmup/plans/{plan_id}/timeline")
async def get_warmup_timeline(plan_id: str):
    """Get timeline data for visualization"""
    timeline = warmup_manager.get_plan_timeline(plan_id)
    if not timeline:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"timeline": timeline}

@router.post("/warmup/plans/{plan_id}/execute")
async def execute_warmup_send(plan_id: str):
    """Manually trigger warmup email sending"""
    result = await warmup_manager.execute_warmup_send(plan_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.get("/warmup/active")
async def get_active_warmup_plans():
    """Get all active warmup plans"""
    plans = warmup_manager.get_active_plans()
    return {"plans": [p.to_dict() for p in plans]}

@router.post("/warmup/scheduler/start")
async def start_warmup_scheduler():
    """Start the automatic warmup scheduler"""
    warmup_manager.start_scheduler()
    return {"success": True, "message": "Scheduler started"}

@router.post("/warmup/scheduler/stop")
async def stop_warmup_scheduler():
    """Stop the automatic warmup scheduler"""
    warmup_manager.stop_scheduler()
    return {"success": True, "message": "Scheduler stopped"}

# === Warmup Executor ===

from services.warmup_executor import warmup_executor

@router.post("/warmup/execute/{plan_id}")
async def execute_warmup_now(plan_id: str):
    """Manually execute warmup for a plan"""
    result = await warmup_executor.execute_warmup_for_plan(plan_id)
    return result

@router.get("/warmup/executor/status")
async def get_executor_status():
    """Get warmup executor status"""
    return warmup_executor.get_scheduler_status()

@router.post("/warmup/executor/start")
async def start_executor():
    """Start the warmup executor scheduler"""
    return warmup_executor.start_scheduler()

@router.post("/warmup/executor/stop")
async def stop_executor():
    """Stop the warmup executor scheduler"""
    return warmup_executor.stop_scheduler()

@router.get("/warmup/executor/log")
async def get_executor_log(plan_id: Optional[str] = None, limit: int = 100):
    """Get execution log"""
    return {"log": warmup_executor.get_execution_log(plan_id, limit)}

@router.post("/warmup/simulate/{plan_id}")
async def simulate_warmup_day(plan_id: str):
    """Simulate a warmup day for testing"""
    plan = warmup_manager.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    result = await warmup_executor._simulate_sending(plan, warmup_manager.get_today_volume(plan_id))
    return result

@router.get("/warmup/strategies")
async def get_warmup_strategies():
    return {
        "strategies": [
            {
                "id": "conservative",
                "name": "Conservative",
                "description": "Slow and safe warmup over 21 days. Best for new domains.",
                "days": 21,
                "risk": "low"
            },
            {
                "id": "moderate",
                "name": "Moderate",
                "description": "Balanced warmup over 14 days. Good for most cases.",
                "days": 14,
                "risk": "medium"
            },
            {
                "id": "aggressive",
                "name": "Aggressive",
                "description": "Fast warmup over 7 days. Higher risk of deliverability issues.",
                "days": 7,
                "risk": "high"
            }
        ]
    }
