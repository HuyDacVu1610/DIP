"""Detection derivatives of normalized source; never inputs for export rendering."""
from dataclasses import dataclass, field, replace
from hashlib import sha256
from math import atan2, ceil, dist, isfinite
from time import perf_counter_ns
from typing import Literal

import cv2
import numpy as np
from numpy.typing import NDArray

from ..settings import MAX_IMAGE_PIXELS
from .geometry import GeometryValidationError, Quad, normalized_to_pixel, order_auto_corners, pixel_to_normalized, validate_quad
from .image_sizes import resize_to_max_edge
from .polygon_metrics import polygon_iou

MAX_ANALYSIS_LONG_EDGE = 1200
CANNY_THRESHOLD_PAIRS = ((50,150), (75,200), (100,250))
REVISED_CANNY_THRESHOLD_PAIRS = ((20,60), (50,150), (75,200))
APPROX_EPSILON_RATIOS = (0.015,0.02,0.03)
MAX_CONTOURS_PER_TRIAL = 30
DETECTION_ALGORITHM_VERSION = 'detect-v1'


class DetectionValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class AnalysisImages:
    source_size: tuple[int, int]
    bgr: NDArray[np.uint8]
    gray: NDArray[np.uint8]
    blurred: NDArray[np.uint8]
    gaussian_kernel: int = 5

    @property
    def analysis_size(self) -> tuple[int, int]:
        return self.bgr.shape[1], self.bgr.shape[0]

    def to_source(self, point: tuple[float, float]) -> tuple[float, float]:
        """Map analysis pixel/subpixel through normalized using actual W-1/H-1."""
        normalized = pixel_to_normalized(point, *self.analysis_size)
        return normalized_to_pixel(normalized, *self.source_size)


@dataclass(frozen=True, slots=True)
class EdgeTrial:
    trial_id: str
    thresholds: tuple[int, int]
    edges: NDArray[np.uint8]
    closed: NDArray[np.uint8]
    gaussian_kernel: int = 5

    @property
    def method(self) -> str:
        return 'canny'


@dataclass(frozen=True, slots=True)
class RegionTrial:
    trial_id: str
    thresholds: tuple[int, int]  # raw Canny support thresholds, not segmentation t
    edges: NDArray[np.uint8]
    mask: NDArray[np.uint8]
    otsu_threshold: float
    support_trial_id: str
    gaussian_kernel: int = 5

    @property
    def method(self) -> str:
        return 'region_otsu'


@dataclass(frozen=True, slots=True)
class ContourCandidate:
    trial_id: str
    thresholds: tuple[int, int]
    analysis_size: tuple[int, int]
    source_size: tuple[int, int]
    contour_index: int
    contour_px: tuple[tuple[float, float], ...]
    epsilon_ratio: float | None
    polygon_px: tuple[tuple[float, float], ...]
    corners: Quad | None
    rejection_reason: str | None
    method: str = 'canny'
    gaussian_kernel: int = 5
    otsu_threshold: float | None = None
    support_trial_id: str | None = None  # region's raw Canny origin; Canny uses trial_id

    @property
    def polygon_vertex_count(self) -> int:
        return len(self.polygon_px)


@dataclass(frozen=True, slots=True)
class CandidateBatch:
    trial_id: str
    analysis_size: tuple[int, int]
    total_contours: int
    considered_contours: int
    attempts: tuple[ContourCandidate, ...]
    rejection_reason: str | None = None

    @property
    def candidates(self) -> tuple[ContourCandidate, ...]:
        return tuple(item for item in self.attempts if item.corners is not None)


@dataclass(frozen=True, slots=True)
class TrialCandidates:
    trial: EdgeTrial | RegionTrial
    batch: CandidateBatch


@dataclass(frozen=True, slots=True)
class CandidateDescription:
    candidate: ContourCandidate
    contour_perimeter_px: float
    polygon_vertex_count: int
    quad_edge_lengths_px: tuple[float, ...]
    quad_turn_angles_rad: tuple[float, ...]
    is_convex: bool
    self_intersects: bool
    area_ratio: float
    fit_area_ratio: float
    edge_sample_counts: tuple[int, ...]
    edge_supported_counts: tuple[int, ...]
    edge_support_per_side: tuple[float, ...]
    edge_support: float
    border_sample_count: int
    border_penalty: float
    heuristic_score: float


