from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Iterable

from .apl253_catalog import APL253_RECORDS, APL253_RELATION_SOURCE, APL253_SOURCE_COMMIT, APL253_SOURCE_LOCATOR
from .domain import SpatialScope


class SourceClass(str, Enum):
    LEGAL_REGULATORY = "LEGAL_REGULATORY"
    OFFICIAL_TECHNICAL = "OFFICIAL_TECHNICAL"
    PROFESSIONAL_GUIDANCE = "PROFESSIONAL_GUIDANCE"
    EMPIRICAL_RESEARCH = "EMPIRICAL_RESEARCH"
    THEORETICAL = "THEORETICAL"
    HEURISTIC = "HEURISTIC"
    PRECEDENT = "PRECEDENT"
    USER_PROVIDED = "USER_PROVIDED"
    SITE_OBSERVATION = "SITE_OBSERVATION"


class ReviewStatus(str, Enum):
    REGISTERED = "REGISTERED"
    BIBLIOGRAPHICALLY_VERIFIED = "BIBLIOGRAPHICALLY_VERIFIED"
    EXTRACTED = "EXTRACTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    DEPRECATED = "DEPRECATED"
    REJECTED = "REJECTED"


class LicenseStatus(str, Enum):
    PUBLIC_DOMAIN = "PUBLIC_DOMAIN"
    OPEN_LICENSE = "OPEN_LICENSE"
    LICENSE_REVIEW_REQUIRED = "LICENSE_REVIEW_REQUIRED"
    USER_AUTHORIZED = "USER_AUTHORIZED"
    NO_REPRODUCTION = "NO_REPRODUCTION"
    UNKNOWN = "UNKNOWN"


class KnowledgeItemType(str, Enum):
    DESIGN_PRINCIPLE = "DESIGN_PRINCIPLE"
    PATTERN_REFERENCE = "PATTERN_REFERENCE"
    HEURISTIC = "HEURISTIC"
    METHOD = "METHOD"
    TYPOLOGY = "TYPOLOGY"
    DIMENSIONAL_GUIDANCE = "DIMENSIONAL_GUIDANCE"
    SPATIAL_RELATION = "SPATIAL_RELATION"
    EVALUATION_CRITERION = "EVALUATION_CRITERION"
    PRECEDENT = "PRECEDENT"
    REGULATORY_RULE = "REGULATORY_RULE"
    EMPIRICAL_FINDING = "EMPIRICAL_FINDING"
    DESIGN_QUESTION = "DESIGN_QUESTION"


class AuthorityLevel(str, Enum):
    LEGAL = "LEGAL"
    OFFICIAL_TECHNICAL = "OFFICIAL_TECHNICAL"
    EMPIRICAL = "EMPIRICAL"
    PROFESSIONAL_GUIDANCE = "PROFESSIONAL_GUIDANCE"
    THEORETICAL = "THEORETICAL"
    HEURISTIC = "HEURISTIC"
    EXPERIENTIAL = "EXPERIENTIAL"
    USER_PREFERENCE = "USER_PREFERENCE"


class AgentStatus(str, Enum):
    READY = "READY"
    INSUFFICIENT_CONTEXT = "INSUFFICIENT_CONTEXT"
    RETRIEVING = "RETRIEVING"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    CONFLICTING = "CONFLICTING"
    RESPONDED = "RESPONDED"


@dataclass(frozen=True)
class DesignKnowledgeSource:
    source_id: str
    title: str
    authors: list[str]
    source_class: SourceClass
    source_type: str
    language: str
    publication_year: int | None = None
    publisher_or_authority: str | None = None
    jurisdiction: str | None = None
    edition_or_version: str | None = None
    isbn_or_legal_id: str | None = None
    url: str | None = None
    license_status: LicenseStatus = LicenseStatus.UNKNOWN
    rights_evidence: str = "Metadata verified from publisher, library, or archive record; no ingestion permission established."
    processing_permission_status: str = "NOT_REQUIRED_METADATA_ONLY"
    bibliographic_reference: str = ""
    content_hash: str | None = None
    review_status: ReviewStatus = ReviewStatus.REGISTERED
    version: int = 1

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.title.strip() or not self.authors:
            raise ValueError("source_id, title and authors are required")


