"""Integrations API endpoints."""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.base import Integration
from app.schemas.integration import IntegrationCreate, IntegrationResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=list[IntegrationResponse])
async def list_integrations(db: Session = Depends(get_db)):
    """List all integrations."""
    try:
        integrations = db.query(Integration).all()
        return [
            IntegrationResponse(
                id=i.id,
                name=i.name,
                description=i.description or "",
                hooks=i.hooks,
                config=i.config,
                enabled=i.enabled == "true",
            )
            for i in integrations
        ]
    except Exception as e:
        logger.error(f"Failed to list integrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=IntegrationResponse)
async def create_integration(request: IntegrationCreate, db: Session = Depends(get_db)):
    """Create a new integration."""
    try:
        # Check if integration with same name exists
        existing = db.query(Integration).filter_by(name=request.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Integration with this name already exists")
        
        integration = Integration(
            name=request.name,
            description=request.description,
            hooks=request.hooks,
            config=request.config,
            enabled="true",
        )
        
        db.add(integration)
        db.commit()
        db.refresh(integration)
        
        return IntegrationResponse(
            id=integration.id,
            name=integration.name,
            description=integration.description or "",
            hooks=integration.hooks,
            config=integration.config,
            enabled=True,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{integration_id}")
async def delete_integration(integration_id: int, db: Session = Depends(get_db)):
    """Delete an integration."""
    try:
        integration = db.query(Integration).filter_by(id=integration_id).first()
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        db.delete(integration)
        db.commit()
        
        return {"message": "Integration deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))