@dataclass(frozen=True, slots=True)
class DetectionTimings:
    preprocess: float
    candidates: float  # Canny/closing/contours and conditional Otsu, together
    describe: float
    select: float  # includes NMS
    debug: float
    total: float


@dataclass(frozen=True, slots=True)
class DetectionDebug:
    algorithm_version: str
    preset: str
    source_bgr_sha256: str  # C-order BGR bytes, not encoded PNG hash
    analysis: AnalysisImages
    trials: tuple[TrialCandidates, ...]
    selected_trial: EdgeTrial | RegionTrial | None
    overlay: NDArray[np.uint8]  # analysis coordinates, no resize or render
    overlay_kind: Literal['proposal', 'diagnostic', 'none']


@dataclass(frozen=True, slots=True)
class DetectionResult:
    status: Literal['proposed', 'proposed_with_warning', 'manual_required']
    corners: Quad | None
    heuristic_score: float | None
    warnings: tuple[str, ...]
    selected: CandidateDescription | None
    candidates: tuple[CandidateDescription, ...]  # score-ranked NMS survivors
    confirmed: bool = field(default=False, init=False)
    timings_ms: DetectionTimings | None = None  # select_proposal alone has no measured run
    debug: DetectionDebug | None = None


def prepare_analysis(source_bgr: NDArray[np.uint8], *, gaussian_kernel: int = 5) -> AnalysisImages:
    """Source BGR uint8 <=16 MP -> max-edge1200 -> gray -> explicit Gaussian.

    Preserve source and return independent stages. Resize is half-up/INTER_AREA,
    without upscaling; reject a resulting side <2 before geometry can divide by
    W-1/H-1. Gaussian5 remains default; 3 or 0 (disabled) are explicit ablations. Filters use
    sigma=0, reflect101; no EXIF/CLAHE/render filters here.
    """
    _validate_gaussian_kernel(gaussian_kernel)
    if (not isinstance(source_bgr, np.ndarray) or source_bgr.dtype != np.uint8
            or source_bgr.ndim != 3 or source_bgr.shape[2] != 3):
        raise DetectionValidationError('INVALID_SOURCE', 'Nguồn phân tích phải là BGR uint8, shape (H,W,3).')
    height, width = source_bgr.shape[:2]
    if min(width, height) < 2:
        raise DetectionValidationError('INVALID_SOURCE', 'Mỗi chiều nguồn phải từ 2 pixel.')
    if width * height > MAX_IMAGE_PIXELS:
        raise DetectionValidationError('TOO_MANY_PIXELS', 'Nguồn phân tích vượt giới hạn 16 triệu pixel.')
    try:
        bgr = resize_to_max_edge(source_bgr, MAX_ANALYSIS_LONG_EDGE)
        if min(bgr.shape[:2]) < 2:
            raise DetectionValidationError('ANALYSIS_TOO_SMALL', 'Ảnh phân tích có cạnh dưới 2 pixel sau thu nhỏ.')
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        blurred = (gray.copy() if gaussian_kernel == 0 else
            cv2.GaussianBlur(gray, (gaussian_kernel,gaussian_kernel), sigmaX=0, borderType=cv2.BORDER_REFLECT_101))
    except cv2.error as error:
        raise DetectionValidationError('ANALYSIS_FAILED', 'Không tạo được ảnh phân tích.') from error
    return AnalysisImages((width,height), bgr, gray, blurred,gaussian_kernel)