@dataclass(frozen=True)
class DesignKnowledgeItem:
    knowledge_item_id: str
    source_id: str
    item_type: KnowledgeItemType
    title: str
    statement: str
    epistemic_status: str
    authority_level: AuthorityLevel
    applicable_scales: list[SpatialScope]
    excluded_scales: list[SpatialScope] = field(default_factory=list)
    applicable_typologies: list[str] = field(default_factory=list)
    jurisdictions: list[str] = field(default_factory=list)
    conditions: dict[str, Any] = field(default_factory=dict)
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    criteria: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    citation_locator: str | None = None
    review_status: ReviewStatus = ReviewStatus.UNDER_REVIEW
    limitations: list[str] = field(default_factory=list)
    related_item_ids: list[str] = field(default_factory=list)
    version: int = 1

    def __post_init__(self) -> None:
        if not self.knowledge_item_id.strip() or not self.source_id.strip() or not self.statement.strip():
            raise ValueError("knowledge_item_id, source_id and statement are required")
        if not self.applicable_scales:
            raise ValueError("at least one applicable scale is required")
        if set(self.applicable_scales) & set(self.excluded_scales):
            raise ValueError("a scale cannot be both applicable and excluded")


@dataclass(frozen=True)
class DesignPattern:
    pattern_id: str
    source_ids: list[str]
    name: str
    problem: dict[str, Any]
    context: list[str]
    forces: list[str]
    solution_family: dict[str, Any]
    consequences: dict[str, Any]
    applicable_scales: list[SpatialScope]
    applicable_typologies: list[str] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    positive_indicators: list[str] = field(default_factory=list)
    negative_indicators: list[str] = field(default_factory=list)
    regulatory_dependencies: list[str] = field(default_factory=list)
    review_status: ReviewStatus = ReviewStatus.UNDER_REVIEW
    version: int = 1

    def __post_init__(self) -> None:
        if not self.pattern_id.strip() or not self.name.strip() or not self.source_ids:
            raise ValueError("pattern_id, name and source_ids are required")
        if not self.applicable_scales:
            raise ValueError("at least one applicable scale is required")


@dataclass(frozen=True)
class DesignKnowledgeQuery:
    spatial_scope: SpatialScope | None = None
    typology: str | None = None
    jurisdiction: str | None = None
    objectives: list[str] = field(default_factory=list)
    problem_terms: list[str] = field(default_factory=list)
    requested_operation: str = "KNOWLEDGE_RETRIEVAL"
    facts: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    preferences: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DesignKnowledgeResponse:
    status: AgentStatus
    query: dict[str, Any]
    applicable_items: list[dict[str, Any]]
    applicable_patterns: list[dict[str, Any]]
    normative_references: list[dict[str, Any]]
    scale_relations: list[dict[str, Any]]
    conflicts: list[dict[str, Any]]
    assumptions: list[str]
    missing_inputs: list[str]
    suggested_questions: list[str]
    rationale: list[str]
    source_ids: list[str]
    evidence_ids: list[str]
    confidence: str
    review_state: str
    decision_created: bool = False


def _scopes(*values: str) -> list[SpatialScope]:
    return [SpatialScope(value) for value in values]


