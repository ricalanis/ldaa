from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, TypedDict, Optional

class DocumentSegment(BaseModel):
    """A segment of a legal document."""
    id: str
    text: str
    document_id: str
    segment_type: Literal["paragraph", "article", "section"]
    position: int
    reasoning: Optional[str] = None  # A short explanation of the reasoning for the chosen segment_type

class SegmentAnalysis(BaseModel):
    """Analysis of a single document segment."""
    segment: str  # The text of the paragraph or section being analyzed
    segment_id: str
    summary: str
    category: str
    segment_type: Optional[str] = None  # A structured definition of the unit of analysis (e.g., paragraph, article, section)
    pros: List[str] = Field(..., min_items=1)
    cons: List[str] = Field(..., min_items=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    meta: Dict[str, Any] = {}
    success: bool = True

class DocumentComparison(BaseModel):
    similarities: List[Dict[str, str]]  # Each item has 'topic' and 'explanation'
    differences: List[Dict[str, str]]   # Each item has 'topic' and 'explanation'
    focus_areas: Dict[str, List[str]]   # {'doc1': [...], 'doc2': [...]}
    gaps: List[str]
    meta: Dict[str, Any] = {}
    verbose_comparison: Optional[str]
    comparative_summary: Optional[str]
    confidence: Optional[float]
    reasoning: Optional[str]
    success: Optional[bool]

class SummaryOutput(BaseModel):
    summary: str

class CategoryOutput(BaseModel):
    category: str

class SegmentAction(BaseModel):
    segment_index: int
    action: str
    confidence: float
    reasoning: str
    success: bool = True
    # Add other fields as needed

class ComparisonAction(BaseModel):
    action: str
    confidence: float
    reasoning: str
    success: bool = True
    # Add other fields as needed

class LegalAnalysisState(BaseModel):
    doc1_path: Optional[str] = None
    doc2_path: Optional[str] = None
    doc1_text: Optional[str] = None
    doc2_text: Optional[str] = None
    doc1_segments: List[DocumentSegment] = Field(default_factory=list)
    doc2_segments: List[DocumentSegment] = Field(default_factory=list)
    doc1_analysis: List[SegmentAnalysis] = Field(default_factory=list)
    doc2_analysis: List[SegmentAnalysis] = Field(default_factory=list)
    doc1_segment_actions: List[SegmentAction] = Field(default_factory=list)
    doc2_segment_actions: List[SegmentAction] = Field(default_factory=list)
    doc1_accepted_segments: List[SegmentAnalysis] = Field(default_factory=list)
    doc2_accepted_segments: List[SegmentAnalysis] = Field(default_factory=list)
    comparison_result: Optional[DocumentComparison] = None
    comparison_action: Optional[ComparisonAction] = None
    output_path: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    vector_db_path: Optional[str] = None
    vector_store_output: Optional[dict] = None  # Add this for vector output summary
    # Meta-logs and other fields can be added as needed
    # e.g., meta_log_ingest, meta_log_segmentation, ...