def create_edge_trials(blurred: NDArray[np.uint8], *, preset: str = 'baseline',
        gaussian_kernel: int = 5, closing: bool = True) -> tuple[EdgeTrial, ...]:
    """Three fixed Canny pairs, baseline or revised, then closing.

    Aperture3/L2gradient=True; white edges on black. Closing uses a rectangular
    3x3 kernel, once, with OpenCV's neutral constant morphology border. Keep
    raw edges separate for future edge-support scoring; closed is for contours.
    Explicit closing=False bypasses morphology for offline ablation only.
    No repeated blur, adaptive retries, contour selection, source/render edits.
    https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html
    https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html
    """
    _validate_gaussian_kernel(gaussian_kernel)
    if type(closing) is not bool or preset not in ('baseline','revised'):
        raise DetectionValidationError('INVALID_ANALYSIS_CONFIG', 'Preset phải baseline/revised và closing phải là bool.')
    if (not isinstance(blurred, np.ndarray) or blurred.dtype != np.uint8 or blurred.ndim != 2
            or min(blurred.shape) < 2 or max(blurred.shape) > MAX_ANALYSIS_LONG_EDGE):
        raise DetectionValidationError('INVALID_ANALYSIS', 'Canny cần ảnh xám phân tích uint8, mỗi chiều trong [2,1200].')
    kernel = np.ones((3,3), dtype=np.uint8)
    trials = []
    try:
        pairs = CANNY_THRESHOLD_PAIRS if preset == 'baseline' else REVISED_CANNY_THRESHOLD_PAIRS
        for low, high in pairs:
            edges = cv2.Canny(blurred, low, high, apertureSize=3, L2gradient=True)
            closed = (cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1, borderType=cv2.BORDER_CONSTANT)
                if closing else edges.copy())
            trials.append(EdgeTrial(_canny_trial_id((low,high),gaussian_kernel), (low,high), edges, closed,gaussian_kernel))
    except cv2.error as error:
        raise DetectionValidationError('EDGE_FAILED', 'Không tạo được Canny/closing từ ảnh phân tích.') from error
    return tuple(trials)


def _validate_gaussian_kernel(kernel: int) -> None:
    if type(kernel) is not int or kernel not in (0,3,5):
        raise DetectionValidationError('INVALID_ANALYSIS_CONFIG', 'Gaussian analysis nhận 3/5 hoặc 0 để tắt khi thí nghiệm.')


def _canny_trial_id(thresholds: tuple[int,int], gaussian_kernel: int) -> str:
    prefix = 'canny' if gaussian_kernel == 5 else f'canny_g{gaussian_kernel}'
    return f'{prefix}_{thresholds[0]}_{thresholds[1]}'


def _validate_trial(trial: EdgeTrial | RegionTrial) -> tuple[int, int]:
    if not isinstance(trial, (EdgeTrial,RegionTrial)) or trial.thresholds not in CANNY_THRESHOLD_PAIRS+REVISED_CANNY_THRESHOLD_PAIRS:
        raise DetectionValidationError('INVALID_TRIAL', 'Trial không thuộc bộ ngưỡng Canny đã chốt.')
    if type(trial.gaussian_kernel) is not int or trial.gaussian_kernel not in (0,3,5):
        raise DetectionValidationError('INVALID_TRIAL', 'Gaussian kernel của trial không hợp lệ.')
    support_id = _canny_trial_id(trial.thresholds,trial.gaussian_kernel)
    expected_id = support_id
    if isinstance(trial,RegionTrial):
        if (trial.support_trial_id != support_id or type(trial.otsu_threshold) not in (int,float)
                or not isfinite(trial.otsu_threshold) or not 0 <= trial.otsu_threshold <= 255):
            raise DetectionValidationError('INVALID_TRIAL', 'Nguồn raw Canny hoặc ngưỡng Otsu không hợp lệ.')
        expected_id = f'region_otsu_g{trial.gaussian_kernel}_{support_id}'
    if trial.trial_id != expected_id:
        raise DetectionValidationError('INVALID_TRIAL', 'ID trial không khớp cặp ngưỡng.')
    contour_image = trial.mask if isinstance(trial,RegionTrial) else trial.closed
    for image in (trial.edges,contour_image):
        if (not isinstance(image,np.ndarray) or image.dtype != np.uint8 or image.ndim != 2
                or min(image.shape) < 2 or max(image.shape) > MAX_ANALYSIS_LONG_EDGE
                or np.any((image != 0) & (image != 255))):
            raise DetectionValidationError('INVALID_TRIAL', 'Raw edge/contour map phải là ảnh nhị phân analysis uint8 hợp lệ.')
    if trial.edges.shape != contour_image.shape:
        raise DetectionValidationError('INVALID_TRIAL', 'Raw edges và contour map phải cùng kích thước.')
    return trial.edges.shape[1],trial.edges.shape[0]