SOURCES: tuple[DesignKnowledgeSource, ...] = (
    DesignKnowledgeSource("BOOK-ALEXANDER-TIMELESS-WAY", "The Timeless Way of Building", ["Christopher Alexander"], SourceClass.THEORETICAL, "BOOK", "en", 1979, "Oxford University Press", edition_or_version="Hardcover; ISBN 9780195024029", isbn_or_legal_id="9780195024029", url="https://global.oup.com/academic/product/the-timeless-way-of-building-9780195024029", license_status=LicenseStatus.LICENSE_REVIEW_REQUIRED, bibliographic_reference="Alexander (1979), The Timeless Way of Building. Metadata verified; page-count discrepancy preserved.", review_status=ReviewStatus.BIBLIOGRAPHICALLY_VERIFIED),
    DesignKnowledgeSource("BOOK-ALEXANDER-PATTERN-LANGUAGE", "A Pattern Language: Towns, Buildings, Construction", ["Christopher Alexander", "Sara Ishikawa", "Murray Silverstein", "Max Jacobson", "Ingrid Fiksdahl-King", "Shlomo Angel"], SourceClass.THEORETICAL, "BOOK", "en", 1977, "Oxford University Press", edition_or_version="1st edition; ISBN 9780195019193", isbn_or_legal_id="9780195019193", url="https://global.oup.com/academic/product/a-pattern-language-9780195019193", license_status=LicenseStatus.LICENSE_REVIEW_REQUIRED, bibliographic_reference="Alexander et al. (1977), A Pattern Language. Metadata verified; pagination is edition/record-dependent.", review_status=ReviewStatus.BIBLIOGRAPHICALLY_VERIFIED),
    DesignKnowledgeSource("BOOK-ALEXANDER-OREGON-EXPERIMENT", "The Oregon Experiment", ["Christopher Alexander", "Murray Silverstein", "Shlomo Angel", "Sara Ishikawa", "Denny Abrams"], SourceClass.THEORETICAL, "BOOK", "en", 1975, "Oxford University Press", edition_or_version="ISBN 9780195018240", isbn_or_legal_id="9780195018240", url="https://global.oup.com/academic/product/the-oregon-experiment-9780195018240", license_status=LicenseStatus.LICENSE_REVIEW_REQUIRED, bibliographic_reference="Alexander et al. (1975), The Oregon Experiment. Metadata verified; author and extent records vary.", review_status=ReviewStatus.BIBLIOGRAPHICALLY_VERIFIED),
    DesignKnowledgeSource("CASE-PREVI-LIMA-LAND", "The Experimental Housing Project (PREVI), Lima", ["Peter Land"], SourceClass.PRECEDENT, "CASE_STUDY", "en/es", 2015, "Ediciones Uniandes / Universidad de los Andes Colombia", edition_or_version="ISBN 9789587741629", isbn_or_legal_id="9789587741629", url="https://ediciones.uniandes.edu.co/gpd-el-proyecto-experimental-de-vivienda-previ-lima-diseno-y-tecnologia-en-un-nuevo-barrio-9789587741629-68097adf34ad6.html", license_status=LicenseStatus.LICENSE_REVIEW_REQUIRED, bibliographic_reference="Land (2015), The Experimental Housing Project (PREVI), Lima. Metadata verified; content rights remain unresolved.", review_status=ReviewStatus.BIBLIOGRAPHICALLY_VERIFIED),
    DesignKnowledgeSource("CASE-HOUSES-GENERATED-BY-PATTERNS", "Houses Generated by Patterns", ["Christopher Alexander", "Sanford Hirshen", "Sara Ishikawa", "Christie Coffin", "Shlomo Angel"], SourceClass.PRECEDENT, "CASE_STUDY", "en", 1969, "Center for Environmental Structure", edition_or_version="OCLC 977860341", isbn_or_legal_id="OCLC 977860341", url="https://christopher-alexander-ces-archive.org/book/houses-generated-by-patterns/", license_status=LicenseStatus.LICENSE_REVIEW_REQUIRED, bibliographic_reference="Alexander et al. (1969), Houses Generated by Patterns. Metadata verified; pagination and rights remain unresolved.", review_status=ReviewStatus.BIBLIOGRAPHICALLY_VERIFIED),
    DesignKnowledgeSource("BOOK-CHING-FORM-SPACE-ORDER", "Architecture: Form, Space, and Order", ["Francis D. K. Ching"], SourceClass.THEORETICAL, "BOOK", "en", 2014, "Wiley", edition_or_version="4th edition", license_status=LicenseStatus.NO_REPRODUCTION, bibliographic_reference="Ching (2014), Architecture: Form, Space, and Order."),
    DesignKnowledgeSource("RNE-CORPUS-RFC025", "Reglamento Nacional de Edificaciones — controlled corpus", ["Ministerio de Vivienda, Construcción y Saneamiento"], SourceClass.LEGAL_REGULATORY, "CORPUS", "es", 2026, "MVCS", jurisdiction="PE", license_status=LicenseStatus.UNKNOWN, bibliographic_reference="RFC-025 controlled RNE corpus", review_status=ReviewStatus.UNDER_REVIEW),
)


