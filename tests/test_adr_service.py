"""Tests for ADR service."""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.database import Base
from app.models.adr import ADR, ADRStatus
from app.services.adr_service import ADRService


@pytest.fixture
async def db_session():
    """Create a test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        yield session
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_adr(db_session):
    """Test creating an ADR."""
    adr = await ADRService.create_adr(
        db_session,
        title="Test ADR",
        context="Test context",
        decision="Test decision",
        consequences="Test consequences"
    )
    
    assert adr.id is not None
    assert adr.number == 1
    assert adr.title == "Test ADR"
    assert adr.status == ADRStatus.DRAFT


@pytest.mark.asyncio
async def test_get_adr(db_session):
    """Test getting an ADR."""
    # Create an ADR
    adr = await ADRService.create_adr(
        db_session,
        title="Test ADR",
        context="Test context",
        decision="Test decision"
    )
    await db_session.commit()
    
    # Get the ADR
    retrieved_adr = await ADRService.get_adr(db_session, adr.id)
    
    assert retrieved_adr is not None
    assert retrieved_adr.id == adr.id
    assert retrieved_adr.title == "Test ADR"


@pytest.mark.asyncio
async def test_list_adrs(db_session):
    """Test listing ADRs."""
    # Create multiple ADRs
    for i in range(3):
        await ADRService.create_adr(
            db_session,
            title=f"Test ADR {i+1}",
            context="Test context",
            decision="Test decision"
        )
    await db_session.commit()
    
    # List ADRs
    adrs = await ADRService.list_adrs(db_session)
    
    assert len(adrs) == 3


@pytest.mark.asyncio
async def test_update_adr(db_session):
    """Test updating an ADR."""
    # Create an ADR
    adr = await ADRService.create_adr(
        db_session,
        title="Original Title",
        context="Original context",
        decision="Original decision"
    )
    await db_session.commit()
    
    # Update the ADR
    updated_adr = await ADRService.update_adr(
        db_session,
        adr.id,
        title="Updated Title",
        status=ADRStatus.ACCEPTED
    )
    await db_session.commit()
    
    assert updated_adr.title == "Updated Title"
    assert updated_adr.status == ADRStatus.ACCEPTED


@pytest.mark.asyncio
async def test_delete_adr(db_session):
    """Test deleting an ADR."""
    # Create an ADR
    adr = await ADRService.create_adr(
        db_session,
        title="Test ADR",
        context="Test context",
        decision="Test decision"
    )
    await db_session.commit()
    
    # Delete the ADR
    success = await ADRService.delete_adr(db_session, adr.id)
    await db_session.commit()
    
    assert success is True
    
    # Verify it's deleted
    deleted_adr = await ADRService.get_adr(db_session, adr.id)
    assert deleted_adr is None


@pytest.mark.asyncio
async def test_format_as_madr(db_session):
    """Test formatting ADR as MADR."""
    adr = await ADRService.create_adr(
        db_session,
        title="Test ADR",
        context="This is the context",
        decision="This is the decision",
        consequences="These are consequences"
    )
    
    markdown = ADRService.format_as_madr(adr)
    
    assert "# 1. Test ADR" in markdown
    assert "## Status" in markdown
    assert "## Context" in markdown
    assert "## Decision" in markdown
    assert "## Consequences" in markdown