def create_region_trial(analysis: AnalysisImages, support: EdgeTrial) -> RegionTrial:
    """Otsu bright-component mask from analysis blur; preserve actual raw evidence.

    No render threshold helper, large closing, hole filling, inverted-polarity
    retries or synthetic edges. RETR_EXTERNAL in candidate generation ignores
    internal holes without changing mask pixels. t and support origin are explicit.
    """
    if not isinstance(support,EdgeTrial):
        raise DetectionValidationError('INVALID_TRIAL', 'Region cần raw Canny support trial.')
    width,height = _validate_trial(support)
    if (not isinstance(analysis,AnalysisImages) or analysis.analysis_size != (width,height)
            or analysis.gaussian_kernel != support.gaussian_kernel or analysis.blurred.shape != support.edges.shape):
        raise DetectionValidationError('INVALID_ANALYSIS', 'Analysis không khớp kích thước/kernel của support trial.')
    try:
        # ponytail: bright regions may merge with bright desks; revisit with independent data, keep manual fallback.
        threshold,mask = cv2.threshold(analysis.blurred,0,255,cv2.THRESH_BINARY|cv2.THRESH_OTSU)
    except cv2.error as error:
        raise DetectionValidationError('REGION_FAILED', 'Không tạo được mask vùng sáng Otsu.') from error
    return RegionTrial(f'region_otsu_g{analysis.gaussian_kernel}_{support.trial_id}',support.thresholds,
        support.edges.copy(),mask,float(threshold),support.trial_id,analysis.gaussian_kernel)


def collect_candidates(analysis: AnalysisImages, *, preset: str = 'revised', closing: bool = True) -> tuple[TrialCandidates, ...]:
    """Current candidate entry: three Canny trials, then at most one region fallback.

    Baseline keeps the original three pairs and no region branch for comparison.
    Revised keeps Gaussian5 by default, substitutes 20/60 for 100/250; Otsu runs
    only if all Canny trials lack a valid quad. No NMS/proposal/confirmation here.
    """
    if not isinstance(analysis,AnalysisImages):
        raise DetectionValidationError('INVALID_ANALYSIS', 'Cần AnalysisImages từ nguồn chuẩn hóa.')
    edges = create_edge_trials(analysis.blurred,preset=preset,gaussian_kernel=analysis.gaussian_kernel,closing=closing)
    results = [TrialCandidates(trial,generate_candidates(analysis,trial)) for trial in edges]
    if preset == 'revised' and not any(result.batch.candidates for result in results):
        region = create_region_trial(analysis,edges[0])
        results.append(TrialCandidates(region,generate_candidates(analysis,region)))
    return tuple(results)