def _apl_scopes(number: int) -> list[SpatialScope]:
    if number <= 94:
        return _scopes("pais", "macro_region", "region", "provincia_metropoli", "distrito_ciudad", "zona_barrio_sector")
    if number <= 204:
        return _scopes("parcela_sitio", "edificacion", "sistema", "espacio")
    return _scopes("edificacion", "sistema", "espacio", "objeto")


def _apl_items() -> tuple[DesignKnowledgeItem, ...]:
    return tuple(
        DesignKnowledgeItem(
            knowledge_item_id=f"ITEM-APL-{number:03d}",
            source_id="BOOK-ALEXANDER-PATTERN-LANGUAGE",
            item_type=KnowledgeItemType.PATTERN_REFERENCE,
            title=title,
            statement=f"Registro metadata-only del patrón APL {number}: {title}. La descripción estructurada de SiMS-DeI queda pendiente de evidencia y revisión de fuente.",
            epistemic_status="SOURCE_METADATA_ONLY",
            authority_level=AuthorityLevel.THEORETICAL,
            applicable_scales=_apl_scopes(number),
            outputs=["design_question"],
            citation_locator=f"APL pattern {number}; public index locator: {APL253_SOURCE_LOCATOR}#pattern-{number}",
            review_status=ReviewStatus.UNDER_REVIEW,
            limitations=[
                "No se ingirió ni reprodujo texto protegido.",
                "El nombre y número provienen de un índice público secundario; requiere verificación bibliográfica independiente.",
                "No constituye requisito, restricción, recomendación ni decisión.",
            ],
            conditions={
                "apl_number": number,
                "canonical_label": title,
                "source_provenance": "SOURCE_METADATA",
                "source_commit": APL253_SOURCE_COMMIT,
                "rights_status": LicenseStatus.LICENSE_REVIEW_REQUIRED.value,
                "verification_status": "PARTIALLY_VERIFIED",
                "p3_applicability": "REQUIRES_EVIDENCE",
                "p6_applicability": "REQUIRES_EVIDENCE",
                "p8_applicability": "REQUIRES_EVIDENCE",
                "relationship_source": "SOURCE_DERIVED",
                "relationship_locator": APL253_RELATION_SOURCE,
            },
            related_item_ids=[f"ITEM-APL-{related:03d}" for related in related_numbers],
        )
        for number, title, related_numbers in APL253_RECORDS
    )

