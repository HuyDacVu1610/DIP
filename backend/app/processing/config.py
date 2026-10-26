"""Full immutable page config and presets; no image mutation, HTTP or DB."""

from collections.abc import Mapping
from numbers import Integral
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, ValidationError, ValidationInfo
from pydantic import field_validator, model_validator

from .geometry import MAX_WARP_LONG_EDGE, validate_quad

Mode = Literal['color', 'gray', 'bw']
Coordinate = Annotated[float, Field(strict=True, allow_inf_nan=False, ge=0, le=1)]
Point = tuple[Coordinate, Coordinate]
Corners = tuple[Point, Point, Point, Point]


class ConfigValidationError(ValueError):
    """One stable config reason code; HTTP mapping belongs to a future route."""

    code = 'INVALID_CONFIG'


class _ConfigModel(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, validate_default=True, revalidate_instances='always')


class DenoiseConfig(_ConfigModel):
    method: Literal['none', 'median', 'gaussian'] = 'none'
    kernel: StrictInt = Field(default=3, ge=3, le=5)

    @field_validator('kernel')
    @classmethod
    def odd_kernel(cls, value: int) -> int:
        if value % 2 == 0:
            raise ValueError('Kernel phải là 3 hoặc 5.')
        return value


class ContrastConfig(_ConfigModel):
    method: Literal['none', 'clahe'] = 'none'
    clip_limit: Annotated[float, Field(strict=True, allow_inf_nan=False, ge=1, le=4)] = 2.0
    tile_grid: tuple[StrictInt, StrictInt] = (8, 8)

    @field_validator('tile_grid')
    @classmethod
    def fixed_grid(cls, value: tuple[int, int]) -> tuple[int, int]:
        if value != (8, 8):
            raise ValueError('MVP dùng tile_grid cố định [8,8].')
        return value


class ThresholdConfig(_ConfigModel):
    method: Literal['otsu', 'adaptive_gaussian'] = 'adaptive_gaussian'
    block_size: StrictInt = Field(default=31, ge=3, le=151)
    c: StrictInt = Field(default=10, ge=-20, le=30)

    @field_validator('block_size')
    @classmethod
    def odd_block(cls, value: int) -> int:
        if value % 2 == 0:
            raise ValueError('Block size phải là số nguyên lẻ.')
        return value


class GeometryConfig(_ConfigModel):
    aspect_policy: Literal['estimated'] = 'estimated'
    max_long_edge: StrictInt = Field(default=MAX_WARP_LONG_EDGE, ge=MAX_WARP_LONG_EDGE, le=MAX_WARP_LONG_EDGE)


def _preset_data(mode: Mode) -> dict[str, Any]:
    return {'mode':mode, 'corners':None, 'confirmed':False, 'rotation':0,
            'denoise':{'method':'median' if mode == 'bw' else 'none', 'kernel':3},
            'contrast':{'method':'clahe' if mode == 'gray' else 'none', 'clip_limit':2.0, 'tile_grid':[8,8]},
            'threshold':{'method':'adaptive_gaussian', 'block_size':31, 'c':10},
            'geometry':{'aspect_policy':'estimated', 'max_long_edge':MAX_WARP_LONG_EDGE}}


def _dimensions(size: object, *, warp: bool = False) -> tuple[int, int]:
    if not isinstance(size, (tuple, list)) or len(size) != 2:
        raise ValueError('Dimensions phải là cặp (width,height).')
    if any(isinstance(d, bool) or not isinstance(d, Integral) or d < 2 for d in size):
        raise ValueError('Dimensions phải là hai số nguyên từ 2 pixel.')
    if warp and max(size) > MAX_WARP_LONG_EDGE:
        raise ValueError('Dimensions warp vượt giới hạn 2400.')
    return int(size[0]), int(size[1])