def generate_candidates(analysis: AnalysisImages, trial: EdgeTrial | RegionTrial) -> CandidateBatch:
    """Closed edges or external bright components -> bounded quad approximations.

    Keep original ordered contour/polygon, including rejected attempts. Check the
    polygon's existing cycle before canonical auto ordering: never repair crossing
    or concavity by sorting vertices. Normalized auto start uses original source
    pixels, while area/length gates and contour coordinates use analysis pixels.
    No right-angle gate, minAreaRect fallback, deduplication or proposal yet.
    https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html
    """
    width,height = _validate_trial(trial)
    if (not isinstance(analysis,AnalysisImages) or analysis.analysis_size != (width,height)
            or analysis.gaussian_kernel != trial.gaussian_kernel):
        raise DetectionValidationError('INVALID_ANALYSIS', 'Analysis dimensions/kernel không khớp trial.')
    is_region = isinstance(trial,RegionTrial)
    contour_image = trial.mask if is_region else trial.closed
    otsu_threshold = trial.otsu_threshold if is_region else None
    support_trial_id = trial.support_trial_id if is_region else None
    if is_region and (not contour_image.any() or np.all(contour_image == 255)):
        return CandidateBatch(trial.trial_id,(width,height),0,0,(),'UNIFORM_REGION_MASK')
    attempts = []
    try:
        contours,_ = cv2.findContours(contour_image,cv2.RETR_EXTERNAL if is_region else cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        ranked = sorted(enumerate(contours),key=lambda pair:(-cv2.contourArea(pair[1]),pair[0]))[:MAX_CONTOURS_PER_TRIAL]
        for index,contour in ranked:
            contour_px = tuple((float(x),float(y)) for x,y in contour.reshape(-1,2))
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour,True)
            if area < 0.10*width*height or perimeter <= 0:
                reason = 'CONTOUR_AREA_TOO_SMALL' if area < 0.10*width*height else 'DEGENERATE_CONTOUR'
                attempts.append(ContourCandidate(trial.trial_id,trial.thresholds,(width,height),analysis.source_size,
                    index,contour_px,None,(),None,reason,trial.method,trial.gaussian_kernel,otsu_threshold,support_trial_id))
                continue
            for ratio in APPROX_EPSILON_RATIOS:
                polygon = cv2.approxPolyDP(contour,ratio*perimeter,True).reshape(-1,2)
                polygon_px = tuple((float(x),float(y)) for x,y in polygon)
                corners,reason = None,None
                if len(polygon) != 4:
                    reason = 'NOT_QUADRILATERAL'
                else:
                    try:
                        normalized = tuple(pixel_to_normalized(p,width,height) for p in polygon_px)
                        # Reversing winding preserves topology; sorting before this gate would not.
                        if cv2.contourArea(polygon,oriented=True) < 0:
                            normalized = normalized[::-1]
                        pixels = validate_quad(normalized,width,height)
                        if cv2.contourArea(polygon) < 0.10*width*height:
                            reason = 'QUAD_AREA_TOO_SMALL'
                        elif any(dist(pixels[i],pixels[(i+1)%4]) < 0.05*min(width,height) for i in range(4)):
                            reason = 'QUAD_EDGE_TOO_SHORT'
                        else:
                            corners = order_auto_corners(normalized,*analysis.source_size)
                    except GeometryValidationError as error:
                        reason = error.code
                attempts.append(ContourCandidate(trial.trial_id,trial.thresholds,(width,height),analysis.source_size,
                    index,contour_px,ratio,polygon_px,corners,reason,trial.method,trial.gaussian_kernel,otsu_threshold,support_trial_id))
    except cv2.error as error:
        raise DetectionValidationError('CANDIDATES_FAILED', 'Không tạo được ứng viên contour/đa giác.') from error
    return CandidateBatch(trial.trial_id,(width,height),len(contours),len(ranked),tuple(attempts))


def _sample_edge_support(start: NDArray, end: NDArray, edges: NDArray[np.uint8]) -> tuple[int, int, int]:
    """Endpoints inclusive, spacing <=2px; Euclidean radius2 around each sample.

    Corners are counted on each incident side, consistently in all denominators.
    Query only the 25 nearby integer pixel centers, without dilating raw evidence.
    """
    samples = np.linspace(start,end,max(2,ceil(float(np.linalg.norm(end-start))/2)+1))
    centers = np.floor(samples+0.5).astype(np.int32)
    height,width = edges.shape
    supported = np.zeros(len(samples),dtype=bool)
    for dy in range(-2,3):
        for dx in range(-2,3):
            pixels = centers+(dx,dy)
            valid = ((pixels[:,0] >= 0) & (pixels[:,0] < width)
                & (pixels[:,1] >= 0) & (pixels[:,1] < height)
                & (np.sum((pixels-samples)**2,axis=1) <= 4))
            supported[valid] |= edges[pixels[valid,1],pixels[valid,0]] != 0
    border = np.min(np.column_stack((samples,width-1-samples[:,0],height-1-samples[:,1])),axis=1) <= 2
    return len(samples),int(supported.sum()),int(border.sum())