ITEMS: tuple[DesignKnowledgeItem, ...] = (
    DesignKnowledgeItem("ITEM-ALEXANDER-TIMELESS-PATTERN-RELATION-001", "BOOK-ALEXANDER-TIMELESS-WAY", KnowledgeItemType.DESIGN_PRINCIPLE, "Relación entre patrón y proceso de diseño", "La fuente se registra como una referencia teórica para explorar relaciones entre patrones, proceso y forma construida; este piloto conserva la afirmación como orientación interpretativa y no como regla universal.", "THEORY", AuthorityLevel.THEORETICAL, _scopes("edificacion", "espacio", "objeto"), outputs=["design_question", "process_direction"], criteria=["traceable_exploration"], citation_locator="Bibliographic metadata only; content locator pending", review_status=ReviewStatus.UNDER_REVIEW, limitations=["No se extrajo texto de la obra.", "No constituye doctrina ni requisito." ], related_item_ids=["ITEM-ALEXANDER-PUBLIC-PRIVATE-001", "ITEM-OREGON-PROCESS-CASE-001"]),
    DesignKnowledgeItem("ITEM-CHING-SPATIAL-HIERARCHY-001", "BOOK-CHING-FORM-SPACE-ORDER", KnowledgeItemType.DESIGN_PRINCIPLE, "Jerarquía espacial", "La jerarquía espacial puede expresarse mediante diferencias de posición, escala, luz, forma o accesibilidad.", "THEORY", AuthorityLevel.THEORETICAL, _scopes("distrito_ciudad", "zona_barrio_sector", "edificacion", "espacio", "objeto"), criteria=["spatial_legibility", "wayfinding"], outputs=["hierarchy_strategy"], citation_locator="Conceptual extraction; page locator pending", limitations=["No es una exigencia normativa."]),
    DesignKnowledgeItem("ITEM-CHING-SPATIAL-SEQUENCE-001", "BOOK-CHING-FORM-SPACE-ORDER", KnowledgeItemType.SPATIAL_RELATION, "Secuencia espacial", "La sucesión de espacios y umbrales puede organizar percepción, orientación y movimiento.", "THEORY", AuthorityLevel.THEORETICAL, _scopes("zona_barrio_sector", "edificacion", "espacio"), criteria=["sequence_legibility", "orientation"], outputs=["movement_sequence"], limitations=["Debe adaptarse a accesibilidad y programa."]),
    DesignKnowledgeItem("ITEM-ALEXANDER-PUBLIC-PRIVATE-001", "BOOK-ALEXANDER-PATTERN-LANGUAGE", KnowledgeItemType.PATTERN_REFERENCE, "Gradiente público-privado", "Una transición gradual puede mediar entre espacios públicos y privados cuando existen necesidades diferenciadas de acceso, privacidad y seguridad.", "HEURISTIC", AuthorityLevel.THEORETICAL, _scopes("distrito_ciudad", "zona_barrio_sector", "edificacion", "espacio"), inputs=["access_points", "user_groups", "public_private_program"], outputs=["access_hierarchy", "transition_sequence"], criteria=["privacy", "legibility", "social_activation"], limitations=["No es universal ni sustituye normativa de seguridad o accesibilidad."], related_item_ids=["ITEM-ALEXANDER-TIMELESS-PATTERN-RELATION-001", "ITEM-PREVI-EXPERIMENTAL-HOUSING-CASE-001"]),
    DesignKnowledgeItem("ITEM-OREGON-PROCESS-CASE-001", "BOOK-ALEXANDER-OREGON-EXPERIMENT", KnowledgeItemType.METHOD, "Proceso y relaciones de campus", "La fuente se conserva como referencia de un proceso de planificación y organización espacial aplicado al campus de la Universidad de Oregon; puede formular preguntas de proceso, pero no prescribe una solución.", "PRECEDENT_CONTEXT", AuthorityLevel.THEORETICAL, _scopes("zona_barrio_sector", "distrito_ciudad", "edificacion"), outputs=["process_question", "relationship_question"], criteria=["phasing", "spatial_relationships"], citation_locator="Bibliographic and institutional metadata; content locator pending", review_status=ReviewStatus.UNDER_REVIEW, limitations=["No se extrae ni se reproduce el contenido del libro.", "La aplicabilidad al proyecto debe ser confirmada por el arquitecto."], related_item_ids=["ITEM-ALEXANDER-TIMELESS-PATTERN-RELATION-001", "ITEM-HOUSES-PATTERNS-PROCESS-001"]),
    DesignKnowledgeItem("ITEM-PREVI-EXPERIMENTAL-HOUSING-CASE-001", "CASE-PREVI-LIMA-LAND", KnowledgeItemType.PRECEDENT, "PREVI como caso experimental de vivienda", "PREVI se registra como un caso documentado de vivienda experimental en Lima que puede aportar preguntas comparativas sobre organización de masas, espacios comunes y relación entre proceso y aplicación.", "CASE_METADATA", AuthorityLevel.EXPERIENTIAL, _scopes("parcela_sitio", "edificacion", "espacio"), outputs=["case_comparison", "open_space_question", "common_space_question"], criteria=["site_openness", "common_space", "spatial_relationships"], citation_locator="Publisher metadata; no plan or image extracted", review_status=ReviewStatus.UNDER_REVIEW, limitations=["No se afirma que una característica concreta de PREVI derive de un patrón específico.", "El caso no es una norma ni una solución transferible automáticamente."], related_item_ids=["ITEM-ALEXANDER-PUBLIC-PRIVATE-001", "ITEM-HOUSES-PATTERNS-PROCESS-001"]),
    DesignKnowledgeItem("ITEM-HOUSES-PATTERNS-PROCESS-001", "CASE-HOUSES-GENERATED-BY-PATTERNS", KnowledgeItemType.PRECEDENT, "Proceso experimental de vivienda y patrones", "La fuente se registra como un caso histórico de proceso experimental de vivienda asociado a patrones; puede apoyar una pregunta de exploración sobre cómo una relación espacial se traduce en una alternativa visible.", "CASE_METADATA", AuthorityLevel.EXPERIENTIAL, _scopes("parcela_sitio", "edificacion", "espacio"), outputs=["design_process_question", "alternative_comparison"], criteria=["mass_organization", "transition", "spatial_hierarchy"], citation_locator="CES archive metadata; no PDF or image extracted", review_status=ReviewStatus.UNDER_REVIEW, limitations=["La fuente no se ingirió y el enlace público no se trató como permiso de copia.", "No se presenta como evidencia de desempeño real."], related_item_ids=["ITEM-OREGON-PROCESS-CASE-001", "ITEM-PREVI-EXPERIMENTAL-HOUSING-CASE-001"]),
) + _apl_items()

