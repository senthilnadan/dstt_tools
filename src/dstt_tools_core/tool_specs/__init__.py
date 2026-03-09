from .math_specs import MATH_SPECS
from .route_specs import ROUTE_SPECS
from .reason_specs import REASON_SPECS
from .iterate_specs import ITERATE_SPECS
from .strategy_specs import STRATEGY_SPECS
from dstt_tools_core.tool_spec import ToolSpecRegistry

def populate_default_spec_registry(registry: ToolSpecRegistry):
    """Integrates all core DSTT tools standard specifications natively."""
    for spec_list in [MATH_SPECS, ROUTE_SPECS, REASON_SPECS, ITERATE_SPECS, STRATEGY_SPECS]:
        for spec in spec_list:
            registry.register(spec)