def describe_candidate(candidate: ContourCandidate, trial: EdgeTrial | RegionTrial) -> CandidateDescription:
    """Describe an accepted quad in analysis pixels, with same-trial raw Canny.

    Perimeter/lengths: px, signed turn angles: radians (x-right/y-down, positive
    convex cycle). e=sum(supported)/sum(samples), not mean(per-side ratios).
    a=Aquad/(W*H), f=min(Acontour,Aquad)/max(...), b=border samples/total.
    Score=clip(.45a+.35e+.20f-.15b,0,1) is a heuristic, never accuracy.
    Geometry is revalidated; no selection, NMS, confirmation or source rendering.
    """
    width,height = _validate_trial(trial)
    if (not isinstance(candidate,ContourCandidate) or candidate.corners is None
            or candidate.rejection_reason is not None or candidate.polygon_vertex_count != 4
            or candidate.analysis_size != (width,height) or candidate.trial_id != trial.trial_id
            or candidate.thresholds != trial.thresholds or candidate.method != trial.method
            or candidate.gaussian_kernel != trial.gaussian_kernel
            or candidate.otsu_threshold != (trial.otsu_threshold if isinstance(trial,RegionTrial) else None)
            or candidate.support_trial_id != (trial.support_trial_id if isinstance(trial,RegionTrial) else None)):
        raise DetectionValidationError('INVALID_CANDIDATE', 'Cần tứ giác hợp lệ và raw edge cùng trial/dimensions.')
    try:
        quad = np.array(validate_quad(candidate.corners,width,height),dtype=np.float64)
    except GeometryValidationError as error:
        raise DetectionValidationError('INVALID_CANDIDATE', 'Hình học ứng viên không hợp lệ.') from error
    contour = np.asarray(candidate.contour_px,dtype=np.float32)
    if (contour.ndim != 2 or contour.shape[1] != 2 or len(contour) < 3
            or not np.isfinite(contour).all() or (contour < 0).any()
            or (contour[:,0] > width-1).any() or (contour[:,1] > height-1).any()):
        raise DetectionValidationError('INVALID_CANDIDATE', 'Contour phải hữu hạn, có thứ tự, trong ảnh phân tích.')
    contour_area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour,True)
    if contour_area <= 0 or perimeter <= 0:
        raise DetectionValidationError('INVALID_CANDIDATE', 'Contour suy biến không có mô tả diện tích/chu vi hợp lệ.')
    quad_area = float(abs(np.dot(quad[:,0],np.roll(quad[:,1],-1))-np.dot(quad[:,1],np.roll(quad[:,0],-1)))/2)
    outgoing = np.roll(quad,-1,axis=0)-quad
    incoming = np.roll(outgoing,1,axis=0)
    lengths = tuple(float(np.linalg.norm(edge)) for edge in outgoing)
    turns = tuple(atan2(a[0]*b[1]-a[1]*b[0],float(np.dot(a,b))) for a,b in zip(incoming,outgoing))
    measured = tuple(_sample_edge_support(quad[i],quad[(i+1)%4],trial.edges) for i in range(4))
    counts = tuple(item[0] for item in measured)
    supported = tuple(item[1] for item in measured)
    border_count = sum(item[2] for item in measured)
    area_ratio = quad_area/(width*height)
    fit_ratio = min(contour_area,quad_area)/max(contour_area,quad_area)
    edge_support = sum(supported)/sum(counts)
    border_penalty = border_count/sum(counts)
    score = float(np.clip(.45*area_ratio+.35*edge_support+.20*fit_ratio-.15*border_penalty,0,1))
    # Shared validate_quad above established convexity and absence of intersections.
    return CandidateDescription(candidate,perimeter,4,lengths,turns,True,False,area_ratio,fit_ratio,
        counts,supported,tuple(m/n for m,n in zip(supported,counts)),edge_support,border_count,border_penalty,score)


def deduplicate_candidates(descriptions: tuple[CandidateDescription, ...]) -> tuple[CandidateDescription, ...]:
    """Greedy polygon NMS: suppress IoU >.95, highest score first, stable ties.

    All descriptions must come from the same source/analysis run. Dimensions
    cannot identify an image: the caller owns source identity. Keep each winning
    description intact, including its own method/kernel/Otsu/raw-edge evidence.
    """
    if not descriptions:
        return ()
    context = descriptions[0].candidate
    for item in descriptions:
        candidate = item.candidate
        if (type(item.heuristic_score) not in (int,float) or not isfinite(item.heuristic_score)
                or not 0 <= item.heuristic_score <= 1 or candidate.corners is None
                or candidate.rejection_reason is not None
                or candidate.source_size != context.source_size
                or candidate.analysis_size != context.analysis_size):
            raise DetectionValidationError('INVALID_CANDIDATE', 'Ứng viên/score hoặc hệ tọa độ NMS không hợp lệ.')
        try:
            validate_quad(candidate.corners, *candidate.analysis_size)
            validate_quad(candidate.corners, *candidate.source_size)
        except GeometryValidationError as error:
            raise DetectionValidationError('INVALID_CANDIDATE', 'Hình học ứng viên NMS không hợp lệ.') from error
    kept = []
    # ponytail: quadratic scan bounded by <=360 attempts/run; index only if that cap changes.
    try:
        for item in sorted(descriptions, key=lambda value: -value.heuristic_score):
            if not any(polygon_iou(item.candidate.corners, winner.candidate.corners,
                    *context.analysis_size) > .95 for winner in kept):
                kept.append(item)
    except GeometryValidationError as error:
        raise DetectionValidationError('NMS_FAILED', 'Không loại trùng được các tứ giác.') from error
    return tuple(kept)