PATTERNS: tuple[DesignPattern, ...] = (
    DesignPattern("PATTERN-PUBLIC-PRIVATE-GRADIENT-001", ["BOOK-ALEXANDER-PATTERN-LANGUAGE"], "Gradiente público-privado", {"title": "Transición abrupta entre ámbitos", "question": "¿Cómo se gradúa el acceso?"}, ["usos públicos y privados", "necesidad de control gradual"], ["seguridad", "orientación", "privacidad", "interacción social"], {"steps": ["introducir espacios intermedios", "graduar visibilidad", "organizar secuencias de acceso"]}, {"positive": ["mejor legibilidad", "privacidad graduada"], "negative": ["mayor complejidad de circulación"]}, _scopes("distrito_ciudad", "zona_barrio_sector", "edificacion", "espacio"), inputs=["access_points", "user_groups", "public_private_program"], outputs=["access_hierarchy", "transition_sequence"], positive_indicators=["privacy", "legibility"], negative_indicators=["barriers", "inaccessibility"], regulatory_dependencies=["accessibility", "fire_safety"]),
)


def _serialize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    return value


def source_to_dict(source: DesignKnowledgeSource) -> dict[str, Any]:
    return _serialize(asdict(source))


def item_to_dict(item: DesignKnowledgeItem) -> dict[str, Any]:
    return _serialize(asdict(item))


def pattern_to_dict(pattern: DesignPattern) -> dict[str, Any]:
    return _serialize(asdict(pattern))


def list_sources(source_class: str | None = None) -> list[dict[str, Any]]:
    values = SOURCES if source_class is None else tuple(item for item in SOURCES if item.source_class.value == source_class.upper())
    return [source_to_dict(item) for item in values]