class PageConfig(_ConfigModel):
    """Use parse_config with source_size for corners and warp_size before filters.

    Missing fields use the requested mode's preset, including nested fields;
    explicit null/unknown/bad values are errors. Never merge an old config.
    Snapshots are frozen, with tuple corners/grid; export via model_dump(json).
    """

    mode: Mode = 'color'
    corners: Corners | None = None
    confirmed: StrictBool = False
    rotation: StrictInt = Field(default=0, ge=0, le=270)
    denoise: DenoiseConfig = Field(default_factory=DenoiseConfig)
    contrast: ContrastConfig = Field(default_factory=ContrastConfig)
    threshold: ThresholdConfig = Field(default_factory=ThresholdConfig)
    geometry: GeometryConfig = Field(default_factory=GeometryConfig)

    @model_validator(mode='before')
    @classmethod
    def mode_defaults(cls, value: Any) -> Any:
        if not isinstance(value, Mapping):
            return value
        mode = value.get('mode', 'color')
        if not isinstance(mode, str) or mode not in ('color', 'gray', 'bw'):
            return value
        result = _preset_data(mode)
        for name, supplied in value.items():
            if isinstance(result.get(name), dict) and isinstance(supplied, Mapping):
                result[name] = result[name] | dict(supplied)
            else:
                result[name] = supplied
        return result

    @field_validator('rotation')
    @classmethod
    def right_angle_rotation(cls, value: int) -> int:
        if value % 90:
            raise ValueError('Rotation chỉ nhận 0/90/180/270 độ theo chiều kim đồng hồ.')
        return value

    @model_validator(mode='after')
    def geometry_and_size(self, info: ValidationInfo) -> Self:
        context = info.context or {}
        if self.confirmed and self.corners is None:
            raise ValueError('Confirmed=true cần đủ bốn góc hợp lệ.')
        if self.corners is not None:
            if context.get('source_size') is None:
                raise ValueError('Cần dimensions nguồn sau EXIF để kiểm tra góc.')
            validate_quad(self.corners, *_dimensions(context['source_size']))
        if context.get('warp_size') is not None:
            width, height = _dimensions(context['warp_size'], warp=True)
            if self.mode == 'bw' and self.threshold.method == 'adaptive_gaussian' and self.threshold.block_size > min(width, height):
                raise ValueError('Block Adaptive lớn hơn cạnh ngắn của warp; chọn block nhỏ hoặc Otsu.')
        return self

    @property
    def inactive_fields(self) -> tuple[str, ...]:
        """Dotted field names, determined by mode/method, not confirmation state."""
        fields = []
        if self.denoise.method == 'none':
            fields.append('denoise.kernel')
        if self.mode == 'color':
            fields.extend(['contrast.method', 'contrast.clip_limit', 'contrast.tile_grid'])
        elif self.contrast.method == 'none':
            fields.extend(['contrast.clip_limit', 'contrast.tile_grid'])
        if self.mode != 'bw':
            fields.extend(['threshold.method', 'threshold.block_size', 'threshold.c'])
        elif self.threshold.method == 'otsu':
            fields.extend(['threshold.block_size', 'threshold.c'])
        return tuple(fields)


def parse_config(data: object, *, source_size: tuple[int, int] | None = None,
                 warp_size: tuple[int, int] | None = None) -> PageConfig:
    """Validate full/partial input without mutating it; return a frozen snapshot.

    source_size is required for any non-null corners (even an unconfirmed
    config); warp_size enables active Adaptive fit checks. Unknown fields,
    nulls, bool/string-as-number and basic invalid inactive values are errors.
    No image rendering or source access. Revalidates PageConfig instances too.
    """
    try:
        return PageConfig.model_validate(data, context={'source_size':source_size, 'warp_size':warp_size})
    except ValidationError as error:
        first = error.errors(include_url=False, include_input=False, include_context=False)[0]
        location = '.'.join(map(str, first['loc'])) or 'config'
        raise ConfigValidationError(f"Cấu hình không hợp lệ tại {location}: {first['msg']}") from error


def get_preset(mode: Mode = 'color') -> PageConfig:
    """Return a new full draft config; presets never confirm corners."""
    return parse_config({'mode':mode})
