# flowcell_manifold/part2.py

# === Standard Libraries ===
from dataclasses import dataclass  # structured data containers
from pathlib import Path  # for managing file paths and export locations

# === Core Libraries ===
import build123d as bd  # Main b123d CAD kernel and modeling API
from build123d_ease import show  # helper to display CAD models in the viewer
from loguru import logger  # rich logging for CLI/debugging

# === Project Utilities (local modules) ===
from flowcell_manifold.utils.export import export_part
from flowcell_manifold.utils.viewer import (
    debug_show_locals,
    setup_viewer,
    viewer_running,
)


# === CAD spec ===
@dataclass
class Part2Spec:
    """Specification for part2: a rectangular plate with a central hole, bottom chamfers, and top fillets."""

    length: float = 80.0
    width: float = 60.0
    thickness: float = 10.0
    hole_diameter: float = 22.0
    chamfer_distance: float = 2.0
    fillet_radius: float = 5.0

    def __post_init__(self) -> None:
        assert self.length > 0, "length must be positive"
        assert self.width > 0, "width must be positive"
        assert self.thickness > 0, "thickness must be positive"
        assert 0 < self.hole_diameter < min(self.length, self.width), (
            "hole_diameter must be positive and smaller than plate dimensions"
        )
        assert self.chamfer_distance >= 0, (
            "chamfer_distance must be non-negative"
        )
        assert self.fillet_radius >= 0, "fillet_radius must be non-negative"


def make_part2(spec: Part2Spec) -> bd.Part | bd.Compound:
    """Create a CAD model of part2."""
    p = bd.Part(None)

    # 1. Base plate
    p += bd.Box(spec.length, spec.width, spec.thickness)

    # 2. Central through-hole
    p -= bd.Cylinder(radius=spec.hole_diameter / 2, height=spec.thickness)

    # 3. Chamfer bottom edges (edges at lowest Z)
    bottom_edges = p.edges().group_by(bd.Axis.Z)[0]
    if spec.chamfer_distance > 0 and bottom_edges:
        p = bd.chamfer(bottom_edges, length=spec.chamfer_distance)

    # 4. Fillet top edges (edges at highest Z)
    top_edges = p.edges().group_by(bd.Axis.Z)[-1]
    if spec.fillet_radius > 0 and top_edges:
        p = bd.fillet(top_edges, radius=spec.fillet_radius)

    return p


# === Script Entrypoint ===

if __name__ == "__main__":
    logger.info("Generating part2 geometry...")

    # Setup optional CAD viewer
    try:
        viewer_classes = setup_viewer()
    except Exception as e:
        logger.warning(f"Viewer setup failed: {e}")
        viewer_classes = ()

    # Build the part
    spec = Part2Spec()
    part2 = make_part2(spec)

    # Show in viewer if available
    if viewer_running():
        try:
            show(part2)
        except Exception as e:
            logger.error(f"Failed to show part in viewer: {e}")
    else:
        logger.info("Viewer not running — skipping live show.")

    # Export to build folder
    export_folder = Path(__file__).parent.parent / "build"
    export_folder.mkdir(exist_ok=True)
    export_part(part2, "part2", export_folder)

    # Optionally dump locals to viewer console
    try:
        debug_show_locals(viewer_classes)
    except Exception as e:
        logger.warning(f"debug_show_locals failed: {e}")