def list_items(scope: SpatialScope | None = None, typology: str | None = None) -> list[dict[str, Any]]:
    values: Iterable[DesignKnowledgeItem] = ITEMS
    if scope is not None:
        values = (item for item in values if scope in item.applicable_scales and scope not in item.excluded_scales)
    if typology:
        values = (item for item in values if not item.applicable_typologies or typology in item.applicable_typologies)
    return [item_to_dict(item) for item in values]


def list_patterns(scope: SpatialScope | None = None, typology: str | None = None) -> list[dict[str, Any]]:
    values: Iterable[DesignPattern] = PATTERNS
    if scope is not None:
        values = (item for item in values if scope in item.applicable_scales)
    if typology:
        values = (item for item in values if not item.applicable_typologies or typology in item.applicable_typologies)
    return [pattern_to_dict(item) for item in values]


class DesignKnowledgeAgent:
    """Retrieves design knowledge while preserving normative boundaries."""

    name = "DESIGN_KNOWLEDGE"

    def __init__(self, regulations: Iterable[dict[str, Any]] | None = None) -> None:
        self.regulations = list(regulations or [])

    def query(self, request: DesignKnowledgeQuery) -> DesignKnowledgeResponse:
        if request.spatial_scope is None and not request.problem_terms and not request.objectives:
            return DesignKnowledgeResponse(AgentStatus.INSUFFICIENT_CONTEXT, asdict(request), [], [], [], [], [], [], ["spatial_scope or problem_terms or objectives"], ["¿Cuál es la escala principal y el problema de diseño?"], [], [], [], "UNKNOWN", "REVIEW_REQUIRED")
        items = list_items(request.spatial_scope, request.typology)
        patterns = list_patterns(request.spatial_scope, request.typology)
        terms = {term.lower() for term in request.problem_terms + request.objectives}
        if terms:
            items = [item for item in items if not terms or any(term in (item["title"] + " " + item["statement"]).lower() for term in terms)] or items
            patterns = [pattern for pattern in patterns if not terms or any(term in (pattern["name"] + " " + str(pattern["problem"])).lower() for term in terms)] or patterns
        conflicts: list[dict[str, Any]] = []
        normative = []
        for regulation in self.regulations:
            status = str(regulation.get("status", "NO_VERIFICADA"))
            normative.append({"regulation": regulation, "use": "reference_only" if status != "VIGENTE" else "candidate_requirement", "automatic_promotion": False})
            if status in {"NO_VERIFICADA", "MODIFICADA", "DEROGADA"}:
                conflicts.append({"type": "NORMATIVE_STATUS", "code": regulation.get("code"), "status": status, "message": "La norma requiere revisión de vigencia y aplicabilidad humana."})
        questions = ["¿Qué requisitos normativos tienen aplicabilidad confirmada?", "¿Qué supuestos deben convertirse en datos observados?"]
        if request.typology is None:
            questions.append("¿Qué tipología de intervención se está diseñando?")
        status = AgentStatus.CONFLICTING if conflicts else AgentStatus.REVIEW_REQUIRED
        source_ids = sorted({item["source_id"] for item in items} | {source_id for pattern in patterns for source_id in pattern["source_ids"]})
        return DesignKnowledgeResponse(status, asdict(request), items, patterns, normative, [], conflicts, list(request.assumptions), [], questions, ["Se recuperó conocimiento por escala y se mantuvo separada la capa normativa.", "Los patrones son orientación teórica; no crean restricciones ni decisiones."], source_ids, [], "MEDIUM", "HUMAN_REVIEW_REQUIRED")


__all__ = ["SourceClass", "ReviewStatus", "LicenseStatus", "KnowledgeItemType", "AuthorityLevel", "AgentStatus", "DesignKnowledgeSource", "DesignKnowledgeItem", "DesignPattern", "DesignKnowledgeQuery", "DesignKnowledgeResponse", "DesignKnowledgeAgent", "source_to_dict", "item_to_dict", "pattern_to_dict", "list_sources", "list_items", "list_patterns"]