def select_proposal(descriptions: tuple[CandidateDescription, ...]) -> DetectionResult:
    """NMS -> best score -> unconfirmed normalized proposal or manual_required.

    Keep a low-scored best candidate as diagnostic evidence only: result.corners
    stays null below .40. No candidates means a null score, not measured zero.
    These score thresholds do not certify that any polygon is the actual page.
    """
    candidates = deduplicate_candidates(descriptions)
    if not candidates:
        return DetectionResult('manual_required', None, None, ('NO_VALID_QUAD',), None, ())
    best = candidates[0]
    score = best.heuristic_score
    if score < .40:
        return DetectionResult('manual_required', None, score, ('LOW_HEURISTIC_SCORE',), best, candidates)
    if score < .60:
        return DetectionResult('proposed_with_warning', best.candidate.corners, score,
            ('LOW_HEURISTIC_SCORE',), best, candidates)
    return DetectionResult('proposed', best.candidate.corners, score, (), best, candidates)


def _build_detection_debug(source_bgr: NDArray[np.uint8], analysis: AnalysisImages,
        runs: tuple[TrialCandidates, ...], result: DetectionResult, preset: str) -> DetectionDebug:
    overlay = analysis.bgr.copy()
    trial, kind = None, 'none'
    if result.selected is not None:
        candidate = result.selected.candidate
        trial = next(run.trial for run in runs if run.trial.trial_id == candidate.trial_id)
        kind = 'proposal' if result.corners is not None else 'diagnostic'
        quad = np.array([normalized_to_pixel(p, *analysis.analysis_size) for p in candidate.corners])
        try:
            cv2.polylines(overlay, [np.rint(candidate.contour_px).astype(np.int32)], True, (255,120,0), 1)
            cv2.polylines(overlay, [np.rint(quad).astype(np.int32)], True, (0,0,255), 2)
            for index, point in enumerate(np.rint(quad).astype(int)):
                cv2.putText(overlay, str(index), tuple(point), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,255), 1)
        except cv2.error as error:
            raise DetectionValidationError('DEBUG_FAILED', 'Không tạo được contour overlay.') from error
    return DetectionDebug(DETECTION_ALGORITHM_VERSION, preset, sha256(source_bgr.tobytes(order='C')).hexdigest(),
        analysis, runs, trial, overlay, kind)


def detect_document(source_bgr: NDArray[np.uint8], *, debug: bool = False,
        preset: str = 'revised') -> DetectionResult:
    """Gaussian5 detector with measured timings; optional bounded debug stages.

    Source is normalized BGR uint8 after EXIF. Errors propagate separately from
    ordinary detection failure. Default revised; baseline is explicit for offline
    comparison. Timings exclude decode/encode/I/O, candidates groups Canny and
    contours, select includes NMS. Debug disabled retains no image stages/hash.
    """
    if type(debug) is not bool or preset not in ('baseline', 'revised'):
        raise DetectionValidationError('INVALID_ANALYSIS_CONFIG', 'debug phải là bool; preset baseline hoặc revised.')
    start = perf_counter_ns()
    analysis = prepare_analysis(source_bgr)
    preprocessed = perf_counter_ns()
    runs = collect_candidates(analysis, preset=preset)
    collected = perf_counter_ns()
    descriptions = tuple(describe_candidate(candidate, run.trial)
        for run in runs for candidate in run.batch.candidates)
    described = perf_counter_ns()
    result = select_proposal(descriptions)
    selected = perf_counter_ns()
    details = _build_detection_debug(source_bgr, analysis, runs, result, preset) if debug else None
    finished = perf_counter_ns() if debug else selected
    timings = DetectionTimings((preprocessed-start)/1e6, (collected-preprocessed)/1e6,
        (described-collected)/1e6, (selected-described)/1e6, (finished-selected)/1e6, (finished-start)/1e6)
    return replace(result, timings_ms=timings, debug=details)
